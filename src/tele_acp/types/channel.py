import enum

from pydantic import BaseModel, Field

from .agent import DEFAULT_AGENT_ID


class ChannelType(str, enum.Enum):
    TELEGRAM = "telegram"
    TELEGRAM_BOT = "telegram_bot"


class Channel(BaseModel):
    id: str


DEFAULT_TELEGRAM_ID = "default"


class TelegramChannel(Channel):
    id: str
    type: ChannelType = ChannelType.TELEGRAM
    session_name: str | None = Field(default=None, description="The session name for the Telegram client")
    allow_contacts: bool = Field(default=True, description="Whether to allow contacts")
    whitelist: list[str] | None = Field(default=[], description="The list of allowed users. peer id or group id")


class TelegramBotChannel(Channel):
    type: ChannelType = ChannelType.TELEGRAM_BOT
    token: str = Field(description="Telegram bot token")


class DialogBind(BaseModel):
    agent: str = Field(default=DEFAULT_AGENT_ID, description="The id of the `Agent`")
    channel: str = Field(default=DEFAULT_TELEGRAM_ID, description="The id of the `Channel`")
