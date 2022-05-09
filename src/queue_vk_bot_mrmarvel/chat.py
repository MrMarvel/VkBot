import json
from enum import Enum, auto
from queue import Queue

from .chat_i import IChat
from .chat_user import ChatUser
from .conversation_in_chat import ConversationInChat
from .gl_vars import pipeline_to_send_msg


class ChatLogic(IChat):
    """
    Описывает все отношения пользователей в чате беседы с ботом.
    Существует пока есть очередь, либо кто-то недописал команды (уязвимость).
    """

    def user_wants_to_force_next_queue(self, user: ChatUser) -> ChatUser | None:
        if user.is_able_to_create_queue:
            if self.__queue_state == self._QueueState.queue_in_progress:
                queue = self.__queue
                if queue.not_empty:
                    return queue.get()
        return None

    class _QueueState(Enum):
        no_queue_running = auto()
        queue_will_start = auto(),
        queue_in_progress = auto(),
        queue_will_end = auto()

    def __init__(self, chat_id: int):
        self.__chat_id = chat_id
        self.__queue_state = self._QueueState.no_queue_running
        self.__relations_in_chat: [int, ConversationInChat] = dict()
        self.__queue: Queue[ChatUser] | None = None

    def get_relationship_with_user(self, user_id: int) -> ConversationInChat | None:
        return self.__relations_in_chat.get(user_id, None)

    def start_relationship_with_user(self, user_id: int) -> ConversationInChat:
        r = self.__relations_in_chat.get(user_id, None)
        if r is None:
            user = ChatUser.load_user(user_id=user_id, chat_id=self.__chat_id)
            r = ConversationInChat(user=user, chat=self)
            self.__relations_in_chat[user_id] = r
        return r

    def user_wants_to_create_queue(self, user_id: int):
        user = ChatUser.load_user(chat_id=self.__chat_id, user_id=user_id)
        if user.is_able_to_create_queue:
            qs = self.__queue_state
            match qs:
                case qs.no_queue_running:
                    self.__send_message("Создаём очередь.")
                    self.__create_queue()
        else:
            self.__send_message("Ты не можешь создавать очереди. Попроси того, кто может ;)")

    def user_wants_to_join_to_queue(self, user: ChatUser) -> int | None:
        """
        Пользователь требует добавить его в очередь
        :param user: Пользователь
        :return: Номер позиции в очереди (от 1), Вернёт None если уже в очереди
        """
        if self.__queue_state != self._QueueState.queue_in_progress:
            self.__send_message("Очередь не начата")
            return
        queue = self.__queue
        if queue is None:
            return
        queue_arr = list(queue.queue)
        if user in queue_arr:
            return None
        queue.put(user)
        return list(queue.queue).index(user) + 1

    def __create_queue(self):
        self.__queue_state = self._QueueState.queue_will_start
        self.__queue = Queue()
        self.__queue_state = self._QueueState.queue_in_progress

    def next_on_queue(self, offset: int = 0) -> ChatUser | None:
        if self.__queue_state != self._QueueState.queue_in_progress:
            return None
        if self.__queue is None:
            return None
        queue_arr: list[ChatUser] = list(self.__queue.queue)
        if len(queue_arr) < offset + 1:
            return None
        return queue_arr[offset]

    @property
    def chat_id(self):
        return self.__chat_id

    @property
    def is_queue_running(self) -> bool:
        return True if self.__queue_state == self._QueueState.queue_in_progress else False

    def __send_message(self, messsage: str):
        pipeline_to_send_msg.put_nowait((self.__chat_id, messsage, False))

    def send_queue_list(self) -> None:
        """
        Отправляет в чат беседы очередь.
        """
        if self.__queue is None:
            return
        msg = "Очередь:"
        arr: list[ChatUser] = list(self.__queue.queue)
        n = len(arr)
        for i in range(10):
            msg += f"\n{i + 1:>2d}" + "    "
            if i < n:
                msg += f"@id{arr[i].user_id}"
            else:
                msg += "..."
        keyboard = {
            "one_time": False,
            "buttons": [
                [self.__get_button("Привет", "positive"), self.__get_button("Привет", "positive")],
                [self.__get_button("Привет", "positive"), self.__get_button("Привет", "positive")]
            ]
        }
        keyboard = json.dumps(keyboard, ensure_ascii=False).encode("utf-8")
        keyboard = str(keyboard).encode("utf-8")
        self.__send_message(messsage=msg)
        # self.__send_messange_with_keyboard(message=msg, keyboard=keyboard)

    @staticmethod
    def __get_button(text: str, color) -> dict:
        return {
            "action": {
                "type": "text",
                "payload": "{\"Button\": \"" + "1" + "\"}",
                "label": f"{text}"
            },
            "color": f"{color}"
        }

    def __send_messange_with_keyboard(self, message: str, keyboard) -> None:
        # msg = {'chat_id': self.__chat_id, 'keyboard': keyboard}
        pipeline_to_send_msg.put_nowait((self.__chat_id, message, False))
        pass
