import datetime
from typing import Optional, Final, List

from peewee import *
import pathlib


def get_connection():
    db = SqliteDatabase('my_database.db')
    return db


class BaseModel(Model):
    class Meta:
        database = get_connection()

    pass


class User(BaseModel):
    user_id = IntegerField(primary_key=True)
    name = CharField(null=False)
    surname = CharField(null=False)
    thirdname = CharField(null=True)


class Chat(BaseModel):
    chat_id = IntegerField(primary_key=True)
    chat_name = CharField(null=True)


class ChatUser(BaseModel):
    user = ForeignKeyField(User, null=False)
    chat = ForeignKeyField(Chat, null=False, backref='users_id')
    is_admin = BooleanField(null=False, default=False)

    class Meta:
        indexes = (
            # create a unique on from/to/date
            (('user', 'chat'), True),
        )


class Queue(BaseModel):
    queue_id = AutoField(primary_key=True)
    chat = ForeignKeyField(Chat, null=False, unique=True)
    created_by = ForeignKeyField(User, null=False)
    created_date = DateTimeField(null=False)
    last_show_list_cmid = IntegerField(null=True, unique=True, default=None)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class QueuePosition(BaseModel):
    queue_position_id = AutoField(primary_key=True)
    user = ForeignKeyField(User, null=False, )
    queue = ForeignKeyField(Queue, null=False, backref='positions')
    pos_in_queue = IntegerField(null=False)

    class Meta:
        indexes = (
            # create a unique on from/to/date
            (('user', 'queue'), True),
            (('queue', 'pos_in_queue'), True)
        )

    @staticmethod
    def get_first_from_queue(queue: Queue) -> Optional['QueuePosition']:
        queue_pos = list(QueuePosition.select().where(QueuePosition.queue == queue))
        if len(queue_pos) < 1:
            return None
        return queue_pos[0]

    @staticmethod
    def push_to_pos_or_above(queue: Queue, user: User, to_pos: int = 0) -> int:
        """
        Добавление пользователя в очередь, желающего встать не раньше to_pos позиции.
        :param user:
        :param queue:
        :param to_pos: Позиция, раньше которой пользователь не хочет войти в очередь. От 0
        :return: Позиция в которую встал пользователь. От 0
        """
        user_pos = QueuePosition.get_or_none(queue=queue, user=user)

        if user_pos is not None:
            return -1

        all_pos: list[QueuePosition] = list(QueuePosition.select().where(QueuePosition.queue == queue))
        for i in range(10):
            try_pos = to_pos + i
            pos = QueuePosition.get_or_none(queue=queue, pos_in_queue=try_pos)
            if pos is None:
                try:
                    user_pos = QueuePosition(queue=queue, user=user, pos_in_queue=try_pos)
                    user_pos.save()
                except Exception as _:
                    return -2
                return try_pos
        return -3

    @staticmethod
    def move(queue: Queue, user: User, to_pos: int):
        user_pos_in_queue_from: QueuePosition | None = QueuePosition.get_or_none(queue=queue, user=user)
        if user_pos_in_queue_from is None:
            return -1
        user_pos_from = user_pos_in_queue_from.pos_in_queue
        for i in range(user_pos_from, to_pos):
            i_pos_from = i
            i_pos_to = i + 1
            i_pos_from_was: QueuePosition | None = QueuePosition.get_or_none(queue=queue, pos_in_queue=i_pos_from)
            i_pos_to_was: QueuePosition | None = QueuePosition.get_or_none(queue=queue, pos_in_queue=i_pos_to)
            i_pos_from_was.delete_instance(recursive=True)
            if i_pos_to_was is not None:
                i_pos_to_was.pos_in_queue = i_pos_from
                i_pos_to_was.save()

            try:
                i_pos_switched = user_pos_in_queue_from
                i_pos_switched.pos_in_queue = i_pos_to
                i_pos_switched.save(force_insert=True)
            except Exception as _:
                return -2

db = get_connection()
db.create_tables([Chat, User, ChatUser, Queue, QueuePosition])


def main():
    q = Queue.get(chat_id=2)
    positions = list(QueuePosition.select().where(QueuePosition.queue == q))
    pass


if __name__ == '__main__':
    main()
