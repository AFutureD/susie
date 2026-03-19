import enum
from typing import TypeAlias

from pydantic.fields import Field
from tele_acp_core import ChannelSettings, ChannelType

# How to obtain your api_id and api_hash is described here: https://core.telegram.org/api/obtaining_api_id
# The default values get from here: https://github.com/telegramdesktop/tdesktop/blob/dev/docs/api_credentials.md
DEFAULT_TELEGRAM_API_ID = 17349
DEFAULT_TELEGRAM_API_HASH = "344583e45741c457fe1862106095a5eb"


class TelegramChannelType(ChannelType, enum.Enum):
    TELEGRAM_USER = "telegram_user"
    TELEGRAM_BOT = "telegram_bot"


class TelegramChannel(ChannelSettings):
    session_name: str = Field(description="The session name for the Telegram client")

    whitelist: list[str] | None = Field(default=[], description="The list of allowed users. peer id or group id")


class TelegramUserChannel(TelegramChannel):
    type: ChannelType = TelegramChannelType.TELEGRAM_USER

    allow_contacts: bool = Field(default=True, description="Whether to allow contacts")


class TelegramBotChannel(TelegramChannel):
    type: ChannelType = TelegramChannelType.TELEGRAM_BOT

    token: str = Field(description="Telegram bot token")


TypeTelegramChannel: TypeAlias = TelegramUserChannel | TelegramBotChannel
