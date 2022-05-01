import random
from enum import Enum, auto
from queue import Queue
from typing import Final

from .gl_vars import DEFAULT_BOT_PREFIX, pipeline_to_send_msg


class RelationshipInChat:
    """
    Отношение пользователя с ботом, описывает состояния поведения в чатах.
    По сути автомат.
    """

    class _CommunicationState(Enum):
        will_start_communicate = auto(),
        after_start_message_printed = auto(),

    def __init__(self, user_id: int, chat_id: int):
        self.__user_id: Final = user_id
        self.__state = self._CommunicationState.will_start_communicate
        self.__chat_id: int | None = chat_id
        self.__bot_prefix = DEFAULT_BOT_PREFIX

    @property
    def bot_prefix(self):
        return self.__bot_prefix

    @bot_prefix.setter
    def bot_prefix(self, new_prefix):
        if len(new_prefix) == 1:
            self.__bot_prefix = new_prefix

    def change_prefix(self, new_prefix: str):  # DEPRECATION у отношений не должно быть зависимости от ДОЛГОЙ истории
        self.bot_prefix = new_prefix

    def react_to_msg_from_chat(self, msg: str) -> None:
        """

        :param msg: Полученное сообщение из чата
        :param msg:
        :return:
        """
        state = self.__state
        if msg.startswith(self.__bot_prefix):
            # Это команда
            clear_msg = msg.removeprefix(self.__bot_prefix)  # Сообщение без префикса
            cmd_args = clear_msg.split(sep=' ')
            if len(cmd_args) > 0:
                cmd = cmd_args[0]
                if cmd == "start":
                    self.__send_welcome_msg_to_chat()
                    return
                if cmd == "help":
                    self.__send_cmd_help()
                    return
                if cmd == "prefix" or cmd == "pr":
                    if len(cmd_args) > 1:
                        sub_cmd = cmd_args[1]
                        if sub_cmd == "change" or sub_cmd == "ch":
                            if len(cmd_args) > 2:
                                new_prefix = cmd_args[2]
                                if len(new_prefix) == 1:
                                    self.change_prefix(new_prefix=new_prefix)
                                    self.__send_message(f"Теперь у меня новый префикс \"{self.__bot_prefix}\" для "
                                                        f"команд!")
                                else:
                                    self.__send_message(f"Префикс \"{new_prefix}\" слишком длинный")
                            else:
                                self.__send_message("Не указан префикс.")
                    else:
                        self.__send_message(f"Текущий установленный префикс \"{self.__bot_prefix}\".\n"
                                            f"Доступны следующий суб-команды:\n"
                                            f"change {{новый префикс}}")
                    return

            self.__send_idk_msg_to_chat()  # Не одна команда не сработала
            return
        match state:
            case state.will_start_communicate:
                pass
            case state.after_start_message_printed:
                pass
            case _:
                pass

    def __send_cap_msg(self) -> None:
        """
        Заглушка сообщение
        """
        self.__send_message(msg="ЗАГЛУШКА")

    def __send_cmd_help(self) -> None:
        p = self.__bot_prefix
        msg = f"{p}help - помощь по командам\n" \
              f"{p}start - начальное сообщение\n" \
              f"{p}prefix {p}pr - управление префиксом команд"
        self.__send_message(msg=msg)

    def __send_welcome_msg_to_chat(self) -> None:
        """
        Сообщение для беседы
        """
        msg = "Привет!\n" \
              "Я бот EzQueue — как и понятно из названия, я умею создавать для вас и ваших друзей очереди!\n" \
              "Но также я могу оповещать вашу учебную группу о новостях, которые сможет отправлять староста " \
              "с нашего удобного десктопного приложения!\n"
        self.__send_message_to_chat(msg)

    def __send_idk_msg_to_chat(self) -> None:
        """
        Общее сообщение
        """
        rand_msgs = "К сожелению я не понял, что вы имели ввиду конкретно.", \
                    "Мяу?\nА вы поняли, что я имел в виду? Вот и я также вас.", \
                    "Хммм.. даже не знаю что сказать."
        pipeline_to_send_msg.put_nowait((self.__chat_id, random.choice(rand_msgs), False))

    # def __send_message_to_user(self, msg: str):
    #     pipeline_to_send_msg.put_nowait((self.__user_id, msg, True))

    def __send_message(self, msg: str):
        self.__send_message_to_chat(msg)

    def __send_message_to_chat(self, msg: str):
        pipeline_to_send_msg.put_nowait((self.__chat_id, msg, False))
