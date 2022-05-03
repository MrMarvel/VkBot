from typing import Protocol

from .chat_user import ChatUser


class IChat(Protocol):

    def user_wants_to_create_queue(self, user_id: int):
        raise NotImplementedError

    @property
    def chat_id(self) -> int:
        raise NotImplementedError

    def send_queue_list(self) -> None:
        raise NotImplementedError

    def user_wants_to_join_to_queue(self, user: ChatUser) -> int | None:
        raise NotImplementedError

    @property
    def is_queue_running(self) -> bool:
        raise NotImplementedError

    def user_wants_to_force_next_queue(self, user: ChatUser) -> ChatUser | None:
        raise NotImplementedError

    def next_on_queue(self, offset: int = 0) -> ChatUser | None:
        raise NotImplementedError