from typing import Protocol


class ISender(Protocol):

    def remove_messages_from_chat(self, message_ids: list[int], chat_id: int) -> dict | None:
        raise NotImplementedError

    def remove_message_from_chat(self, message_id: int, chat_id: int) -> dict | None:
        raise NotImplementedError

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

    def send_msg_packed_by_json(self, message_json, do_not_remove_message: bool = False) -> dict | None:
        """
        Send message to VK user
        :param do_not_remove_message:
        :param message_json: JSON сообщения (тело сообщения без random_id)
        """
        raise NotImplementedError
