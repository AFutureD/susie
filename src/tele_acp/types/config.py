from pydantic import BaseModel, Field, model_validator

from .agent import DEFAULT_AGENT_ID, AgentConfig
from .channel import DEFAULT_TELEGRAM_ID, DialogBind, TelegramBotChannel, TelegramUserChannel


class Config(BaseModel):
    dialog_idle_timeout_minutes: int = Field(default=30, ge=1, description="Idle timeout for per-dialog context")

    channels: list[TelegramUserChannel | TelegramBotChannel] = [
        TelegramUserChannel(id=DEFAULT_TELEGRAM_ID, api_id=611335, api_hash="d524b414d21f4d37f08684c1df41ac9c"),
    ]
    agents: list[AgentConfig] = [AgentConfig(id=DEFAULT_AGENT_ID)]
    bindings: list[DialogBind] = []

    @model_validator(mode="after")
    def check_bindings(self) -> Self:
        # Valiate Channels
        channel_ids = map(lambda x: x.id, self.channels)
        channel_id_set = set(channel_ids)
        assert len(self.channels) >= 1, "At least one channel is required"
        assert DEFAULT_TELEGRAM_ID in channel_id_set, "Default channel must be present"
        assert len(self.channels) == len(channel_id_set), "Channel ids must be unique"
        assert len(self.channels) <= 1 or all(channel.session_name is not None for channel in self.channels), "session_name must be provided for all channels"

        # Valiate Agents
        agent_ids = map(lambda x: x.id, self.agents)
        agent_id_set = set(agent_ids)
        assert len(self.agents) >= 1, "At least one agent is required"
        assert DEFAULT_AGENT_ID in agent_id_set, "Default agent must be present"
        assert len(self.agents) == len(agent_id_set), "Agent ids must be unique"

        return self
