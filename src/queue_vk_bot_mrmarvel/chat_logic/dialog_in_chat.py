import random
from enum import Enum, auto
from typing import Final

from ..queue.queue_controller import QueueControllerInChat
from ..chat_logic.all_dialogs_in_chats_i import IAllDialogInChatsController
from ..utils.chat_user import ChatUser, Permission
from ..gl_vars import DEFAULT_BOT_PREFIX
from ..bot.bot_i import IBot, permission


class DialogInChat:
    """
    Подконтроллер Контроллера бота. 1 отношение на 1 команду пользователя
    Отношение пользователя с ботом, описывает состояния поведения в чатах.
    По сути автомат.
    """

    class _CommunicationState(Enum):
        will_start_communicate = auto(),
        after_start_message_printed = auto(),
        queue_in_chat_and_will_start_communicate = auto(),
        communication_will_end = auto(),

    def __init__(self, bot: IBot, all_dialogs_in_chats_controller: IAllDialogInChatsController,
                 chating_with_user: ChatUser, in_chat_id: int):
        self._bot = bot
        self._all_dialogs_in_chats_controller: IAllDialogInChatsController = all_dialogs_in_chats_controller
        self._user: ChatUser = chating_with_user
        self._chat_id: int = in_chat_id

        self._queue_contr = self._bot.get_queue_from_chat(chat_id=self._chat_id)
        self.__user_id: Final = chating_with_user.user_id
        self.__state = self._CommunicationState.will_start_communicate
        self.__bot_prefix = DEFAULT_BOT_PREFIX
        self.__user_cmds: list[int] = list()

    @property
    def is_queue_running(self):
        return self._queue_contr is not None

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
        create_alias = ['создать очередь', 'создание очереди', 'create queue', 'qc', 'cq',
                        'очередь появись', 'queue init', 'queue initialization']
        show_queue_alias = ['вывод очереди', 'очередь', 'текущая очередь']
        delete_queue_alias = ['удаление очереди', 'delete queue', 'remove queue', 'clear queue', 'очистить очередь',
                              'очистка очереди']
        join_queue_alias = ['Встать в очередь', 'join/j', 'занять очередь']
        if msg in create_alias:
            self.user_wants_to_create_queue()
            return
        if msg in show_queue_alias:
            self.user_wants_to_show_queue()
            return
        if msg in delete_queue_alias:
            self.user_wants_to_close_queue()
        if msg in join_queue_alias:
            self.user_wants_to_join_queue()
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
                if cmd == "queue" or cmd == "q":
                    if len(cmd_args) > 1:
                        sub_cmd = cmd_args[1]
                        if sub_cmd == "create" or sub_cmd == "new":
                            self.user_wants_to_create_queue()

                        elif sub_cmd == "join" or sub_cmd == "j":
                            self.user_wants_to_join_queue()

                        elif sub_cmd in ("skip", "sk", "skp"):
                            # Следующий по очереди
                            self.user_wants_to_force_skip()
                        elif sub_cmd in ("close", "cl"):
                            self.user_wants_to_close_queue()
                            return
                        elif sub_cmd in ("next", "nxt"):
                            self.__send_message("Автор ещё не реализовал эту фичу!")
                            # TODO
                            return
                        elif sub_cmd in ("switch", "sw", "swtch"):
                            if not self.is_queue_running:
                                self.__send_message(f"Нету очереди. Чтобы создать очередь {self.__bot_prefix}q create")
                            if len(cmd_args) > 3:
                                pos1 = int(cmd_args[2])
                                pos2 = int(cmd_args[3])
                                # if type(pos1) is not int:
                                #     self.__send_message(f"{pos1} не число!")
                                #     return
                                # if type(pos2) is not int:
                                #     self.__send_message(f"{pos2} не число!")
                                #     return
                                if not self._all_dialogs_in_chats_controller.switch(pos1 - 1, pos2 - 1):
                                    self.__send_message(f"Нет столько людей в очереди сколько указали вы позиций! "
                                                        f"{max(pos1, pos2)}")
                                    return
                                self.__send_message(f"Были успешно поменяны местами {pos1} и {pos2}!")
                                self.user_wants_to_show_queue()
                            return
                        else:
                            self.__send_message(f"Ожидалось create|new, join|j, skip|sk, next, но получил {sub_cmd}.")
                    elif self.is_queue_running:
                        self.user_wants_to_show_queue()
                    else:
                        self.__send_message(f"Нету очереди. Чтобы создать очередь {self.__bot_prefix}q create")
                        # self.__chat.send_queue_list()
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

    def user_wants_to_force_skip(self):
        if not self._queue_contr:
            return None

        if self._queue_contr is not None:
            user = self._queue_contr.model.pop()
            if user is not None:
                next_user = self._queue_contr.model.get_last()
                if next_user is not None:
                    msg = f"Твоя очередь, @id{next_user.user_id}!"
                    next_user_after_next_user = self._queue_contr.model.get_last(offset=1)
                    if next_user_after_next_user is not None:
                        msg += (f"\n@id{next_user_after_next_user.user_id}, ты идёшь "
                                f"после него.")
                    self.__send_message(msg)
                else:
                    self.__send_message(f"Очередь опустела, чтоб закрыть очередь "
                                        f"{self.__bot_prefix}q close")
            else:
                self.__send_message("Очередь и так пуста!")
        else:
            self.__send_message("Очередь не запущена!")

    def user_wants_to_create_queue(self):
        # user = ChatUser.load_user(chat_id=self._chat_id, user_id=self._user.user_id)
        if self._user.is_able_to_create_queue:
            if self._queue_contr is None:
                self.__send_message("Создаём очередь.")
                self._queue_contr = self._bot.create_queue_in_chat(chat_id=self._chat_id, by_user=self._user)
                self._queue_contr.view.reset_queue_list()
            else:
                self.__send_message("Очередь уже создана!")
        else:
            self.__send_message("Ты не можешь создавать очереди. Попроси того, кто может ;)")

    def user_wants_to_show_queue(self):
        if not self._queue_contr:
            return None
        self._queue_contr.view.reset_queue_list()

    def user_wants_to_join_queue(self):
        if self._queue_contr is not None:
            pos_in_queue = self._queue_contr.model.push(self._user)
            if pos_in_queue is None:
                self.__send_message("Вы уже в очереди!")
            else:
                self.__send_message(f"Вы встали в очередь {pos_in_queue}ым!")
        else:
            self.__send_message("Невозможно подключится к несуществующей очереди!")

    def user_wants_to_close_queue(self):
        if self._user.has_permission(Permission.DESTROY_QUEUE):
            if self._queue_contr is not None:
                self._bot.destroy_queue_in_chat(in_chat_id=self._chat_id, by_user=self._user)
                self._queue_contr = None
                self.__send_message("Прощай очередь!")
            else:
                self.__send_message("Очередь и так нету!")
        else:
            self.__send_message("")

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
        rand_msgs = "К сожелению я не понял, что вы имели ввиду.", \
                    "Мяу?\nА вы поняли, что я имел в виду? Вот и я также вас.", \
                    "Хммм.. даже не знаю что сказать."
        self._bot.write_msg_to_chat(self._chat_id, random.choice(rand_msgs))
        # pipeline_to_send_msg.put_nowait((self.__chat_id, random.choice(rand_msgs), False))

    # def __send_message_to_user(self, msg: str):
    #     pipeline_to_send_msg.put_nowait((self.__user_id, msg, True))

    def __send_message(self, msg: str):
        self.__send_message_to_chat(msg)

    def __send_message_to_chat(self, msg: str):
        self._bot.write_msg_to_chat(self._chat_id, msg)
        # pipeline_to_send_msg.put_nowait((self.__chat_id, msg, False))

