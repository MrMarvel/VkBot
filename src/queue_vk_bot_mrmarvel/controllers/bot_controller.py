import time
from threading import Thread
from typing import Final

from vk_api import VkApi
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType, VkBotMessageEvent
from vk_api.longpoll import VkLongPoll, VkEventType, Event

from ..chat_logic.relationship_list_in_chat import ChatLogic
from ..controllers.queue_controller import QueueController
from ..controllers.request_controller import RequestController
from ..gl_vars import relationships_in_chats, relationships_in_ls, pipeline_to_send_msg
from ..chat_logic.relationship_in_ls import RelationshipInLS
from ..utils.bot_i import IBot
from deprecated import deprecated


@deprecated
def write_msg_to_user(vk, user_id, message):
    """
    Send message to VK user
    :param vk: API session
    :param user_id: ID ВК пользователя
    :param message: String of message to send
    :return:
    """
    msg = {'user_id': user_id, 'message': message, 'random_id': time.time_ns()}
    send_msg_packed_by_json(vk, msg)


@deprecated
def write_msg_to_chat(vk, chat_id, message) -> None:
    """
    DEPRECATED
    Send message to VK user
    :param vk: API session
    :param chat_id: ID ВК чата
    :param message: String of message to send
    """
    msg = {'chat_id': chat_id, 'message': message, 'random_id': time.time_ns()}
    send_msg_packed_by_json(vk, msg)


@deprecated
def send_msg_packed_by_json(vk, message_json) -> None:
    """
    DEPRECATED
    Send message to VK user
    :param vk: API session
    :param message_json: JSON сообщения
    """
    message_json['random_id'] = time.time_ns()

    # vk.method('messages.send', message_json)


def write_msg(vk, deliver_id, message, is_private: bool = True):
    """
    DEPRECATED
    Send message to VK user
    :param vk: API session
    :param deliver_id: ID ВК чата или пользователя
    :param message: String of message to send
    :param is_private: 1 - личный чат 0 - беседа
    :return:
    """
    if is_private:
        write_msg_to_user(vk=vk, user_id=deliver_id, message=message)
    else:
        write_msg_to_chat(vk=vk, chat_id=deliver_id, message=message)


def init_connection(token) -> VkApi | None:
    """
    TODO
    :param token:
    :return:
    """
    return None


