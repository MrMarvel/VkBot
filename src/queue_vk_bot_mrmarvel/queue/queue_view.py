import inspect
import json
from time import time_ns

from ..queue.queue_model import QueueInChat
from ..bot.sender_i import ISender


class QueueViewInChat:
    CHAT_ID_PREFIX = 2000000000
    _FIXED_BOT_PREFIX = '!'

    def __init__(self, model: QueueInChat, sender: ISender):

        self._model = model
        self._sender = sender
        self._queue_list_message_id = None
        self.view_did_load()

    def view_did_load(self):
        self._sender.write_msg_to_chat(self._model.chat_id, "Очередь создана!")

    def reset_queue_list(self):
        if self._queue_list_message_id is not None:
            self._remove_queue_list()
        self._send_queue_list()

    def _remove_queue_list(self):
        if self._queue_list_message_id is not None:
            chat_id = self._model.chat_id
            self._sender.remove_message_from_chat(message_id=self._queue_list_message_id,
                                                  chat_id=chat_id)
        self._queue_list_message_id = None

    def _send_queue_list(self):
        """
        Отправляет в чат беседы очередь.
        """
        queue = self._model.as_list()
        chat_id = self._model.chat_id
        message = f"В очереди: {len(queue)} человек\n"
        for i, user in enumerate(queue):
            message += f"{i + 1} — @id{user.user_id}\n"
        message += f'----------------------------\n' \
                   f'{self._FIXED_BOT_PREFIX}q j — чтобы войти следующим!'
        values = {"random_id": time_ns(),
                  "peer_ids": [self.CHAT_ID_PREFIX + chat_id],
                  "message": message,
                  "intent": "default"}
        result = self._sender.send_msg_packed_by_json(values, do_not_remove_message=True)
        if type(result) is list:
            if len(result) > 0:
                result = result[0]
        response = None
        if type(result) is dict:
            response = result.get('response', None)
        # result = self._vk.method(method="messages.send", values=values)
        if type(response) is list:
            if len(response) > 0:
                response = response[0]
        if type(response) is dict:
            print(response)
            conversation_message_id = response.get("conversation_message_id", None)
            if conversation_message_id is None:
                print(self.__class__.__name__, inspect.currentframe().f_code.co_name, "Непредвиденная ситуация")
                return
            conversation_message_id = int(conversation_message_id)
            self._queue_list_message_id = conversation_message_id


def get_button(text: str, color) -> dict:
    return {
        "action": {
            "type": "text",
            "payload": "{\"Button\": \"" + "1" + "\"}",
            "label": f"{text}"
        },
        "color": f"{color}"
    }


def send_messange_with_keyboard(self, message: str, keyboard) -> None:
    # msg = {'chat_id': self.__chat_id, 'keyboard': keyboard}
    # pipeline_to_send_msg.put_nowait((self._chat_id, message, False))
    pass
