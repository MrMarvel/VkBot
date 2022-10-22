import os
from threading import Thread

from vk_api import VkApi
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

from command import CommandManager
from event_manager import EventManager, GotMessageFromPublicChatEvent
from module_controller import ModuleController
from utils.global_bot_i import IGlobalBot
from modules.fancy_old_queue_module.src.queue_vk_bot_mrmarvel.app import FancyOldQueueModule


def long_poll_loop_listen(vk: VkApi, group_id: int, em: EventManager):
    print("Цикл чтение лонг полла запущен!")
    # Работа с сообщениями из бесед от имени ГРУППЫ
    longpoll_chat = VkBotLongPoll(vk, group_id=group_id)
    # Основной цикл
    for event in longpoll_chat.listen():
        # Если пришло новое сообщение
        if event.type == VkBotEventType.MESSAGE_NEW:

            # Если оно имеет метку для меня( то есть бота)
            if event.from_chat:
                em.register_event(GotMessageFromPublicChatEvent(event))


class VkListener:
    def _auth(self, token):
        self._vk = VkApi(token=token)

    def __init__(self, t, gid, em: EventManager):
        self._vk: VkApi | None = None
        self._token = t
        self._group_id = gid
        self._em = em
        self._auth(token=self._token)
        self._thread = Thread(target=long_poll_loop_listen, args=(self._vk, self._group_id, self._em), daemon=True)
        self._thread.start()

    def join(self):
        self._thread.join()


class GlobalBot(IGlobalBot):
    """
    Основной класс
    """
    def get_event_manager(self):
        """
        Получение менеджера событий
        """
        return self._em

    def get_command_manager(self):
        """
        Получение менеджера комманд
        """
        return self._cm

    @property
    def vk(self) -> VkApi:
        """
        Получение ВК API
        """
        return self._vk

    def __init__(self):
        """
        Запуск бота через конструктор!
        """
        self._token: str | None = os.environ.get('TOKEN')
        self._bot_group_id: int | None = os.environ.get('BOT_GROUP_ID')

        if self._token is None:
            raise Exception("TOKEN is not in environment!")
        if self._bot_group_id is None:
            raise Exception("BOT_GROUP_ID is not in environment!")
        self._vk = VkApi(token=self._token)
        self._em = EventManager()
        self._cm = CommandManager(self)

        module_controller = ModuleController()
        # module_controller.start_module(NewQueueModule(self))
        module_controller.start_module(FancyOldQueueModule())

        listener = VkListener(self._token, self._bot_group_id, self._em)

        module_controller.join()
        listener.join()

        self._em.unregister_all_event_listeners()
        module_controller.destroy_modules()


if __name__ == '__main__':
    bot = GlobalBot()
