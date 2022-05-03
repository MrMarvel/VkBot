import random
import threading
import time
from typing import Final

from vk_api import VkApi
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType, VkBotMessageEvent
from vk_api.longpoll import VkLongPoll, VkEventType, Event
import os

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
from . import gl_vars
from .chat import ChatLogic
from .chat_user import ChatUser
from .config_operations import load_config
from .gl_vars import pipeline_to_send_msg, token
from .conversation_in_chat import ConversationInChat
from .relationship_in_ls import RelationshipInLS


def print_hi(name: str) -> None:
    """
    Print hello to username
    :param name: Username
    :return:
    """

    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


relationships_in_ls: Final[dict[int, RelationshipInLS]] = dict()  # Состояния общения с пользователями в ЛС
# Состояния общения с пользователями в чатах. {Чат1: {Пользователь1: Отношение, ...}, ...}
relationships_in_chats: Final[dict[int, ChatLogic]] = dict()
MAX_REQUESTS_PER_SECOND: Final = 3


def got_msg_from_user_to_bot_in_chat(vk: VkApi, chat_msg_event: VkBotMessageEvent) -> None:
    """
    Среагировать на полученное сообщение от пользователя.
    :param vk: ВК
    :param chat_msg_event: Событие сообщения из беседы
    """
    # Сообщение от пользователя
    request = str(chat_msg_event.message.get("text"))
    in_msg = request.lower()  # Нечувствительность к регистру
    chat_id = chat_msg_event.chat_id
    user_id = chat_msg_event.message.get("from_id")

    chat_logic = relationships_in_chats.get(chat_id, None)
    if chat_logic is None:
        chat_logic = ChatLogic(chat_id=chat_id)
        relationships_in_chats[chat_id] = chat_logic

    relation = chat_logic.get_relationship_with_user(user_id)
    user = ChatUser.load_user(chat_id=chat_id, user_id=user_id)
    if relation is None:
        relation = chat_logic.start_relationship_with_user(user_id=user_id)

    relation.react_to_msg_from_chat(msg=in_msg)


def got_msg_from_user_to_bot_in_ls(vk: VkApi, ls_msg_event: Event) -> None:
    """
    Среагировать на полученное сообщение от пользователя.
    :param vk: ВК
    :param ls_msg_event: Событие сообщения из лс
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


def run_cycle_on_chats(vk: VkApi) -> None:
    """
    Один из основных циклов программы.
    Обрабатывает сообщения из бесед.
    :param vk: ВК
    """
    print("Main logic cycle for chats is running!")

    try:
        # Работа с сообщениями из бесед от имени ГРУППЫ
        longpoll_chat = VkBotLongPoll(vk, group_id=bot_group_id)
        # Основной цикл
        for event in longpoll_chat.listen():

            # Если пришло новое сообщение
            if event.type == VkBotEventType.MESSAGE_NEW:

                # Если оно имеет метку для меня( то есть бота)
                if event.from_chat:
                    got_msg_from_user_to_bot_in_chat(vk=vk, chat_msg_event=event)
    except Exception as e:
        print(e)
        raise e
    finally:
        print("Main logic cycle for chats stopped working!")


# Press the green button in the gutter to run the script.
def run_cycle_on_ls(vk: VkApi) -> None:
    """
    Один из основных циклов программы.
    Обрабатывает сообщения из ЛС
    :param vk: ВК
    """
    print("Main logic cycle for Personal Messages(LS) is running!")
    try:
        # Работа с сообщениями из ЛС
        longpoll_ls = VkLongPoll(vk)
        # Основной цикл
        for event in longpoll_ls.listen():

            # Если пришло новое сообщение
            if event.type == VkEventType.MESSAGE_NEW:

                # Если оно имеет метку для меня( то есть бота)
                if event.to_me:
                    got_msg_from_user_to_bot_in_ls(vk=vk, ls_msg_event=event)
    except Exception as e:
        print(e)
        raise e
    finally:
        print("Main logic cycle for Personal Messages(LS) stopped working!")


vk: VkApi | None = None


def run_cycle_to_send_msg() -> None:
    print("Sending cycle is running!")
    min_time_to_wait_before_next_request: Final = 0.334

    try:
        while 1:
            id, msg, is_private = pipeline_to_send_msg.get(block=True)
            try:
                if type(msg) is dict:
                    send_msg_packed_by_json(vk=vk, message_json=msg)
                elif type(msg) is str:
                    if is_private:
                        write_msg_to_user(vk=vk, user_id=id, message=msg)
                    else:
                        write_msg_to_chat(vk=vk, chat_id=id, message=msg)
            except Exception as e:
                print(f"ERRORED sending a message\n{vk, id, msg, is_private}")
                print(e)
                break
            time.sleep(min_time_to_wait_before_next_request + random.random() * 0.1)
    finally:
        print("Sending cycle stopped working!")


bot_group_id: int


def run():
    """
    Отправная точка работы программы
    :return:
    """
    print("Absolute path:", os.path.abspath(''))

    print_hi('PyCharm')
    try:
        pass
        load_config()  # DEPRECATION because of Heroku env input
    except FileNotFoundError:
        pass
    if gl_vars.token is None:
        gl_vars.token = os.environ.get('TOKEN')
    global bot_group_id
    bot_group_id = os.environ.get('BOT_GROUP_ID')  # 209160825
    # Авторизуемся как сообщество
    global vk
    vk = VkApi(token=gl_vars.token)
    # Основной цикл
    threading.Thread(target=run_cycle_to_send_msg, daemon=True).start()
    threading.Thread(target=run_cycle_on_chats, args=(vk,), daemon=True).start()
    thread_ls = threading.Thread(target=run_cycle_on_ls, args=(vk,), daemon=True)
    thread_ls.start()
    thread_ls.join()
    print("Main program is finished!")


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


def write_msg_to_chat(vk, chat_id, message) -> None:
    """
    Send message to VK user
    :param vk: API session
    :param chat_id: ID ВК чата
    :param message: String of message to send
    """
    msg = {'chat_id': chat_id, 'message': message, 'random_id': time.time_ns()}
    send_msg_packed_by_json(vk, msg)


def send_msg_packed_by_json(vk, message_json) -> None:
    """
    Send message to VK user
    :param vk: API session
    :param message_json: JSON сообщения
    """
    message_json['random_id'] = time.time_ns()
    vk.method('messages.send', message_json)


def write_msg(vk, deliver_id, message, is_private: bool = True):
    """
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
