from pydantic import BaseModel, Field

from .agent import DEFAULT_AGENT_ID, AgentConfig
from .channel import DEFAULT_TELEGRAM_ID, DialogBind, TelegramBotChannel, TelegramChannel


class Config(BaseModel):
    api_id: int = Field(description="Telegram api_id")
    api_hash: str = Field(description="Telegram api_hash")
    dialog_idle_timeout_minutes: int = Field(default=30, ge=1, description="Idle timeout for per-dialog context")

    channels: list[TelegramChannel | TelegramBotChannel] = [TelegramChannel(id=DEFAULT_TELEGRAM_ID)]
    agents: list[AgentConfig] = [AgentConfig(id=DEFAULT_AGENT_ID)]
    bindings: list[DialogBind] = []

    @model_validator(mode="after")
    def check_bindings(self) -> Self:
        # Valiate Channels
        channel_ids = map(lambda x: x.id, self.channels)
        assert len(channel_ids) == len(set(channel_ids)), "Channel ids must be unique"

        # Valiate Agents
        agent_ids = map(lambda x: x.id, self.agents)
        assert len(agent_ids) == len(set(agent_ids)), "Agent ids must be unique"

        return self
