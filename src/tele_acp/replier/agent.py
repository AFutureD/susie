import logging
from typing import AsyncIterator

from tele_acp.acp import ACPAgentRuntime, AcpMessage
from tele_acp.types import AgentConfig, ChatMessage, ChatMessageReplyable
from tele_acp.types.chat import Chatable


def convert_acp_message_to_chat_message(channel_id: str, chat_id: str, message: AcpMessage) -> ChatMessage:
    text = message.markdown()
    parts = [text] if text else []

    return ChatMessage(id=None, channel_id=channel_id, chat_id=chat_id, parts=parts)


class AgentThread:
    def __init__(self, settings: AgentConfig, acp_runtime: ACPAgentRuntime):
        self.settings = settings
        self._acp_runtime = acp_runtime
        self.logger = logging.getLogger(__name__)

    async def stop_and_send_message(self, message: str) -> AsyncIterator[AcpMessage]:
        async for item in self._acp_runtime.prompt([message]):
            yield item


class ChatReplier(AgentThread, ChatMessageReplyable):
    async def receive_message(self, chat: Chatable, message: ChatMessage) -> None:
        if len(message.parts) == 0:
            return

        prompt = message.parts[0]
        self.logger.info(prompt)

        stream = self.stop_and_send_message(prompt)
        async for delta in stream:
            msg = convert_acp_message_to_chat_message(message.channel_id, message.chat_id, delta)
            await chat.send_message(msg)
