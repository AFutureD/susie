from typing import TypeAlias

import acp
from pydantic import BaseModel

AcpMessageChunk: TypeAlias = (
    acp.schema.AgentMessageChunk | acp.schema.AgentThoughtChunk | acp.schema.ToolCallStart | acp.schema.ToolCallProgress | acp.schema.AgentPlanUpdate
)

# | acp.schema.AvailableCommandsUpdate
# | acp.schema.CurrentModeUpdate
# | acp.schema.ConfigOptionUpdate


class AcpMessage(BaseModel):
    prompt: acp.schema.UserMessageChunk | str | None

    # sessonInfo: acp.schema.SessionInfoUpdate
    model: acp.schema.CurrentModeUpdate | None
    chunks: list[AcpMessageChunk] = []
    usage: acp.schema.UsageUpdate | None
    in_turn: bool = True

    def markdown(self) -> str:
        def content_text(content: object) -> str:
            if isinstance(content, acp.schema.TextContentBlock):
                return content.text
            return ""

        def quote(text: str) -> str:
            return "\n".join(f"> {line}" if line else ">" for line in text.splitlines())

        def tool_label(chunk: acp.schema.ToolCallStart | acp.schema.ToolCallProgress) -> str:
            if chunk.title:
                return chunk.title
            if chunk.kind:
                return chunk.kind
            return chunk.tool_call_id

        parts: list[str] = []

        for chunk in self.chunks:
            match chunk:
                case acp.schema.AgentThoughtChunk():
                    text = content_text(chunk.content)
                    parts.append(text)
                    # if text:
                    #     parts.append(quote(text))
                case acp.schema.ToolCallStart():
                    parts.append(f"\n- [ ] {tool_label(chunk)}\n")
                case acp.schema.ToolCallProgress():
                    if chunk.status in {"completed", "failed"}:
                        label = tool_label(chunk)
                        if chunk.status == "failed":
                            label = f"{label} (failed)"
                        parts.append(f"\n- [x] {label}\n")
                case acp.schema.AgentMessageChunk():
                    text = content_text(chunk.content)
                    if text:
                        parts.append(text)
                case _:
                    continue

        return "".join(parts)
