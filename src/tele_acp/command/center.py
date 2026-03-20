import inspect
from typing import Any, Callable

from tele_acp_core import CommandExecutable
from tele_acp_core.command import AnyFunction, Command

from tele_acp.constant import NAME


class CommandCenter(CommandExecutable):
    def __init__(self) -> None:
        self._registered_commands_by_name: dict[str, Command] = {}
        self.add_command(self.show_help, name="help", description="show help message")
        self.add_command(self.echo, name=f"{NAME}.echo", description="echo a message")

    def get_command(self, name: str) -> Command | None:
        return self._registered_commands_by_name.get(name)

    async def can_execute(self, name: str) -> bool:
        return name in self._registered_commands_by_name

    async def execute_command(self, name: str, *args, **kwargs) -> Any:
        name = name.strip()
        command = self.get_command(name)
        if not command:
            raise ValueError(f"command not found: {name}")

        registered_command = self.get_command(name)
        if registered_command is None:
            raise ValueError(f"unknown command: {name}")

        result = registered_command.fn(*args, **kwargs)
        if inspect.isawaitable(result):
            return await result
        return result

    def command(self, name: str | None = None, description: str | None = None) -> Callable[[AnyFunction], AnyFunction]:
        def decorator(fn: AnyFunction) -> AnyFunction:
            self.add_command(fn, name=name, description=description)
            return fn

        return decorator

    def add_command(self, fn: AnyFunction, *, name: str | None = None, description: str | None = None) -> Command:
        command_name = name or fn.__name__  # ty:ignore[unresolved-attribute]
        if name == "<lambda>":
            raise ValueError("You must provide a name for lambda functions")

        if command_name in self._registered_commands_by_name:
            raise ValueError(f"command already registered: {command_name}")

        description = description or inspect.getdoc(fn) or ""
        command = Command(fn=fn, name=command_name, description=description)

        self._registered_commands_by_name[command_name] = command
        return command

    async def show_help(self) -> str:
        lines = [f"/{command.name}: {command.description}" for command in self._registered_commands_by_name.values()]
        return "\n".join(lines)

    async def echo(self, message: str) -> str:
        """Echo the message back to the user."""
        return message
