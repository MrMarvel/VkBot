from typing import Final


class ChatUser:
    def __init__(self, user_id: int, chat_id: int):
        self._user_id: Final = user_id
        self._chat_id: Final = chat_id
        self._is_able_to_create_queue: Final = True

    @property
    def is_able_to_create_queue(self):
        return self._is_able_to_create_queue

    @property
    def user_id(self):
        return self._user_id

    @property
    def chat_id(self):
        return self._chat_id

    @staticmethod
    def load_user(chat_id: id, user_id: int) -> 'ChatUser':
        return ChatUser(user_id=user_id, chat_id=chat_id)
