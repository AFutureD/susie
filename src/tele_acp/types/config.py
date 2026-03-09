from pydantic import BaseModel, Field

from .agent import DEFAULT_AGENT_ID, AgentConfig
from .channel import DEFAULT_TELEGRAM_ID, DialogBind, TelegramBotChannel, TelegramChannel


class Config(BaseModel):
    api_id: int = Field(description="Telegram api_id")
    api_hash: str = Field(description="Telegram api_hash")
    dialog_idle_timeout_minutes: int = Field(default=30, ge=1, description="Idle timeout for per-dialog context")

    channel: list[TelegramChannel | TelegramBotChannel] = [TelegramChannel(id=DEFAULT_TELEGRAM_ID)]
    agents: list[AgentConfig] = [AgentConfig(id=DEFAULT_AGENT_ID)]
    bindings: list[DialogBind] = []
