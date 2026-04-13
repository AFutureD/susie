import json
from dataclasses import dataclass
from typing import Any, Literal, TypeAlias

import acp
from acp.schema import AudioContentBlock, EmbeddedResourceContentBlock, ImageContentBlock, ResourceContentBlock, StopReason, TextContentBlock
from pydantic import BaseModel

AcpAgentMessageChunk: TypeAlias = (
    acp.schema.AgentMessageChunk | acp.schema.AgentThoughtChunk | acp.schema.ToolCallStart | acp.schema.ToolCallProgress | acp.schema.AgentPlanUpdate
)
AcpContentBlock: TypeAlias = TextContentBlock | ImageContentBlock | AudioContentBlock | ResourceContentBlock | EmbeddedResourceContentBlock

_SectionKey: TypeAlias = Literal["THINK", "MESSAGE", "TOOL"]

# | acp.schema.AvailableCommandsUpdate
# | acp.schema.CurrentModeUpdate
# | acp.schema.ConfigOptionUpdate


@dataclass
class _RenderedSection:
    key: _SectionKey
    text: str
    parse_markdown: bool
    expandable_blockquote: bool = False


class AcpMessage(BaseModel):
    # TODO: make it list and as message can handle queued messages.
    prompt: list[AcpContentBlock] = []

    # sessonInfo: acp.schema.SessionInfoUpdate
    model: acp.schema.CurrentModeUpdate | None = None

    delta: AcpAgentMessageChunk | None = None
    chunks: list[AcpAgentMessageChunk] = []

    usage: acp.schema.UsageUpdate | None = None
    stop_reason: StopReason | None = None

    def markdown(self) -> str:
        parts: list[str] = []

        for section in self._rendered_sections():
            text = section.text.strip()
            if text == "":
                continue

            if section.expandable_blockquote:
                text = "\n".join("> " if line == "" else f"> {line}" for line in text.splitlines())

            parts.append(text)

        return "\n\n".join(parts)

    def rich_text_sections(self) -> list[dict[str, str]]:
        sections: list[dict[str, str]] = []

        for section in self._rendered_sections():
            text = section.text.strip()
            if text == "":
                continue

            text_type = "plain"
            if section.expandable_blockquote:
                text_type = "expandable_blockquote"
            elif section.parse_markdown:
                text_type = "markdown"

            sections.append(
                {
                    "text": text,
                    "text_type": text_type,
                }
            )

        return sections

    def _rendered_sections(self) -> list[_RenderedSection]:
        sections: list[_RenderedSection] = []

        for chunk in self.chunks:
            match chunk:
                case acp.schema.AgentThoughtChunk():
                    self._append_section(sections, "THINK", self._describe_content_block(chunk.content), parse_markdown=True)
                case acp.schema.AgentMessageChunk():
                    self._append_section(sections, "MESSAGE", self._describe_content_block(chunk.content), parse_markdown=True)
                case acp.schema.ToolCallProgress():
                    description = self._describe_tool_call(chunk)
                    if description != "":
                        sections.append(
                            _RenderedSection(
                                key="TOOL",
                                text=description,
                                parse_markdown=False,
                                expandable_blockquote=True,
                            )
                        )
                case _:
                    continue

        return sections

    def _append_section(self, sections: list[_RenderedSection], key: _SectionKey, text: str, *, parse_markdown: bool) -> None:
        if text == "":
            return

        if sections and sections[-1].key == key and sections[-1].parse_markdown == parse_markdown and not sections[-1].expandable_blockquote:
            sections[-1].text += text
            return

        sections.append(_RenderedSection(key=key, text=text, parse_markdown=parse_markdown))

    def _describe_content_block(self, content: AcpContentBlock) -> str:
        if isinstance(content, TextContentBlock):
            return content.text
        if isinstance(content, ImageContentBlock):
            return "ImageContentBlock"
        if isinstance(content, AudioContentBlock):
            return "AudioContentBlock"
        if isinstance(content, ResourceContentBlock):
            return "ResourceContentBlock"
        if isinstance(content, EmbeddedResourceContentBlock):
            return "EmbeddedResourceContentBlock"
        return ""

    def _describe_tool_call(self, chunk: acp.schema.ToolCallProgress) -> str:
        status = chunk.status
        if status not in {"completed", "failed"}:
            return ""

        found = next((item for item in self.chunks if isinstance(item, acp.schema.ToolCallStart) and item.tool_call_id == chunk.tool_call_id), None)
        title = chunk.title or (found.title if found is not None else None)
        if title is None:
            return ""

        kind = chunk.kind or (found.kind if found is not None else None)
        content = chunk.content if chunk.content is not None else (found.content if found is not None else None)
        locations = chunk.locations or (found.locations if found is not None else None) or []
        raw_input = chunk.raw_input if chunk.raw_input is not None else (found.raw_input if found is not None else None)
        raw_output = chunk.raw_output if chunk.raw_output is not None else (found.raw_output if found is not None else None)

        lines = [f"Tool call: {title}", f"Status: {status}"]

        if kind is not None:
            lines.append(f"Kind: {kind}")

        if len(locations) > 0:
            lines.append("Locations:")
            lines.extend(f"- {location.path}:{location.line}" if location.line is not None else f"- {location.path}" for location in locations)

        if content:
            lines.append("Content:")
            lines.extend(self._describe_tool_call_content(content))

        if raw_input is not None:
            lines.append("Raw input:")
            lines.extend(self._indent_block(self._format_value(raw_input)))

        if raw_output is not None:
            lines.append("Raw output:")
            lines.extend(self._indent_block(self._format_value(raw_output)))

        return "\n".join(lines)

    def _describe_tool_call_content(
        self,
        content: list[acp.schema.ContentToolCallContent | acp.schema.FileEditToolCallContent | acp.schema.TerminalToolCallContent],
    ) -> list[str]:
        lines: list[str] = []

        for index, item in enumerate(content, start=1):
            match item:
                case acp.schema.ContentToolCallContent():
                    lines.append(f"[{index}] content")
                    lines.extend(self._indent_block(self._describe_content_tool_call_content(item)))
                case acp.schema.FileEditToolCallContent():
                    lines.append(f"[{index}] diff: {item.path}")
                    if item.old_text is not None:
                        lines.append("  Old text:")
                        lines.extend(self._indent_block(item.old_text, prefix="    "))
                    lines.append("  New text:")
                    lines.extend(self._indent_block(item.new_text, prefix="    "))
                case acp.schema.TerminalToolCallContent():
                    lines.append(f"[{index}] terminal: {item.terminal_id}")

        return lines

    def _describe_content_tool_call_content(self, item: acp.schema.ContentToolCallContent) -> str:
        content = item.content

        if isinstance(content, TextContentBlock):
            return content.text
        if isinstance(content, ImageContentBlock):
            return self._format_value(content.model_dump(mode="json", by_alias=True, exclude_none=True))
        if isinstance(content, AudioContentBlock):
            return self._format_value(content.model_dump(mode="json", by_alias=True, exclude_none=True))
        if isinstance(content, ResourceContentBlock):
            return self._format_value(content.model_dump(mode="json", by_alias=True, exclude_none=True))
        if isinstance(content, EmbeddedResourceContentBlock):
            return self._format_value(content.model_dump(mode="json", by_alias=True, exclude_none=True))

        return self._format_value(content)

    def _indent_block(self, text: str, *, prefix: str = "  ") -> list[str]:
        if text == "":
            return [prefix.rstrip()]

        return [f"{prefix}{line}" if line != "" else prefix.rstrip() for line in text.splitlines()]

    def _format_value(self, value: Any) -> str:
        try:
            if hasattr(value, "model_dump"):
                text = json.dumps(value.model_dump(mode="json", by_alias=True, exclude_none=True), ensure_ascii=False, indent=2, sort_keys=True)
            elif isinstance(value, str):
                text = value
            else:
                text = json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True)
        except TypeError:
            text = str(value)

        return text
