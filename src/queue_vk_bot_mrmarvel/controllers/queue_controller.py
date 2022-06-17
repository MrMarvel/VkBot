from queue_vk_bot_mrmarvel.models.queue_model import QueueInChat
from queue_vk_bot_mrmarvel.views.queue_view import QueueViewInChat


class QueueControllerInChat:
    def __init__(self, model: QueueInChat, view: QueueViewInChat):
        self._model = model
        self._view = view
