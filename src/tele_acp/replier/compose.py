from tele_acp_core import Chatable, ChatMessage, ChatReplyable


class ComposedReplier(ChatReplyable):
    def __init__(self, *ordered_repliers: ChatReplyable) -> None:
        self._repliers = ordered_repliers

    async def receive_message(self, chat: Chatable, message: ChatMessage) -> bool:
        ok = False
        for replier in self._repliers:
            try:
                ok = await replier.receive_message(chat, message)

                # TODO: check if the replier allow multiple replies for the same message.
                # for now, we only have to replisers, agent and command,
                # so once command is ok, we do not need to continue to agent.
                if ok:
                    return ok
            except Exception as e:
                print(f"replier {type(replier).__name__} failed with error: {e}")
        return ok
