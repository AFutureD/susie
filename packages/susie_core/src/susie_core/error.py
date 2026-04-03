from __future__ import annotations

from typing import Never


def unreachable(message: str) -> Never:
    """Raise an AssertionError with the given message."""
    raise AssertionError(f"Expected code to be unreachable. {message}")


class SusieException(Exception):
    """Base exception class for Tele CLI."""

    pass


class ConfigError(SusieException, ValueError):
    """Exception raised when there is an error in the configuration file."""

    pass


class CurrentSessionPathNotValidError(SusieException, RuntimeError):
    """Exception raised when there is an error during validating the current session path."""

    pass


class ChatAwareError(SusieException, RuntimeError):
    """Exception raised when there is an error during executing a command."""

    pass
