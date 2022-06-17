import os
from typing import Final


class User:
    def __init__(self, user_id: int):
        self._user_id: Final = user_id

    @property
    def user_id(self):
        return self._user_id


class ChatUser(User):
    def __init__(self, user_id: int, chat_id: int):
        super().__init__(user_id)
        admin_list_vk_id = os.environ.get("ADMIN_LIST").split(',')
        self._chat_id: Final = chat_id
        self._is_able_to_create_queue: Final = str(user_id) in admin_list_vk_id
        self._is_able_to_force_skip: Final = str(user_id) in admin_list_vk_id
        self._is_able_to_switch_pos_in_queue: Final = str(user_id) in admin_list_vk_id

    @property
    def is_able_to_create_queue(self):
        return self._is_able_to_create_queue

    @property
    def chat_id(self):
        return self._chat_id

    @staticmethod
    def load_user(chat_id: id, user_id: int) -> 'ChatUser':
        return ChatUser(user_id=user_id, chat_id=chat_id)
