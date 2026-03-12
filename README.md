# tele-acp


An `APP` have to main class `AgentRuntimeManager` and "ChannelGateway"

A ChannelGateway can have multiple Channel
A Channel may be a Telegram_User or Telegram_Bot.
A Channel have multiple Dialog

A AgentRuntimeManager may have multiple AgentSettings
A AgentSettings may have mutiple AgentRuntime 

A Dialog have A AgentRuntime, connect via inbound and outbound.
Dialog -> AgentRuntime: InobundMessage
Dialog -> AgentRuntime: OutboundMessage
