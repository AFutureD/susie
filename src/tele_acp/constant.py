from __future__ import annotations

import importlib.metadata

_meta = importlib.metadata.distribution("tele-acp")

NAME = "ACP Interface on Telegram"

APP_NAME = _meta.name
VERSION = _meta.version