class BotController(IBot):
    CHAT_ID_PREFIX: Final = 2000000000

    def __init__(self, vk: VkApi, bot_group_id: int):
        self._vk = vk
        self._bot_group_id = bot_group_id
        self._request_contr = RequestController(self, vk, bot_group_id)
        self._request_contr.start()

    def start(self):
        thread_chats = Thread(target=self.run_cycle_on_chats, args=(), daemon=True)
        thread_chats.start()
        thread_ls = Thread(target=self.run_cycle_on_ls, args=(), daemon=True)
        thread_ls.start()
        thread_ls.join()

    def create_queue_in_chat(self, chat_id) -> None:
        """
        TODO
        :param chat_id:
        :return:
        """
        raise NotImplementedError
        pass

    def show_next_in_queue_in_chat(self):
        pass

    def get_queue_from_chat(self, chat_id) -> QueueController | None:
        """
        TODO
        :param chat_id:
        :return:
        """
        raise NotImplementedError
        pass

    def write_msg_to_user(self, user_id, message) -> None:
        """
        Send message to VK user
        :param user_id: ID ВК пользователя
        :param message: String of message to send
        :return:
        """
        msg = {'user_id': user_id, 'message': message, 'random_id': time.time_ns()}
        send_msg_packed_by_json(self._vk, msg)

    def write_msg_to_chat(self, chat_id, message) -> None:
        """
        Send message to VK user
        :param chat_id: ID ВК чата
        :param message: String of message to send
        """
        msg = {'chat_id': chat_id, 'message': message, 'random_id': time.time_ns()}
        self.send_msg_packed_by_json(msg)

    def send_msg_packed_by_json(self, message_json) -> dict | None:
        """
        Send message to VK user
        :param message_json: JSON сообщения
        """
        message_json['random_id'] = time.time_ns()
        message_json['v'] = '5.131'
        request_method = 'messages.send'
        return self._send_request({'method': request_method, 'body': message_json})
        # return self._request_contr.got_to_send_request({'method': request_method, 'body': message_json})
        # self._vk.method('messages.send', message_json)

    def _send_request(self, request: dict) -> dict | None:
        """
        Отправляет запросы в ВК.
        :param request:
        :return:
        """
        return self._request_contr.got_to_send_request(request=request)

    def remove_messages_from_chat(self, message_ids: list[int], chat_id: int) -> dict | None:
        body = {"peer_id": self.CHAT_ID_PREFIX + 1,
                "cmids": ','.join(map(lambda x: str(x), message_ids)),
                "delete_for_all": 1}
        method = "messages.delete"
        return self._send_request({"method": method, "body": body})

    def remove_message_from_chat(self, message_id: int, chat_id: int) -> dict | None:
        return self.remove_messages_from_chat([message_id], chat_id)

    def write_msg(self, deliver_id, message, is_private: bool = True):
        """
        Send message to VK user
        :param deliver_id: ID ВК чата или пользователя
        :param message: String of message to send
        :param is_private: 1 - личный чат 0 - беседа
        :return:
        """
        if is_private:
            write_msg_to_user(vk=self._vk, user_id=deliver_id, message=message)
        else:
            write_msg_to_chat(vk=self._vk, chat_id=deliver_id, message=message)

    def run_cycle_on_chats(self) -> None:
        """
        Один из основных циклов программы.
        Обрабатывает сообщения из бесед.
        :returns:
        """
        print("Main logic cycle for chats is running!")

        try:
            # Работа с сообщениями из бесед от имени ГРУППЫ
            longpoll_chat = VkBotLongPoll(self._vk, group_id=self._bot_group_id)
            # Основной цикл
            for event in longpoll_chat.listen():

                # Если пришло новое сообщение
                if event.type == VkBotEventType.MESSAGE_NEW:

                    # Если оно имеет метку для меня( то есть бота)
                    if event.from_chat:
                        self.got_msg_from_user_to_bot_in_chat(chat_msg_event=event)
        except Exception as e:
            print(e)
            raise e
        finally:
            print("Main logic cycle for chats stopped working!")

    def run_cycle_on_ls(self) -> None:
        """
        Один из основных циклов программы.
        Обрабатывает сообщения из ЛС.
        """
        print("Main logic cycle for Personal Messages(LS) is running!")
        try:
            # Работа с сообщениями из ЛС
            longpoll_ls = VkLongPoll(self._vk)
            # Основной цикл
            for event in longpoll_ls.listen():

                # Если пришло новое сообщение
                if event.type == VkEventType.MESSAGE_NEW:

                    # Если оно имеет метку для меня( то есть бота)
                    if event.to_me:
                        self.got_msg_from_user_to_bot_in_ls(vk=self._vk, ls_msg_event=event)
        except Exception as e:
            print(e)
            raise e
        finally:
            print("Main logic cycle for Personal Messages(LS) stopped working!")

    def got_msg_from_user_to_bot_in_chat(self, chat_msg_event: VkBotMessageEvent) -> None:
        """
        Среагировать на полученное сообщение от пользователя.
        :param chat_msg_event: Событие сообщения из беседы
        """
        # Сообщение от пользователя
        request = str(chat_msg_event.message.get("text"))
        in_msg = request.lower()  # Нечувствительность к регистру
        chat_id = chat_msg_event.chat_id
        user_id = chat_msg_event.message.get("from_id")

        chat_logic = relationships_in_chats.get(chat_id, None)
        if chat_logic is None:
            chat_logic = ChatLogic(self, chat_id=chat_id)
            relationships_in_chats[chat_id] = chat_logic

        relation = chat_logic.get_relationship_with_user(user_id)
        # user = ChatUser.load_user(chat_id=chat_id, user_id=user_id)
        if relation is None:
            relation = chat_logic.start_relationship_with_user(user_id=user_id)

        relation.react_to_msg_from_chat(msg=in_msg)

    def got_msg_from_user_to_bot_in_ls(self, ls_msg_event: Event) -> None:
        """
        Среагировать на полученное сообщение от пользователя.
        :param ls_msg_event: Событие сообщения из ЛС.
        """
        # Сообщение от пользователя
        request = str(ls_msg_event.text)
        in_msg = request.lower()  # Нечувствительность к регистру
        user_id = ls_msg_event.user_id
        relation = relationships_in_ls.get(user_id, None)
        if relation is None:
            relation = RelationshipInLS(user_id=user_id, pipeline_to_send_msg=pipeline_to_send_msg)
            relationships_in_ls[user_id] = relation
        relation.react_to_msg_from_ls(msg=in_msg)
