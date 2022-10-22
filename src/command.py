from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from vk_api.bot_longpoll import VkBotMessageEvent

from event_manager import EventListener, Event, EventType, EventManager
from utils.global_bot_i import IGlobalBot


class Command(ABC):
    def __init__(self):
        self._root_command: Command | None = None
        self._sub_commands: Dict[str, Command] = dict()

    @property
    def sub_commands(self) -> Dict[str, 'Command']:
        return self.sub_commands.copy()

    @property
    def root_command(self) -> Optional['Command']:
        return self._root_command

    @root_command.setter
    def root_command(self, cmd: Optional['Command']):
        self._root_command = cmd

    @property
    def full_command_name(self) -> str:
        if self._root_command is None:
            return self.command_last_part_name
        return self._root_command.full_command_name + self.command_last_part_name

    @property
    @abstractmethod
    def command_last_part_name(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def help_str(self) -> str:
        return self.full_command_name

    @property
    @abstractmethod
    def short_help_str(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def run(self, args: Any = None):
        raise NotImplementedError

    def register_sub_command(self, cmd: 'Command'):
        self.sub_commands[cmd.command_last_part_name] = cmd
        cmd._root_command = self

    def unregister_sub_command(self, cmd: 'Command'):
        if cmd.command_last_part_name not in self.sub_commands:
            return

        self.sub_commands.pop(cmd.full_command_name)._root_command = None


class HelpCommand(Command):

    @property
    def short_help_str(self) -> str:
        return "Выводит помощь"

    @property
    def command_last_part_name(self) -> str:
        return "help"

    @property
    def help_str(self) -> str:
        return "help {cmd} - расскажет о команде"

    def run(self, args: Any = None):
        if type(args) is list:
            args: list


class CommandManager(EventListener):

    def react_to_event(self, e: Event):
        if e.event_type == EventType.GOT_MESSAGE_FROM_PUBLIC_CHAT:
            context = e.context
            if type(context) is VkBotMessageEvent:
                context: VkBotMessageEvent
                cmd = self.get_command_by_str(context.message.get("text", ""))
                if cmd is None:
                    return
                cmd.run()

    @property
    def help_chat_str(self) -> str:
        msg = "Возможные команды:\n"
        for cmd in self._chat_commands.values():
            if cmd.root_command is not None:
                continue
            msg += f"!{cmd.full_command_name} - {cmd.short_help_str}\n"
        return msg

    def __init__(self, gb: IGlobalBot):
        self._chat_commands: Dict[str, Command] = dict()
        event_manager: EventManager = gb.get_event_manager()
        event_manager.register_event_listener(self, EventType.GOT_MESSAGE_FROM_PUBLIC_CHAT)
        event_manager.register_event_listener(self, EventType.GOT_MESSAGE_FROM_PERSONAL_CHAT)

        self.register_command(HelpCommand())

    def register_command(self, cmd: Command):
        if cmd.full_command_name in self._chat_commands:
            print(f"Команда {cmd.full_command_name} уже объявлена!")
            return

        self._chat_commands[cmd.full_command_name] = cmd

    def get_command_by_str(self, str_cmd: str) -> Command | None:
        split_cmd = str_cmd.lower().split(sep=" ")
        sum_str = ""
        answer_cmd: Command | None = None
        for i, part_str_cmd in enumerate(split_cmd):
            sum_str += part_str_cmd
            if sum_str in self._chat_commands:
                answer_cmd = self._chat_commands.get(sum_str, None)
        return answer_cmd

    def unregister_command(self, cmd: Command):
        if cmd.full_command_name not in self._chat_commands:
            print(f"Такой {cmd.full_command_name} команды нет!")
            return

        self._chat_commands.pop(cmd.full_command_name)

    def unregister_all_commands(self):
        self._chat_commands.clear()
