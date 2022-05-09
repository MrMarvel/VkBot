import random
from enum import Enum, auto
from queue import Queue
from typing import Final

from .gl_vars import DEFAULT_BOT_PREFIX, pipeline_to_send_msg


class RelationshipInLS:
    """
    Отношение пользователя с ботом, описывает состояния поведения в личных сообщениях.
    По сути автомат.
    """

    class _CommunicationState(Enum):
        not_started_communitaction = auto(),
        after_start_message_printed = auto(),

    def __init__(self, user_id: int, pipeline_to_send_msg: Queue[tuple[int, str, bool]]):
        self.__user_id: Final = user_id
        self.__state = self._CommunicationState.not_started_communitaction
        self.__last_chat_id: int | None = None
        self.__pipeline_to_send_msg = pipeline_to_send_msg

    def is_useless(self) -> bool:
        return False

    def react_to_msg_from_ls(self, msg: str, from_chat: int | None = None) -> None:
        """

        :param msg: Полученное сообщение из ЛС
        :param from_chat:
        :return:
        """
        state = self.__state
        if msg.startswith(DEFAULT_BOT_PREFIX):
            # Это команда
            cmd_args = msg[1:].split(sep=' ')
            if len(cmd_args) > 0:
                cmd = cmd_args[0]
                if cmd == "start":
                    if from_chat is None:
                        self.__send_welcome_msg_to_user()
                    else:
                        self.__send_welcome_msg_to_user()
        match state:
            case state.not_started_communitaction:
                pass
            case state.after_start_message_printed:
                pass
            case _:
                pass
        if "начать" in msg or \
                "что ты умеешь" in msg or \
                "нач" in msg or \
                "прив" in msg:
            self.__send_welcome_msg_to_user()
            state = state.after_start_message_printed
            return

        self.__send_idk_msg_to_place()  # Не одна команда не сработала
        return

    def __send_cap_msg(self) -> None:
        """
        Заглушка сообщение
        """
        self.__send_message_to_user(msg="ЗАГЛУШКА")

    def __send_welcome_msg_to_user(self) -> None:
        """
        Личное сообщение
        """
        msg = "Привет!\n" \
              "Я бот EzQueue — как и понятно из названия, я умею создавать для вас и ваших друзей очереди!\n" \
              "Но также я могу оповещать вашу учебную группу о новостях, которые сможет отправлять староста " \
              "с нашего удобного десктопного приложения!\n" \
              "Для того, начать чтобы помогать вам с друзьями создавать очереди в беседах, мне потребуется быть в " \
              "вашей беседе.\n "
        self.__send_message_to_user(msg=msg)

    def __send_welcome_msg_to_chat(self) -> None:
        """
        Сообщение для беседы
        """
        msg = "Привет!\n" \
              "Я бот EzQueue — как и понятно из названия, я умею создавать для вас и ваших друзей очереди!\n" \
              "Но также я могу оповещать вашу учебную группу о новостях, которые сможет отправлять староста " \
              "с нашего удобного десктопного приложения!\n" \
              "Для того, начать чтобы помогать вам с друзьями создавать очереди в беседах, мне потребуется быть " \
              "добавленным в вашу беседе.\n" \
              "Помимо этого потребуются права на чтение и отправку сообщений."
        self.__send

    def __send_idk_msg_to_place(self, is_private: bool = True) -> None:
        """
        Общее сообщение
        """
        rand_msgs = "К сожелению я не понял, что вы имели ввиду конкретно.", \
                    "Мяу?\nА вы поняли, что я имел в виду? Вот и я также вас.", \
                    "Хммм.. даже не знаю что сказать."
        pipeline_to_send_msg.put_nowait((self.__user_id if is_private else self.__last_chat_id,
                                         random.choice(rand_msgs), is_private))

    def __send_message_to_user(self, msg: str):
        pipeline_to_send_msg.put_nowait((self.__user_id, msg, True))

    def __send_message_to_chat(self, msg: str):
        pipeline_to_send_msg.put_nowait()
