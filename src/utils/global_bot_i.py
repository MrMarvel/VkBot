from abc import abstractmethod
from typing import Protocol, Optional

from vk_api import VkApi


class IGlobalBot(Protocol):
    """
    Интерфейс бота
    """

    @abstractmethod
    def get_event_manager(self):
        raise NotImplementedError

    @abstractmethod
    def get_command_manager(self):
        raise NotImplementedError

    @property
    def vk(self) -> VkApi:
        raise NotImplementedError
