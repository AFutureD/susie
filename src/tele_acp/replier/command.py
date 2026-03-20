from tele_acp_core import Chatable, ChatMessage, ChatMessageTextPart, ChatReplyable, CommandExecutable

SUSIE_COMMAND_TRIGGER = "/"


class CommandReplier(ChatReplyable):
    def __init__(self, executor: CommandExecutable):
        self._executor = executor

    async def receive_message(self, chat: Chatable, message: ChatMessage) -> bool:
        text_part = next((x for x in message.parts if isinstance(x, ChatMessageTextPart)), None)
        if text_part is None:
            return False

        text = text_part.text
        if not text.startswith(SUSIE_COMMAND_TRIGGER):
            return False

        command = text.removeprefix(SUSIE_COMMAND_TRIGGER)
        name, args, kwargs = self.parse_command(command)
        if not await self._executor.can_execute(name):
            await chat.send_message(
                ChatMessage(
                    id=None,
                    channel_id=message.channel_id,
                    chat_id=message.chat_id,
                    receiver=None,
                    out=False,
                    mute=False,
                    parts=[ChatMessageTextPart(f"Unknown command: {name}")],
                )
            )
            return True

        response = await self._executor.execute_command(name, *args, **kwargs)
        if isinstance(response, str):
            response_message = ChatMessage(
                id=None,
                channel_id=message.channel_id,
                chat_id=message.chat_id,
                receiver=None,
                out=False,
                mute=False,
                parts=[ChatMessageTextPart(response)],
            )
            await chat.send_message(response_message)

        return True

    def parse_command(self, command: str) -> tuple[str, list, dict]:
        name, *args = command.split()
        return name, args, {}
