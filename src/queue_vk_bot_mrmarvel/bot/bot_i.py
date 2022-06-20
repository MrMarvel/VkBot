from functools import wraps
from typing import Protocol, Callable, Any, Concatenate, ParamSpec, TypeVar, Tuple, Dict, Union

from decohints import decohints

from ..queue.queue_controller import QueueControllerInChat
from ..utils.chat_user import User, Permission, ChatUser
from ..bot.sender_i import ISender


class NoPermissionException(Exception):
    pass


def permission(do: Permission | str):
    if do is not Permission:
        try:
            do = Permission(value=do)
        except ValueError as e:
            print(e)
            print(f"Права \"{do}\" нету в списке прав!")
            raise NoPermissionException("Нет такого права")

    @decohints
    def decorator(f: Callable):
        @wraps(f)
        def wrapper(*args, user: ChatUser, **kwargs):
            if not user.has_permission(do):
                raise NoPermissionException(f"Пользователь {user} не обладает правом {do}!")
            return f(*args, **kwargs)

        return wrapper

    return decorator


ps = Union[Permission, str]


def has_permission(user: ChatUser, do: Permission | str) -> bool:
    if do is not Permission:
        try:
            do = Permission(value=do)
        except ValueError as e:
            print(e)
            print(f"Права \"{do}\" нету в списке прав!")
            raise NoPermissionException("Нет такого права")
    return user.has_permission(do)


def has_permission_in_chat(user: User, in_chat_id: int) -> bool:
    return user.is_admin_in_chat(in_chat=in_chat_id)


class IBot(ISender, Protocol):

    def get_queue_from_chat(self, chat_id) -> QueueControllerInChat | None:
        raise NotImplementedError

    def create_queue_in_chat(self, chat_id, by_user: User) -> QueueControllerInChat:
        """
        Создаёт очередь в чате
        :param by_user:
        :param chat_id:
        :return:
        """
        raise NotImplementedError

    def destroy_queue_in_chat(self, in_chat_id: int, by_user: User):
        """
        Уничтожение очереди
        :param in_chat_id:
        :param by_user:
        :return:
        """
        raise NotImplementedError