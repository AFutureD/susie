# Optimize AcpMessage Markdown

* Task: 260413T2354-optimize-acpmessage-markdown
* Author: [Huanan](https://github.com/AFutureD)
* Status: DONE
* Type: BUG
* Related: []


## Background

`AcpMessage.markdown()` currently flattens tool calls into a single quoted status line.

That output loses most of the tool-call context and does not map well to Telegram's richer formatting model, especially for long tool-call payloads.


## Goal

Improve ACP message rendering so tool calls are shown as expandable blockquotes in Telegram while preserving normal assistant markdown formatting.


## Requirements

- Keep the existing assistant/thought text readable.
- Render completed and failed tool calls as collapsed Telegram blockquotes.
- Include useful tool-call context such as title, status, locations, input, and output summaries.
- Add regression coverage for ACP rendering and Telegram send behavior.


## Notes

- Telethon's built-in markdown parser does not create blockquote entities.
- Telegram blockquotes can be created via `MessageEntityBlockquote(collapsed=True)`, so the ACP renderer needs to provide entity metadata to the Telegram channel layer.
