import asyncio
import contextlib
from typing import AsyncIterator

from tele_acp.router import Router
from tele_acp.types import Channel, ChatMessage, Config

from .telegram import TelegramChannel


class ChannelHub:
    def __init__(self, config: Config, router: Router | None = None) -> None:
        self._config = config
        self._router = router

        self._channels_lock = asyncio.Lock()
        self._channels: dict[str, Channel] = {}

        for channel_settings in self._config.channels:
            channel = TelegramChannel(channel_settings, self._on_receive_new_message)
            self._channels[channel.id] = channel

    def set_router(self, router: Router) -> None:
        self._router = router

    def get_channel(self, channel_id: str) -> Channel | None:
        return self._channels.get(channel_id)

    @contextlib.asynccontextmanager
    async def run(self) -> AsyncIterator[ChannelHub]:
        async with contextlib.AsyncExitStack() as stack:
            async with self._channels_lock:
                for channel in self._channels.values():
                    await stack.enter_async_context(channel.run_until_finish())
            yield self

    async def _on_receive_new_message(self, message: ChatMessage) -> None:
        """Called when a new message is received from a channel."""
        assert self._router is not None

        await self._router.route(message)
