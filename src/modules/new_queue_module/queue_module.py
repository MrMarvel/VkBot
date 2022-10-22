from typing import Final, List

from vk_api.bot_longpoll import VkBotMessageEvent
from vk_api.utils import get_random_id
from vk_api.vk_api import VkApiMethod

from src.event_manager import EventListener, Event, EventType, EventManager
from src.utils.global_bot_i import IGlobalBot
from src.modules.dao_module.src.DAO import DAO
from src.utils.module import Module


class NewQueueModule(Module, EventListener):
    CHAT_ID_PREFIX: Final = 2000000000

    def react_to_event(self, e: Event) -> bool:
        if e.event_type == EventType.GOT_MESSAGE_FROM_PUBLIC_CHAT:
            if type(e.context) is VkBotMessageEvent:
                context: VkBotMessageEvent = e.context
                message = dict(context.message)
                got_from_id: int = message.get("from_id", 0)
                message_text: str = message.get("text", "")
                chat_id: int = context.chat_id


                create_alias = ['создать очередь', 'создание очереди', 'create queue', 'qc', 'cq',
                                'очередь появись', 'queue init', 'queue initialization']
                show_queue_alias = ['вывод очереди', 'очередь', 'текущая очередь']
                delete_queue_alias = ['удаление очереди', 'delete queue', 'remove queue', 'clear queue',
                                      'очистить очередь', 'очистка очереди']
                join_queue_alias = ['Встать в очередь', 'join', 'j', 'занять очередь']
                if message_text in create_alias:
                    self.user_wants_to_create_queue(chat_id)
                    return True
                if message_text in show_queue_alias:
                    self.user_wants_to_show_queue(chat_id)
                    return True
                if message_text in delete_queue_alias:
                    self.user_wants_to_close_queue(chat_id)
                    return True
                if message_text in join_queue_alias:
                    self.user_wants_to_join_queue(chat_id)
                    return True
                if message_text.startswith("!"):
                    split = message_text.split(" ")
                    cmd = split[0]
                    cmd_args = split[1:]
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
                                            self.__send_message(
                                                f"Теперь у меня новый префикс \"{self.__bot_prefix}\" для "
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
                                    return
                                elif sub_cmd in ("switch", "sw", "swtch"):
                                    if not self.is_queue_running:
                                        self.__send_message(
                                            f"Нету очереди. Чтобы создать очередь {self.__bot_prefix}q create")
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
                                            self.__send_message(
                                                f"Нет столько людей в очереди сколько указали вы позиций! "
                                                f"{max(pos1, pos2)}")
                                            return
                                        self.__send_message(f"Были успешно поменяны местами {pos1} и {pos2}!")
                                        self.user_wants_to_show_queue()
                                    return
                                else:
                                    self.__send_message(
                                        f"Ожидалось create|new, join|j, skip|sk, next, но получил {sub_cmd}.")
                            elif self.is_queue_running:
                                self.user_wants_to_show_queue()
                            else:
                                self.__send_message(f"Нету очереди. Чтобы создать очередь {self.__bot_prefix}q create")
                                # self.__chat.send_queue_list()
                            return

                    self.__send_idk_msg_to_chat()  # Не одна команда не сработала
                    return

        return True

    def __init__(self, gb: IGlobalBot):
        super().__init__()
        self._queues: List[int] = list()
        self._app = None
        self._gb = gb
        self._vk_api: VkApiMethod | None = None
        self._DAO: DAO | None = None

    @property
    def name(self) -> str:
        return "NewQueueModule"

    def module_will_load(self):
        self._vk_api = self._gb.vk.get_api()
        self._DAO = DAO()
        event_manager: EventManager = self._gb.get_event_manager()
        event_manager.register_event_listener(self, EventType.GOT_MESSAGE_FROM_PUBLIC_CHAT)

    def module_will_unload(self):
        event_manager: EventManager = self._gb.get_event_manager()
        event_manager.unregister_event_listener(self, EventType.GOT_MESSAGE_FROM_PUBLIC_CHAT)

    def module_infinite_run(self):
        pass

    def send_msg(self, chat_id, msg):
        self._vk_api.messages.send(peers_id=[NewQueueModule.CHAT_ID_PREFIX + chat_id],
                                   message=msg,
                                   random_id=get_random_id())

    def user_wants_to_create_queue(self, chat_id: int):
        if chat_id in self._queues:
            self.send_msg(chat_id=chat_id, msg="Очеред уже создана")

        self.q

    def user_wants_to_show_queue(self, chat_id: int):
        pass