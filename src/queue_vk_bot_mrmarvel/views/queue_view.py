from ..models.queue_model import QueueInChat
from ..utils.bot_i import IBot


class QueueViewInChat:
    def __init__(self, model: QueueInChat, bot: IBot):
        self._model = model
        self._bot = bot
        self._queue_list_message_id = None
        self.view_did_load()

    def view_did_load(self):
        self._bot.write_msg_to_chat(self._model.chat_id, "Очередь создана!")

    def reset_queue_list(self):
        pass