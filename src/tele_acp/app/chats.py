import asyncio
import contextlib
from abc import abstractmethod
from typing import AsyncIterator, Awaitable, Callable, Protocol

from tele_acp import types
import telethon
from pydantic.dataclasses import dataclass
from telethon.custom import Message

from tele_acp.telegram import TGClient
from tele_acp.types import AcpMessage, Config


def convert_acp_message_to_chat_message(message: AcpMessage) -> ChatMessage:
    return ChatMessage.Empty()


def convert_telegram_message_to_chat_message(message: Message) -> ChatMessage:
    return ChatMessage.Empty()


class AgentThread:
    def __init__(self):
        pass

    async def stop_and_send_message(self, message: str) -> AsyncIterator[AcpMessage]:
        yield AcpMessage(
            prompt=None,
            model=None,
            chunks=[],
            usage=None,
            stopReason=None,
        )


class Channel(Protocol):
    @abstractmethod
    @contextlib.asynccontextmanager
    async def run_until_finish(self):
        yield

    @abstractmethod
    async def send_message(self, message: ChatMessage): ...

    @abstractmethod
    async def receive_message(self, message: ChatMessage): ...


class TelegramChannel(Channel):
    def __init__(self, settings: types.TypeTelegramChannel, message_handler: Callable[[ChatMessage], Awaitable[None]]):
        tele_client = TGClient.create_as_login(None, None, settings)
        tele_client.add_event_handler(self._on_reveive_new_message_event, telethon.events.NewMessage())
        self._tele_client = tele_client
        self._message_handler = message_handler
        self.channel_id =

    @contextlib.asynccontextmanager
    async def run_until_finish(self):
        async with contextlib.AsyncExitStack() as stack:
            await stack.enter_async_context(self._tele_client)
            yield

    async def send_message(self, message: ChatMessage):
        await self._tele_client.send_message("me")
        pass

    async def receive_message(self, message: ChatMessage):
        await self._message_handler(message)

    async def _on_reveive_new_message_event(self, event: telethon.events.NewMessage.Event):
        chat_message = convert_telegram_message_to_chat_message(event.message)
        await self.receive_message(chat_message)


@dataclass
class ChatMessage:
    channel_id: str
    parts: list[str]

    @staticmethod
    def Empty() -> ChatMessage:
        return ChatMessage(channel_id="", parts=[])


class Chat:
    def __init__(self, channel: Channel, agent: AgentThread):
        self.agent_thread = agent
        self.channel = channel
        pass

    async def receive_message(self, message: ChatMessage):
        prompt = message.parts[0]

        iter = self.agent_thread.stop_and_send_message(prompt)
        async for delta in iter:
            msg = convert_acp_message_to_chat_message(delta)
            await self.send_message(msg)

        pass

    async def send_message(self, message: ChatMessage):
        await self.channel.send_message(message)


class ChatManager:
    def __init__(self, config: Config):
        self._config = config

        self._channels_lock = asyncio.Lock()
        self._channels: dict[str, Channel] = {}

    @contextlib.asynccontextmanager
    async def run_until_finish(self):
        async with contextlib.AsyncExitStack() as stack:
            async with self._channels_lock:
                for channel_settings in self._config.channels:
                    channel = TelegramChannel(channel_settings, self.receive_message)
                    await stack.enter_async_context(channel.run_until_finish())

                    self._channels[channel.channel_id] = channel

            yield

    def get_channel(self, channel_id: str) -> Channel | None:
        return self._channels.get(channel_id)

    async def send_message(self, message: ChatMessage):
        channel = self.get_channel(message.channel_id)
        if not channel:
            return
        await channel.send_message(message)

    async def receive_message(self, message: ChatMessage):
        channel_id = message.channel_id
        channel = self.get_channel(channel_id)
        assert channel is not None


        await channel.receive_message(message)
