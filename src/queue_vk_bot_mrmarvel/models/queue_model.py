from _weakref import ReferenceType, ref
from copy import deepcopy
from typing import Callable

from ..utils.chat_user import ChatUser


class QueueInChat:
    """
    Очередь, которая отображается в чате
    Сущность
    """

    def __init__(self, chat_id: int):
        super().__init__()
        self._queue_list_message_id = None
        self._queue = list[ChatUser]()
        self._chat_id = chat_id
        self._didPush: ReferenceType[Callable[[], None]] | None = None
        self._didPop: ReferenceType[Callable[[], None]] | None = None

    @property
    def chat_id(self):
        return self._chat_id

    @property
    def did_push(self):
        return self._didPush

    @did_push.setter
    def did_push(self, f: Callable[[], None] | None):
        self._didPush = ref(f)

    @property
    def did_pop(self):
        return self._didPop

    @did_pop.setter
    def did_pop(self, f: Callable[[], None] | None):
        self._didPop = ref(f)

    def __len__(self):
        return self._queue.__len__()

    @property
    def as_list(self) -> list[ChatUser]:
        """
        Получение очереди как списка.
        :return:
        """
        return deepcopy(self._queue)

    def get_last(self) -> ChatUser | None:
        """
        Получение последнего места.
        :return:
        """
        if len(self._queue) > 0:
            return self._queue[-1]
        return None

    def get_first(self) -> ChatUser | None:
        """
        Получение первого места.
        :return:
        """
        if len(self._queue) > 0:
            return self._queue[0]
        return None

    def pop(self) -> ChatUser | None:
        """
        Получение и удаление первого места.
        :return:
        """
        if len(self._queue) > 0:
            deleted_chat_user = self._queue.pop(0)
            if self.did_pop is not None:
                self.did_pop()
            return deleted_chat_user
        return None

    def push(self, chat_user: ChatUser) -> None:
        """
        Вставка пользователя, который есть в чате, в последнее место.
        :param chat_user:
        :return:
        """
        if len(self._queue) > 0:
            if chat_user.chat_id == self._chat_id:
                self._queue.append(chat_user)
                if self.did_push is not None:
                    self.did_push()


