import contextlib
from typing import Any, Protocol

from pydantic import ConfigDict, Field
from pydantic.dataclasses import dataclass


@dataclass(config=ConfigDict(arbitrary_types_allowed=True))
class ChatMessage:
    """The Message in Chat"""

    id: str | None = Field(description="The identifier of the message in the chat")
    channel_id: str = Field(description="Which channel this message was sent from")
    chat_id: str = Field(description="Which chat this message wants to be sent to")
    parts: list[str] = Field(default_factory=list, description="The Message")
    lifespan: contextlib.AbstractAsyncContextManager | None = Field(default=None, exclude=True)
    meta: dict[str, Any] = Field(default_factory=dict, description="Metadata for the message")

    @staticmethod
    def Empty() -> ChatMessage:
        return ChatMessage(id=None, channel_id="", chat_id="", parts=[])


class Chatable(Protocol):
    async def receive_message(self, message: ChatMessage): ...
    async def send_message(self, message: ChatMessage): ...


class ChatMessageReplyable(Protocol):
    async def receive_message(self, chat: Chatable, message: ChatMessage) -> None: ...
