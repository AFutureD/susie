from __future__ import annotations

import asyncio
import contextlib
import logging
from collections.abc import Awaitable, Callable
from contextlib import AsyncExitStack
from dataclasses import dataclass
from typing import AsyncIterator

import telethon
from telethon import events
from telethon.custom import Message

from tele_acp.mcp import MCP
from tele_acp.telegram import TGClient
from tele_acp.types import Config, peer_hash_into_str
from tele_acp.types.channel import TelegramChannel


@dataclass(frozen=True, slots=True)
class InboundEnvelope:
    channel_id: str
    client: TGClient
    message: Message
    peer: telethon.types.TypePeer


@dataclass(frozen=True, slots=True)
class TelegramRuntime:
    channel: TelegramChannel
    client: TGClient


class TelegramManager:
    def __init__(
        self,
        config: Config,
        *,
        mcp_server: MCP,
        on_message: Callable[[InboundEnvelope], Awaitable[None]],
    ) -> None:
        self.logger = logging.getLogger(__name__)

        self._config = config
        self._mcp_server = mcp_server
        self._on_message = on_message

        self._run_lock = asyncio.Lock()
        self._has_started = False

        channels = [channel for channel in config.channel if isinstance(channel, TelegramChannel)]
        if not channels:
            raise ValueError("At least one Telegram channel is required.")

        if len(channels) > 1 and any(channel.session_name is None for channel in channels):
            raise ValueError("TelegramChannel.session_name must be set when multiple Telegram channels are configured.")

        self._runtimes: dict[str, TelegramRuntime] = {}
        for channel in channels:
            if channel.id in self._runtimes:
                raise ValueError(f"Duplicate Telegram channel id: {channel.id}")

            client = TGClient.create(session_name=channel.session_name, config=config)
            client.add_event_handler(self._build_message_handler(channel.id), events.NewMessage())

            self._mcp_server.set_tele_client(channel.id, client)
            self._runtimes[channel.id] = TelegramRuntime(channel=channel, client=client)

    @contextlib.asynccontextmanager
    async def run(self) -> AsyncIterator[None]:
        async with self._run_lock:
            if self._has_started:
                raise RuntimeError("TelegramManager has already started.")
            self._has_started = True

        async with AsyncExitStack() as stack:
            for runtime in self._runtimes.values():
                await stack.enter_async_context(runtime.client)

            self.logger.info("Started %s Telegram clients", len(self._runtimes))
            try:
                yield
            finally:
                self.logger.info("Finished")

    async def wait_until_disconnect(self) -> None:
        disconnect_tasks = [asyncio.ensure_future(runtime.client.disconnected) for runtime in self._runtimes.values()]
        if not disconnect_tasks:
            raise RuntimeError("No Telegram clients are configured.")

        try:
            done, pending = await asyncio.wait(disconnect_tasks, return_when=asyncio.FIRST_COMPLETED)
            for task in done:
                await task
            for task in pending:
                task.cancel()
            await asyncio.gather(*pending, return_exceptions=True)
        finally:
            for task in disconnect_tasks:
                if not task.done():
                    task.cancel()

    def _build_message_handler(self, channel_id: str):
        async def handler(event: events.NewMessage.Event) -> None:
            await self._handle_message(channel_id, event)

        return handler

    async def _handle_message(self, channel_id: str, event: events.NewMessage.Event) -> None:
        runtime = self._runtimes[channel_id]
        message: Message = event.message
        self.logger.info("New message received on channel %s: %s", channel_id, message)

        if message.out:
            return

        peer = message.peer_id
        if peer is None:
            return

        # Current dialog handling only supports direct user peers.
        if not isinstance(peer, telethon.types.PeerUser):
            return

        if not await self._is_allowed(runtime, peer):
            return

        await self._on_message(
            InboundEnvelope(
                channel_id=channel_id,
                client=runtime.client,
                message=message,
                peer=peer,
            )
        )

    async def _is_allowed(self, runtime: TelegramRuntime, peer: telethon.types.PeerUser) -> bool:
        whitelist = runtime.channel.whitelist or []
        if whitelist and self._peer_matches_whitelist(peer, whitelist):
            return True

        if not runtime.channel.allow_contacts:
            return False

        contacts = await runtime.client.get_contact_user_peer()
        return any(contact.user_id == peer.user_id for contact in contacts)

    def _peer_matches_whitelist(self, peer: telethon.types.TypePeer, whitelist: list[str]) -> bool:
        raw_id: str | None = None
        if isinstance(peer, telethon.types.PeerUser):
            raw_id = str(peer.user_id)
        elif isinstance(peer, telethon.types.PeerChat):
            raw_id = str(peer.chat_id)
        elif isinstance(peer, telethon.types.PeerChannel):
            raw_id = str(peer.channel_id)

        peer_hash = peer_hash_into_str(peer)
        return any(item in {peer_hash, raw_id} for item in whitelist if raw_id is not None)
