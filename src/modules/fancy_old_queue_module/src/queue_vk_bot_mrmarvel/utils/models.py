from peewee import *
import pathlib


def get_connection():
    db = SqliteDatabase('my_database.db')
    print(pathlib.Path().resolve())
    return db

class BaseModel(Model):
    class Meta:
        database = get_connection()

    pass


class User(BaseModel):
    user_id = IntegerField(primary_key=True)


class Queue(BaseModel):
    queue_id = AutoField(primary_key=True)
    chat_id = IntegerField(null=False, unique=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class QueuePosition(BaseModel):
    queue_position_id = AutoField(primary_key=True)
    user = ForeignKeyField(User)
    queue = ForeignKeyField(Queue)
    pos_in_queue = IntegerField(null=False)

    class Meta:
        indexes = (
            # create a unique on from/to/date
            (('user', 'queue'), True),
        )



def main():
    db = get_connection()
    db.create_tables([Queue, User, QueuePosition])
    q = Queue.get(chat_id=2)
    positions = list(QueuePosition.select().where(QueuePosition.queue == q))
    pass


if __name__ == '__main__':
    main()
