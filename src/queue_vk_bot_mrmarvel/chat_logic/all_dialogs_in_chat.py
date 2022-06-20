import inspect
import json
import warnings
from time import time_ns
from typing import Final

from deprecated.classic import deprecated

from ..bot.bot_i import IBot
from ..chat_logic.all_dialogs_in_chats_i import IAllDialogInChatsController
from ..queue.queue_controller import QueueControllerInChat
from ..utils.chat_user import ChatUser, User
from ..chat_logic.dialog_in_chat import DialogInChat
from ..gl_vars import pipeline_to_send_msg, DEFAULT_BOT_PREFIX


class AllDialogsInChatsLogic(IAllDialogInChatsController):
    """
    Описывает все отношения пользователей в чате беседы с ботом.
    Существует пока есть очередь, либо кто-то недописал команды (уязвимость).
    """


    CHAT_ID_PREFIX: Final = 2000000000

    @deprecated
    def user_wants_to_force_next_queue(self, user: ChatUser) -> ChatUser | None:
        if user.is_able_to_create_queue:
            chat_id = user.chat_id
            queue_model = self.get_queue(chat_id).model
            if queue_model is not None:
                return queue_model.pop()
        return None

    def __init__(self, bot: IBot, chat_id: int):
        self._bot = bot
        self._chat_id = chat_id

        self.__relations_in_chat: [int, DialogInChat] = dict()

        self._bot_prefix = DEFAULT_BOT_PREFIX
        # self.__queue: Queue[ChatUser] | None = None

    def get_relationship_with_user(self, user_id: int) -> DialogInChat | None:
        return self.__relations_in_chat.get(user_id, None)

    def start_relationship_with_user(self, user_id: int) -> DialogInChat:
        r = self.__relations_in_chat.get(user_id, None)
        if r is None:
            user = ChatUser.load_user(user_id=user_id, chat_id=self._chat_id)
            r = DialogInChat(self._bot, chating_with_user=user, in_chat_id=self._chat_id,
                             all_dialogs_in_chats_controller=self)
            self.__relations_in_chat[user_id] = r
        return r

    @deprecated
    def user_wants_to_join_to_queue(self, user: ChatUser) -> int | None:
        """
        Пользователь требует добавить его в очередь
        :param user: Пользователь
        :return: Номер позиции в очереди (от 1), Вернёт None если уже в очереди
        """
        warnings.warn("deprecated", DeprecationWarning)
        chat_id = user.chat_id
        queue_model = self.get_queue(chat_id)
        if queue_model is None:
            self.__send_message("Очередь не начата")
            return

        pos = queue_model.push(user)
        if pos is None:
            self.__send_message("Ты уже стоишь в очереди!")
        return pos

    def __send_message(self, messsage: str):
        self._bot.write_msg_to_chat(self._chat_id, messsage)

    @deprecated
    def send_queue_list(self) -> None:
        """
        Отправляет в чат беседы очередь.
        """
        warnings.warn("deprecated", DeprecationWarning)
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

    def switch(self, pos1: int, pos2: int) -> bool:
        warnings.warn("deprecated", DeprecationWarning)
        return self._queue_contr.switch(pos1, pos2)
