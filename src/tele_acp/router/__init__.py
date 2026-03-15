from tele_acp.types import Chatable, ChatMessage


class Router:
    def __init__(self, chat_handler: Chatable):
        self._chat_handler = chat_handler
        self._accepting = True

    async def route(self, message: ChatMessage) -> None:
        if not self._accepting:
            return

        # TODO: add middlewares in the future.
        await self._chat_handler.receive_message(message)

    def stop_accepting(self) -> None:
        self._accepting = False
