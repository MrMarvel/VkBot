import os
from typing import Tuple

from vkbottle.bot import Message, Bot

from utils.module import Module

bot = Bot(os.environ['TOKEN'])
print(1)
class BottleQueueModule(Module):

    @property
    def name(self) -> str:
        return "Bottle Queue Module"

    def module_will_load(self):
        pass

    def module_will_unload(self):
        pass

    def module_infinite_run(self):
        pass


@bot.on.message(text="пока")
async def say_handler(message: Message, args: Tuple[str]):
    print(message, args)
