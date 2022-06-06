import copy
import inspect
import time
from queue import Queue, Empty
from time import time_ns

from deprecated import deprecated

from queue_vk_bot_mrmarvel.utils.chat_user import ChatUser


class QueueController:
    """
    Контроллер и модель из паттерна MVC.
    Управляет очередями в чате.
    1 контроллер = 1 очередь
    """

    def __init__(self, chat_id):
        super().__init__()
        self._queue_list_message_id = None
        self._queue = Queue[ChatUser]()
        self._chat_id = chat_id

    @property
    def queue(self) -> list:
        """
        Получение копии очереди пользователей чата.
        :return: Список
        """
        return copy.deepcopy(self._queue.queue)

    @property
    def empty(self) -> bool:
        return len(self._queue.queue) == 0

    @property
    def chat_id(self) -> int:
        return self._chat_id

    def put(self, elem: ChatUser) -> int | None:
        if elem in self._queue.queue:
            return None
        self._queue.put(elem)
        return len(self._queue.queue)

    def pop(self) -> ChatUser | None:
        q = self._queue
        try:
            elem = q.get()
            return elem
        except Empty:
            pass
        return None

    def skip_force(self) -> ChatUser | None:
        return self.pop()

    def get_next_on_queue(self) -> ChatUser | None:
        queue = list(self._queue.queue)
        if len(queue) < 2:
            return None
        return queue[1]

    def show_queue_list_message(self):
        values = {"random_id": time_ns(),
                  "chat_id": self._chat_id,
                  "message": f"СПИСОК в чате {self._chat_id}"}
        raise NotImplementedError
        result = None
        # result = self._vk.method(method="messages.send", values=values)
        if type(result) is dict:
            result: dict
            conversation_message_id = result.get("conversation_message_id", None)
            if conversation_message_id is None:
                print(self.__class__.__name__, inspect.currentframe().f_code.co_name, "Непредвиденная ситуация")
                return
            conversation_message_id = int(conversation_message_id)
            self._queue_list_message_id = conversation_message_id

    def notify_chat_next_in_queue(self):
        pass


'''
@deprecated
class ChatView:
    """
    Вид из паттерна MVC.
    Отображает изменения позиций в очередях.
    """

    def __init__(self, queue_controller: QueueController, queue_model: 'QueueModel', vk: 'VkApi'):
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
            self._user_go_message_id = message_id'''
