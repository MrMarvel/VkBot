import configparser as cp
import random
import time

import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import os

from .book import *


# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


def print_hi(name: str) -> None:
    """
    Print hello to username
    :param name: Username
    :return:
    """

    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


def prepare_config() -> None:
    """
    Prepare config before loading.
    Adding default values instead of leak of them.
    :return:
    """

    config = cp.ConfigParser()
    config.read(CONFIG_FILENAME)

    api_label = 'API'
    if not config.has_section(api_label):
        config.add_section(api_label)
    api = config[api_label]
    if 'api_token' not in api:
        # noinspection SpellCheckingInspection
        api['api_token'] = "6a9c267cd469388709a9e9acaddbe0aa81a0abbf12239b3e597a31729ffbddb9c88e80a443554c918b8f7"

    with open(CONFIG_FILENAME, 'w') as configfile:
        config.write(configfile)


# noinspection SpellCheckingInspection
# API-ключ созданный ранее
token = "6a9c267cd469388709a9e9acaddbe0aa81a0abbf12239b3e597a31729ffbddb9c88e80a443554c918b8f7"


def load_config() -> None:
    """
    Load main config
    :return:
    """

    global token
    prepare_config()
    config = cp.ConfigParser()
    config.read(CONFIG_FILENAME)
    token = config['API'].get('api_token')


CONFIG_FILENAME = "data/config.ini"


# Press the green button in the gutter to run the script.
def run():
    """
    Initial function
    :return:
    """
    print("Absolute path:", os.path.abspath(''))

    print_hi('PyCharm')
    load_config()
    # Авторизуемся как сообщество
    vk = vk_api.VkApi(token=token)
    # Работа с сообщениями
    longpoll = VkLongPoll(vk)

    # Основной цикл
    for event in longpoll.listen():

        # Если пришло новое сообщение
        if event.type == VkEventType.MESSAGE_NEW:

            # Если оно имеет метку для меня( то есть бота)
            if event.to_me:

                # Сообщение от пользователя
                request = event.text

                # Каменная логика ответа
                if request == "привет":
                    write_msg(vk, event.user_id, "Хай")
                elif request == "пока":
                    write_msg(vk, event.user_id, "Пока((")
                else:
                    write_msg(vk, event.user_id, "Не поняла вашего ответа...")


def write_msg(vk, user_id, message):
    """
    Send message to VK user
    :param vk: API session
    :param user_id: ID of VK user
    :param message: String of message to send
    :return:
    """
    vk.method('messages.send', {'user_id': user_id, 'message': message, 'random_id': time.time_ns()})




