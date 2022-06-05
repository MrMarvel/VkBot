import queue
from typing import Final

DEFAULT_BOT_PREFIX: Final = "!"
pipeline_to_send_msg: Final[queue.Queue[tuple[int, str | dict, bool]]] = queue.Queue()
pipeline_to_send_requests = queue.Queue()
CONFIG_FILENAME = "data/config.ini"
bot_group_id: int | None = None
# API-ключ созданный ранее
token: str | None = None

relationships_in_ls: Final[dict[int, 'RelationshipInLS']] = dict()  #
# Состояния общения с пользователями в ЛС
# Состояния общения с пользователями в чатах.
# {Чат1: {Пользователь1: Отношение, ...}, ...}
relationships_in_chats: Final[dict[int, 'ChatLogic']] = dict()
MAX_REQUESTS_PER_SECOND: Final = 3
