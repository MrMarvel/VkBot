import enum
import os
from copy import deepcopy
from typing import Final, Any

from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Permission(enum.Enum):

    @staticmethod
    def _generate_next_value_(name: str, start: int, count: int, last_values: list[Any]) -> Any:
        return 'is_able_to_' + name.lower()

    CREATE_QUEUE = 'is_able_to_create_queue'
    FORCE_SKIP = enum.auto()
    SWITCH_POS_IN_QUEUE = enum.auto()
    DESTROY_QUEUE = enum.auto


class User:
    admin_list_vk_id = str(os.environ.get("ADMIN_LIST")).split(',')

    def __init__(self, user_id: int):
        super().__init__()
        self._user_id: int = user_id
        self._admin_in_chat_ids = list[int]()
        self._name: str | None = None
        self._surname: str | None = None
        self._lastname: str | None = None

    @property
    def user_id(self):
        return self._user_id

    @property
    def admin_chats(self):
        return deepcopy(self._admin_in_chat_ids)

    @admin_chats.setter
    def admin_chats(self, admin_chats: list[int]):
        self._admin_in_chat_ids = admin_chats

    @property
    def name(self):
        return self._name

    @property
    def surname(self):
        return self._surname

    @property
    def lastname(self):
        return self._lastname

    def is_admin_in_chat(self, in_chat: int):
        if str(self.user_id) in self.admin_list_vk_id:
            return True
        if in_chat not in self._admin_in_chat_ids:
            return False
        return self._admin_in_chat_ids[in_chat]


class ChatUser(User):
    def __init__(self, user_id: int, chat_id: int):
        super().__init__(user_id)

        self._chat_id: Final = chat_id
        self._permissions = dict[Permission, bool]()

        self._is_admin: bool = self.is_admin_in_chat(in_chat=self._chat_id)

        for p in Permission:
            self._permissions[p] = self._is_admin

        self._is_able_to_create_queue = self._is_admin
        self._is_able_to_force_skip = self._is_admin
        self._is_able_to_switch_pos_in_queue = self._is_admin

    def has_permission(self, permission: Permission):
        if permission in self._permissions:
            return self._permissions[permission]
        return False

    @property
    def is_admin(self):
        return self._is_admin

    @property
    def is_able_to_create_queue(self):
        return self._is_able_to_create_queue

    @property
    def chat_id(self):
        return self._chat_id

    @staticmethod
    def load_user(chat_id: id, user_id: int) -> 'ChatUser':
        return ChatUser(user_id=user_id, chat_id=chat_id)
