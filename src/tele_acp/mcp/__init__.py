from __future__ import annotations

from datetime import datetime, timedelta
from typing import cast

from mcp.server.fastmcp import Context, FastMCP
from telethon import hints

from tele_acp.telegram import TGClient


class MCP(FastMCP):
    def __init__(self):
        super().__init__(name="telegram_mcp_server", json_response=True, port=9998)
        self._clients: dict[str, TGClient] = {}

    @property
    def mcp_url(self) -> str:
        return f"http://{self.settings.host}:{self.settings.port}{self.settings.streamable_http_path}"

    def set_tele_client(self, channel_id: str, tele_client: TGClient) -> None:
        self._clients[channel_id] = tele_client

    def get_tele_client(self, channel_id: str) -> TGClient:
        tele_client = self._clients.get(channel_id)
        if tele_client is None:
            raise RuntimeError(f"Telegram client is not bound for channel: {channel_id}")

        if not tele_client.is_connected():
            raise RuntimeError(f"Telegram client is not connected for channel: {channel_id}")

        return tele_client


mcp_server = MCP()


@mcp_server.tool()
async def get_self(ctx: Context, channel: str) -> str | None:
    """Get self information for a configured Telegram channel."""
    tele_client = cast(MCP, ctx.fastmcp).get_tele_client(channel)
    me = await tele_client.get_user()
    if not me:
        return None
    return me.to_json()


@mcp_server.tool()
async def send_message(
    ctx: Context,
    channel: str,
    entity: str | int,
    message: str,
    file: list[str] | None = None,
) -> str | None:
    """Send a message to a Telegram entity on the given channel.

    Args:
        channel:
            The Telegram channel id configured in tele-acp.
        entity:
            `peer id` or `username` or `phone`

            - `int`: treated as a `peer id` (see https://core.telegram.org/api/peers#peer-id).
            - `str`: first try Telethon's resolver (username, phone, etc).

            If that fails, fall back to scanning dialogs and picking the *unique* match by:
                - dialog name contains `entity` (case-insensitive), or
                - dialog peer id equals `entity`, or
                - dialog entity id equals `entity`.

        message: The content string of the message.

        file:
            The file path.

            - `str`: single file path.
            - `list[str]`: multiple file paths.
            - `None`: no file.

    Return:
        The sent message if succeed.

    """
    tele_client = cast(MCP, ctx.fastmcp).get_tele_client(channel)

    send_file = cast(hints.FileLike | list[hints.FileLike] | None, file)
    msg = await tele_client.send_message(entity=entity, message=message, file=send_file)

    try:
        return msg.to_json()
    except Exception as e:
        return str(e)


@mcp_server.tool()
async def list_messages(
    ctx: Context,
    channel: str,
    entity: str | int,
    date_start: str | None = None,
    date_end: str | None = None,
    date_range: str | None = None,
    offset_id: int = 0,
    limit: int | None = None,
    reverse: bool = False,
) -> list[str] | None:
    """List messages from a dialog on the given channel.

    By default if no date range is specified and not limit is given, it fetches the latest message.

    Args:
        channel:
            The Telegram channel id configured in tele-acp.
        entity:
            The entity to list messages from. `peer id` or `username` or `phone`

        date_start:
            The start date for the message range.
            Accepts natural language dates, e.g. "-2d", "yesterday", "2 weeks ago".
        date_end:
            The end date for the message range.
            Accepts natural language dates, e.g. "-1d", "yesterday", "2 weeks ago".
        date_range:
            The date range for the message range. overrides `date_start` and `date_end`.
            Accepts natural language date ranges, e.g. "last week", "this month".
            Special case: "this week" is treated as Sunday..Saturday.
        offset_id: The message ID to start from (excluded).
        limit:
            The maximum number of messages to fetch.
        reverse:
            Whether to reverse the order of messages.

    Returns:
        A list of messages.

    """
    tele_client = cast(MCP, ctx.fastmcp).get_tele_client(channel)

    import dateparser
    from dateparser.search import search_dates

    date_from: datetime | None = None
    if date_start:
        date_from = dateparser.parse(date_start)
        date_from = date_from and date_from.replace(hour=0, minute=0, second=0, microsecond=0)

    date_to: datetime | None = None
    if date_end:
        date_to = dateparser.parse(date_end)
        date_to = date_to and date_to.replace(hour=0, minute=0, second=0, microsecond=0)

    date_span: list[datetime] | None = None
    if date_range and date_range == "this week":
        start_date = dateparser.parse("sunday")
        assert start_date is not None
        date_span = [start_date, start_date + timedelta(days=6)]
    elif date_range:
        dates = search_dates(date_range, settings={"RETURN_TIME_SPAN": True}) or []
        if len(dates) == 2:
            # https://github.com/scrapinghub/dateparser/blob/cd5f226454e0ed3fe93164e7eff55b00f57e57c7/dateparser/search/search.py#L202
            start = next((x for (s, x) in dates if "start" in s), None)
            end = next((x for (s, x) in dates if "end" in s), None)
            if start and end:
                date_span = [start, end]

    if date_span:
        date_from = date_span[0]
        date_to = date_span[1]

    messages = await tele_client.list_messages(
        entity=entity,
        date_start=date_from,
        date_end=date_to,
        offset_id=offset_id,
        limit=limit,
        reverse=reverse,
    )

    return [msg.to_json() or "{}" for msg in messages]
