import random
import time
from threading import Thread
import copy

import schedule
import vk_api.exceptions
from vk_api import VkApi

from ..bot.bot_i import IBot
from ..gl_vars import *


class RequestController:
    _QUEUE_MAX_SIZE: Final = 10

    def __init__(self, bot: IBot, vk: VkApi, bot_group_id: int):
        self._bot = bot
        self._vk = vk
        self._bot_group_id = bot_group_id
        self._started = False
        self._requests = queue.Queue[dict]()
        self._responses = queue.Queue[dict](self._QUEUE_MAX_SIZE)

    def run_iteration_to_send_requests(self) -> bool:
        """
        Цикл для отправки запрсов.
        :return:
        """
        # print("REQ")
        if pipeline_to_send_requests.empty():
            return False
        raise NotImplementedError

    def got_to_send_request(self, request) -> dict | None:
        try:
            method = request['method']
            msg = request['body']
            request['need_response'] = True
            self._requests.put(request)
            tries = 1
            uuid = time.time_ns()
            request['uuid'] = uuid
            while uuid not in map(lambda x: dict(x).get('uuid', 0), self._responses.queue) and tries <= 10:
                time.sleep(0.5)
                tries += 1
            if tries > 10:
                print(Exception("Превышено кол-во попыток ожидания"))
                # raise Exception("Превышено кол-во попыток ожидания")
                return None
            return request
        except Exception as e:
            raise e
            return None

    async def got_to_send_request_no_wait(self, request) -> int:
        try:
            method, msg = request

            self._requests.put(request)
        except Exception:
            return -1
        return 200

    def run_iteration_to_send_msg(self) -> bool:
        # print("MSG")
        if pipeline_to_send_msg.empty():
            if self._requests.empty():
                return False
            request: dict = self._requests.get()
            clear_request = copy.deepcopy(request)
            need_response = False
            if request.get('need_response', False):
                need_response = clear_request.pop('need_response')
            try:
                method = request['method']
                body = request['body']
                response = self._vk.method(method, body)
                if need_response:
                    request['response'] = response
                    if self._responses.qsize() >= self._QUEUE_MAX_SIZE - 1:
                        self._responses.get()
                    self._responses.put(request)
            except vk_api.exceptions.ApiError as e:
                print(f"ERRORED sending a message\n{request, self._requests}")
                print(e)
            except Exception as e:
                print(f"ERRORED sending a message\n{request, self._requests}")
                raise e
            return True
        id, msg, is_private = pipeline_to_send_msg.get(block=True)
        try:
            if type(msg) is dict:
                self._bot.send_msg_packed_by_json(message_json=msg)
            elif type(msg) is str:
                if is_private:
                    self._bot.write_msg_to_user(user_id=id, message=msg)
                else:
                    self._bot.write_msg_to_chat(chat_id=id, message=msg)
        except Exception as e:
            print(f"ERRORED sending a message\n{self._vk, id, msg, is_private}")
            raise e
        return True

    def run_cycle_to_send_msg(self) -> None:
        print("Sending cycle is running!")
        min_time_to_wait_before_next_request: Final = 0.334
        iter_pos = 1
        max_iter_pos = 2
        try:
            while 1:
                iter_pos = (iter_pos + 1) % max_iter_pos
                try:
                    for _ in range(max_iter_pos):
                        match iter_pos:
                            case 0:
                                if self.run_iteration_to_send_msg():
                                    break
                            case 1:
                                if self.run_iteration_to_send_requests():
                                    break
                        iter_pos = (iter_pos + 1) % max_iter_pos
                except Exception as e:
                    print(e)
                    raise e
                time.sleep(min_time_to_wait_before_next_request + random.random() * 0.1)
        finally:
            print("Sending cycle stopped working!")

    def start(self):
        if self._started:
            return
        Thread(target=self.run_cycle_to_send_msg, daemon=True).start()
        self._started = True
