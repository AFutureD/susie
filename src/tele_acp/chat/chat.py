import contextlib

from tele_acp.types import Channel, Chatable, ChatMessage, ChatMessageReplyable


class Chat(Chatable):
    def __init__(self, chat_id: str, channel: Channel, replier: ChatMessageReplyable):
        self.id = chat_id
        self.replier = replier
        self.channel = channel

    async def receive_message(self, message: ChatMessage):
        lifespan = message.lifespan or contextlib.nullcontext()

        async with lifespan:
            await self.replier.receive_message(self, message)

    async def send_message(self, message: ChatMessage):
        await self.channel.send_message(message)
