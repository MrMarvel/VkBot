from ..queue.queue_model import QueueInChat
from ..queue.queue_view import QueueViewInChat


class QueueControllerInChat:
    def __init__(self, model: QueueInChat, view: QueueViewInChat):
        self._model = model
        self._view = view

    @property
    def model(self):
        return self._model

    @property
    def view(self):
        return self._view
