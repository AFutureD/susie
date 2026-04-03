import logging

from susie_core import Chatable, ChatMessage, ChatReplyable


class ComposedReplier(ChatReplyable):
    def __init__(self, *ordered_repliers: ChatReplyable) -> None:
        self._repliers = ordered_repliers
        self.logger = logging.getLogger(f"{self.__class__.__module__}.{self.__class__.__name__}")

    async def cancel(self):
        for replier in self._repliers:
            await replier.cancel()

    async def receive_message(self, chat: Chatable, message: ChatMessage):
        for replier in self._repliers:
            try:
                await replier.receive_message(chat, message)
            except Exception as e:
                self.logger.error("Error while receiving message: %s", e)
