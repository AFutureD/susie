from __future__ import annotations

from pathlib import Path

from .constant import NAME


def get_app_user_default_dir() -> Path:
    """Get the application default directory path."""
    # TODO: respect XDG and other environment variable.
    share_dir = Path.home() / ".config" / NAME
    share_dir.mkdir(parents=True, exist_ok=True)
    return share_dir
