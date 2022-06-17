import inspect
import json
from enum import Enum, auto
from queue import Queue
from time import time_ns
from typing import Final

from vk_api import VkApi

from ..controllers.all_queues_controller import AllQueueController
from ..utils.bot_i import IBot
from ..utils.chat_i import IChat
from ..utils.chat_user import ChatUser
from ..chat_logic.dialog_in_chat import RelationshipInChat
from ..gl_vars import pipeline_to_send_msg, DEFAULT_BOT_PREFIX


class ChatLogic(IChat):
    """
    Описывает все отношения пользователей в чате беседы с ботом.
    Существует пока есть очередь, либо кто-то недописал команды (уязвимость).
    """
    CHAT_ID_PREFIX: Final = 2000000000

    def show_queue(self):
        if self._queue_list_message_id is not None:
            self._bot.remove_message_from_chat(message_id=self._queue_list_message_id,
                                               chat_id=self._chat_id)
            self._queue_list_message_id = None
        if self._queue_contr is None:
            raise Exception("Нету очереди для вывода")
        queue = self._queue_contr.get_queue_as_list
        message = f"В очереди: {len(self._queue_contr.get_queue_as_list)} человек\n"
        for i, user in enumerate(queue):
            message += f"{i+1} — @id{user.user_id}\n"
        message += f'----------------------------\n' \
                   f'{self._bot_prefix}q j — чтобы войти следующим!'
        values = {"random_id": time_ns(),
                  "peer_ids": [self.CHAT_ID_PREFIX + self._chat_id],
                  "message": message,
                  "intent": "default"}
        result = self._bot.send_msg_packed_by_json(values)
        if type(result) is list:
            if len(result) > 0:
                result = result[0]
        response = None
        if type(result) is dict:
            response = result.get('response', None)
        # result = self._vk.method(method="messages.send", values=values)
        if type(response) is list:
            if len(response) > 0:
                response = response[0]
        if type(response) is dict:
            print(response)
            conversation_message_id = response.get("conversation_message_id", None)
            if conversation_message_id is None:
                print(self.__class__.__name__, inspect.currentframe().f_code.co_name, "Непредвиденная ситуация")
                return
            conversation_message_id = int(conversation_message_id)
            self._queue_list_message_id = conversation_message_id

    def user_wants_to_force_next_queue(self, user: ChatUser) -> ChatUser | None:
        if user.is_able_to_create_queue:
            if self.__queue_state == self._QueueState.queue_in_progress:
                queue = self._queue_contr.get_queue_as_list
                if not self._queue_contr.empty:
                    return self._queue_contr.pop()
        return None

    class _QueueState(Enum):
        no_queue_running = auto()
        queue_will_start = auto(),
        queue_in_progress = auto(),
        queue_will_end = auto()

    def __init__(self, bot: IBot, chat_id: int):
        self._queue_list_message_id: int | None = None
        self._bot = bot
        self._chat_id = chat_id

        self.__relations_in_chat: [int, RelationshipInChat] = dict()

        self._queue_contr: AllQueueController | None = None
        self.__queue_state = self._QueueState.no_queue_running
        self._bot_prefix = DEFAULT_BOT_PREFIX
        # self.__queue: Queue[ChatUser] | None = None

    def get_relationship_with_user(self, user_id: int) -> RelationshipInChat | None:
        return self.__relations_in_chat.get(user_id, None)

    def start_relationship_with_user(self, user_id: int) -> RelationshipInChat:
        r = self.__relations_in_chat.get(user_id, None)
        if r is None:
            user = ChatUser.load_user(user_id=user_id, chat_id=self._chat_id)
            r = RelationshipInChat(self._bot, user=user, chat=self)
            self.__relations_in_chat[user_id] = r
        return r

    def user_wants_to_create_queue(self, user_id: int):
        user = ChatUser.load_user(chat_id=self._chat_id, user_id=user_id)
        if user.is_able_to_create_queue:
            qs = self.__queue_state
            match qs:
                case qs.no_queue_running:
                    self.__send_message("Создаём очередь.")
                    self._create_queue()
                case _:
                    self.__send_message("Очередь уже создана!")
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

        if self._queue_contr is None:
            return
        queue_arr = list(self._queue_contr.get_queue_as_list)
        if user in queue_arr:
            return None
        pos = self._queue_contr.put(user)
        if pos is None:
            # self.__send_message("Ты уже стоишь в очереди!") # Уже отписал
            return None
        return pos

    def _create_queue(self):
        self.__queue_state = self._QueueState.queue_will_start
        self._queue_contr = AllQueueController(self._chat_id)
        self.__queue_state = self._QueueState.queue_in_progress

    def peek_next_on_queue(self, offset: int = 0) -> ChatUser | None:
        if self.__queue_state != self._QueueState.queue_in_progress:
            return None
        if self._queue_contr is None:
            return None
        queue_arr: list[ChatUser] = self._queue_contr.get_queue_as_list
        if len(queue_arr) < offset + 1:
            return None
        return queue_arr[offset]

    @property
    def chat_id(self):
        return self._chat_id

    @property
    def is_queue_running(self) -> bool:
        return True if self.__queue_state == self._QueueState.queue_in_progress else False

    def __send_message(self, messsage: str):
        self._bot.write_msg_to_chat(self._chat_id, messsage)

    def send_queue_list(self) -> None:
        """
        Отправляет в чат беседы очередь.
        """
        if self._queue_contr is None:
            return
        msg = "Очередь:"
        arr: list[ChatUser] = list(self._queue_contr.get_queue_as_list)
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
        pipeline_to_send_msg.put_nowait((self._chat_id, message, False))
        pass

    def get_queue(self) -> AllQueueController | None:
        return self._queue_contr

    def switch(self, pos1: int, pos2: int) -> bool:
        return self._queue_contr.switch(pos1, pos2)
