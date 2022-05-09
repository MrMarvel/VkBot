import inspect
import time
import weakref
from _weakref import ReferenceType
from abc import ABCMeta, abstractmethod
from queue import Queue, Empty
from typing import Any

from vk_api import VkApi


class QueueController:
    """
    Контроллер из паттерна MVC.
    Управляет очередями в чате.
    """

    def __init__(self, queue_model: 'QueueModel'):
        self._queue_model = queue_model


class ObserverModel(metaclass=ABCMeta):

    def __init__(self):
        self._observers: list[ReferenceType[QueueObserver]] = list()

    def add_observer(self, obs: 'QueueObserver') -> None:
        self._observers.append(weakref.ref(obs))

    def remove_observer(self, obs: 'QueueObserver') -> None:
        self._observers.remove(obs)

    def notify_observers(self) -> None:
        for obs in self._observers:
            obs.model_is_changed()


class QueueModel(ObserverModel):
    """
    Модель из паттерна MVC.
    Хранит информацию об очередях.
    """

    @property
    def queue(self) -> list:
        return self._queue.queue.copy()

    @property
    def chat_id(self) -> int:
        return self._chat_id

    def __init__(self, chat_id: int):
        super().__init__()
        self._chat_id = chat_id
        self._queue = Queue()

    def put(self, elem: Any) -> None:
        self._queue.put(elem)
        self.notify_observers()

    def pop(self) -> Any | None:
        q = self._queue
        try:
            elem = q.get()
            self.notify_observers()
            return elem
        except Empty:
            pass
        return None


class QueueObserver(metaclass=ABCMeta):
    """
    Наблюдатель из паттерна Наблюдатель для паттерна MVC.
    Наблюдает за параметрами очереди.
    """

    @abstractmethod
    def model_is_changed(self):
        """
        Метод, который вызывается при измении модели
        """
        pass


class ChatView(QueueObserver):
    """
    Вид из паттерна MVC.
    Отображает изменения позиций в очередях.
    """

    def __init__(self, queue_controller: QueueController, queue_model: QueueModel, vk: VkApi):
        self._queue_controller = queue_controller
        self._queue_model = queue_model
        self._queue = self._queue_model.queue
        self._queue_list_message_id = None
        self._user_go_message_id = None
        self._user_go = None
        self._vk = vk
        queue_model.add_observer(self)
        self._refresh_queue_without_user_go()

    def manual_refresh(self):
        self._refresh_queue_without_user_go()

    def model_is_changed(self) -> None:
        """
        Очередь изменилась. Либо добавился. Либо удалился.
        Либо переместился.
        """
        new_queue = self._queue_model.queue
        print(self._queue, "->", new_queue)
        self._queue = new_queue

    def _refresh_queue_without_user_go(self):
        if self._queue_list_message_id is not None:
            self.__delete_queue_list_message()
        self.__show_queue_list_message()

    def _refresh_queue_new_user_go(self):
        if self._queue_list_message_id is not None:
            self.__delete_queue_list_message()
        if self._user_go_message_id is not None:
            self.__delete_user_go_message()
        self.__show_queue_list_message()
        self.__show_user_go_message()

    def __delete_queue_list_message(self):
        if self._queue_list_message_id is None:
            print(self, "попытался удалить сообщение, которого нету!")
            return
        values = {"message_ids": 252741,  # TODO
                  "delete_for_all": 1,
                  "peer_id": 2000000000 + self._queue_model.chat_id}
        self._vk.method(method="messages.delete", values=values)
        self._queue_list_message_id = None
        # TODO

    def __delete_user_go_message(self):
        if self._user_go_message_id is None:
            print(self, "попытался удалить сообщение, которого нету!")
            return
        values = {"message_ids": self._user_go_message_id,
                  "delete_for_all": 1,
                  "peer_id": 2000000000 + self._queue_model.chat_id}
        self._vk.method(method="messages.delete", values=values)
        self._user_go_message_id = None
        # TODO

    def __show_queue_list_message(self):
        values = {"random_id": time.time_ns(),
                  "chat_id": self._queue_model.chat_id,
                  "message": f"СПИСОК в чате {self._queue_model.chat_id}"}
        result = self._vk.method(method="messages.send", values=values)
        if type(result) is dict:
            result: dict
            message_id = result.get("message_id", None)
            if message_id is None:
                print(self.__class__.__name__, inspect.currentframe().f_code.co_name, "Непредвиденная ситуация")
                return
            message_id = int(message_id)
            self._queue_list_message_id = message_id
        # TODO

    def __show_user_go_message(self):
        if self._user_go is None:
            return
        values = {"random_id": time.time_ns(),
                  "chat_id": self._queue_model.chat_id,
                  "message": f"Ты следующий, {self._user_go}!"}
        result = self._vk.method(method="messages.send", values=values)
        if type(result) is dict:
            result: dict
            message_id = result.get("message_id", None)
            if message_id is None:
                print(self.__class__.__name__, inspect.currentframe().f_code.co_name, "Непредвиденная ситуация")
                return
            message_id = int(message_id)
            self._user_go_message_id = message_id
