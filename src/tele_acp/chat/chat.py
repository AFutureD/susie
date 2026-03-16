import contextlib
import logging

from tele_acp.types import Channel, Chatable, ChatMessage, ChatMessageReplyable


class Chat(Chatable):
    def __init__(self, chat_id: str, channel: Channel, replier: ChatMessageReplyable):
        self.id = chat_id
        self.replier = replier
        self.channel = channel
        self.logger = logging.getLogger(__name__ + ":" + chat_id)

    async def receive_message(self, message: ChatMessage):
        if message.out:
            await self._handle_sent_message(message)
        else:
            await self._handle_new_message(message)

    async def send_message(self, message: ChatMessage):
        await self.channel.send_message(message)

    async def _handle_sent_message(self, message: ChatMessage):
        pass

    async def _handle_new_message(self, message: ChatMessage):
        lifespan = message.lifespan or contextlib.nullcontext()

        async with lifespan:
            await self.replier.receive_message(self, message)
