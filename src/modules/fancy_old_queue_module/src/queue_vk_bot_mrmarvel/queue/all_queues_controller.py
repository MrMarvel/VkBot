from ..queue.queue_model import QueueInChat
from ..queue.queue_controller import QueueControllerInChat
from ..bot.bot_i import IBot
from ..utils.chat_user import User
from ..queue.queue_view import QueueViewInChat


class AllQueueController:
    """
    Управляющий класс.
    Управляет очередями в чатах.
    НЕ СУЩНОСТЬ
    """

    def __init__(self, bot: IBot):
        self._bot = bot
        self._queues_in_chats = dict[int, QueueControllerInChat]()
        # self.put(ChatUser(10, 1))

    def __queue_did_push(self, added_user: User):
        pass

    def __queue_did_pop(self, added_user: User):
        pass

    def create_queue(self, chat_id: int) -> QueueControllerInChat:
        queue_controller_in_chat = self._queues_in_chats.get(chat_id, None)
        if queue_controller_in_chat is None:
            queue_in_chat = QueueInChat(chat_id)
            queue_in_chat.did_push = self.__queue_did_push
            queue_in_chat.did_pop = self.__queue_did_pop

            queue_view_in_chat = QueueViewInChat(model=queue_in_chat, sender=self._bot)

            queue_controller_in_chat = QueueControllerInChat(model=queue_in_chat, view=queue_view_in_chat)

            self._queues_in_chats[chat_id] = queue_controller_in_chat
        return queue_controller_in_chat

    def get_queue(self, in_chat_id: int) -> QueueControllerInChat | None:
        contr = self._queues_in_chats.get(in_chat_id, None)
        if contr is None:
            return None
        return contr

    def destroy_queue_in_chat(self, in_chat_id: int) -> QueueControllerInChat | None:
        return self._queues_in_chats.pop(in_chat_id, None)

    def destroy_queue(self, queue_in_chat: QueueControllerInChat) -> QueueControllerInChat | None:
        values = list(self._queues_in_chats.values())
        return self.destroy_queue_in_chat(in_chat_id=values.index(queue_in_chat))

    # @deprecated("МЕТОДЫ СУЩНОСТИ БУДУТ УДАЛЕНЫ")
    # def get_queue_as_list(self) -> list:
    #     """
    #     Получение копии очереди пользователей чата.
    #     :return: Список
    #     """
    #     return deepcopy(self._queue)
    #
    # @deprecated("МЕТОДЫ СУЩНОСТИ БУДУТ УДАЛЕНЫ")
    # @property
    # def empty(self) -> bool:
    #     return len(self._queue) == 0
    #
    # @deprecated("МЕТОДЫ СУЩНОСТИ БУДУТ УДАЛЕНЫ")
    # @property
    # def chat_id(self) -> int:
    #     return self._chat_id
    #
    # @deprecated("МЕТОДЫ СУЩНОСТИ БУДУТ УДАЛЕНЫ")
    # def get(self, pos: int) -> ChatUser | None:
    #     """
    #     Получение пользователя по позиции в очереди.
    #     :param pos:
    #     :return: Пользователь
    #     """
    #     queue_list = list(self._queue)
    #     if pos < len(queue_list):
    #         return queue_list[pos]
    #     return None
    #
    # @deprecated("МЕТОДЫ СУЩНОСТИ БУДУТ УДАЛЕНЫ")
    # def put(self, elem: ChatUser) -> int | None:
    #     if elem in self._queue:
    #         return None
    #     self._queue.insert(len(self), elem)
    #     return len(self._queue)
    #
    # @deprecated("МЕТОДЫ СУЩНОСТИ БУДУТ УДАЛЕНЫ")
    # def pop(self) -> ChatUser | None:
    #     q = self._queue
    #     try:
    #         elem = q.pop(0)
    #         return elem
    #     except Empty:
    #         pass
    #     return None
    #
    # @deprecated("МЕТОДЫ СУЩНОСТИ БУДУТ УДАЛЕНЫ")
    # def __len__(self):
    #     return self._queue.__len__()

    # def skip_force(self) -> ChatUser | None:
    #     return self.pop()
    #
    # def get_next_on_queue(self) -> ChatUser | None:
    #     queue = list(self._queue)
    #     if len(queue) < 2:
    #         return None
    #     return queue[1]
    #
    # def show_queue_list_message(self):
    #     values = {"random_id": time_ns(),
    #               "chat_id": self._chat_id,
    #               "message": f"СПИСОК в чате {self._chat_id}"}
    #     raise NotImplementedError
    #     result = None
    #     # result = self._vk.method(method="messages.send", values=values)
    #     if type(result) is dict:
    #         result: dict
    #         conversation_message_id = result.get("conversation_message_id", None)
    #         if conversation_message_id is None:
    #             print(self.__class__.__name__, inspect.currentframe().f_code.co_name, "Непредвиденная ситуация")
    #             return
    #         conversation_message_id = int(conversation_message_id)
    #         self._queue_list_message_id = conversation_message_id
    #
    # def notify_chat_next_in_queue(self):
    #     pass
    #
    # def switch(self, pos1: int, pos2: int) -> bool:
    #     """
    #     Поменять местами двух пользователей по местам в очередях
    #     :param pos1:
    #     :param pos2:
    #     :return: Успешность выполнения
    #     """
    #     queue_list = self._queue
    #     if pos1 >= len(queue_list):
    #         return False
    #     if pos2 >= len(queue_list):
    #         return False
    #     t = queue_list[pos1]
    #     queue_list[pos1] = queue_list[pos2]
    #     queue_list[pos2] = t
    #     return True
