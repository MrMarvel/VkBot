"""
Основная программа
"""
import os
import threading
from time import sleep

from vk_api import VkApi
from vkbottle import Bot

# Press Shift+F10 to execute it or replace it with your code. Press Double
# Shift to search everywhere for classes, files, tool windows, actions,
# and settings.
from utils.module import Module
from . import gl_vars
from .bot.bot_controller import BotController



class FancyOldQueueModule(Module):

    @property
    def name(self) -> str:
        return "FancyOldQueueModule"

    def module_will_load(self):
        pass

    def module_will_unload(self):
        pass

    def module_infinite_run(self):
        run()


def print_hi(name: str) -> None:
    """
    Print hello to username
    :param name: Username
    :return:
    """

    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.


vk: VkApi | None = None

thread_chats: threading.Thread | None = None  # DEPRECATED


def run():
    """
    Отправная точка работы программы.
    """
    print("Absolute path:", os.path.abspath(''))

    print_hi('PyCharm')
    try:
        pass
        # load_config()  # DEPRECATION because of Heroku env input
    except FileNotFoundError:
        pass
    if gl_vars.token is None:
        gl_vars.token = os.environ.get('TOKEN')
        if gl_vars.token is None:
            raise Exception("TOKEN is not in environment!")
    gl_vars.bot_group_id = os.environ.get('BOT_GROUP_ID')  # 209160825
    if gl_vars.bot_group_id is None:
        raise Exception("BOT_GROUP_ID is not in environment!")
    #

    bottle_bot = Bot(os.environ['TOKEN'])

    # Авторизуемся как сообщество
    global vk
    vk = VkApi(token=gl_vars.token)
    # Основной цикл
    # threading.Thread(target=run_cycle_to_send_msg, daemon=True).start()

    bot = BotController(vk, int(gl_vars.bot_group_id))
    max_shutdown_count = 10
    for shutdowns_count in range(max_shutdown_count+1):
        bot.start()
        if shutdowns_count == 0:
            sleep(1)
            bot.stop()
        while bot.check_or_stop():
            sleep(1)
        sleep(3)
        print("RESTARTING SERVICE....")
    # thread_chats = threading.Thread(target=run_cycle_on_chats, args=(vk,), daemon=True)
    # thread_chats.start()

    # thread_ls = threading.Thread(target=run_cycle_on_ls, args=(vk,), daemon=True)
    # thread_ls.start()
    # thread_ls.join()
    print("Main program is finished!")
