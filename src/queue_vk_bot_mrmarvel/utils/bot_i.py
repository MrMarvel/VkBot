from queue import Queue
from typing import Protocol

from queue_vk_bot_mrmarvel.controllers.queue_controller import QueueController


class IBot(Protocol):
    def write_msg_to_chat(self, chat_id, message) -> None:
        """
        Send message to VK user
        :param chat_id: ID ВК чата
        :param message: String of message to send
        """
        raise NotImplementedError

    def write_msg_to_user(self, user_id, message) -> None:
        """
        Send message to VK user
        :param user_id: ID ВК пользователя
        :param message: String of message to send
        :return:
        """
        raise NotImplementedError

    def send_msg_packed_by_json(self, message_json) -> None:
        """
        Send message to VK user
        :param message_json: JSON сообщения
        """
        raise NotImplementedError

    def create_queue_in_chat(self, chat_id) -> None:
        """
        Создаёт очередь в чате
        :param chat_id:
        :return:
        """
        raise NotImplementedError

    def get_queue_from_chat(self, chat_id) -> QueueController | None:
        raise NotImplementedError
