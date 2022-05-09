from queue import Queue
from typing import Final

DEFAULT_BOT_PREFIX: Final = "!"
pipeline_to_send_msg: Final[Queue[tuple[int, str | dict, bool]]] = Queue()
pipeline_to_send_requests = Queue()
CONFIG_FILENAME = "data/config.ini"
# API-ключ созданный ранее
token: str | None = None
