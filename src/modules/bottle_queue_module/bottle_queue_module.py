import asyncio
import datetime
import os
import random
from asyncio import sleep
from typing import List

import loguru
from scheduler.asyncio import Scheduler
from vkbottle import *
from vkbottle.bot import Message, Bot
from vkbottle.dispatch.rules.base import *
from vkbottle_types.codegen.objects import UsersUserFull

from .models import Queue, User, QueuePosition
from .module import Module

bot = Bot(os.environ['TOKEN'])
api = API(os.environ['TOKEN'])

loguru.logger.disable("DEBUG")
loguru.logger.disable("vkbottle.framework")
loguru.logger.disable("vkbottle.polling")
time_to_live_service_message = 30  # seconds
print(1)
prefix = "!"


class BottleQueueModule(Module):

    @property
    def name(self) -> str:
        return "Bottle Queue Module"

    def module_will_load(self):
        pass

    def module_will_unload(self):
        pass

    def module_infinite_run(self):
        pass


def get_orm_user(user_info: UsersUserFull) -> User | None:
    u = None
    try:
        u = User.get(user_id=user_info.id)
    except Exception as _:
        pass
    if u is None:
        try:
            u = User(user_id=user_info.id, name=user_info.first_name, surname=user_info.last_name,
                     thirdname=user_info.maiden_name)
            u.save(force_insert=True)
        except Exception as _:
            return None
    return u


def get_orm_queue(chat_id: int) -> Queue | None:
    q = None
    try:
        q = Queue.get(chat_id=chat_id)
    except Exception as _:
        return None
    return q


def user_mention_str(user_id: int, display_str: str) -> str:
    return f"@id{user_id} ({display_str})"


def user_mention_name_surname_str(user_id: int, name: str, surname: str) -> str:
    return user_mention_str(user_id, name + surname)


def user_mention_obj_str(user_info: UsersUserFull) -> str:
    return user_mention_name_surname_str(user_info.id, user_info.first_name, user_info.last_name)


async def service_message(message: Message, text: str):
    answer = await message.reply(message=text)

    scheduler = Scheduler(loop=asyncio.get_running_loop())

    async def delete() -> None:
        try:
            await api.messages.delete(cmids=[answer.conversation_message_id], delete_for_all=True,
                                      peer_id=answer.peer_id)
        except Exception as _:
            pass

    scheduler.once(datetime.timedelta(seconds=time_to_live_service_message), delete)


async def queue_list_message(message: Message):
    user_info = await message.get_user()
    queue = Queue.get_or_none(chat_id=message.chat_id)
    if queue is None:
        return
    last_cmid = queue.last_show_list_cmid

    async def delete() -> None:
        try:
            await api.messages.delete(cmids=[last_cmid], delete_for_all=True,
                                      peer_id=message.peer_id)
        except Exception as _:
            pass

    if last_cmid is not None:
        await delete()
        queue.last_show_list_cmid = None
        queue.save()

    queue_list: List[QueuePosition] = list(QueuePosition.select()
                                           .where(QueuePosition.queue == queue)
                                           .order_by(QueuePosition.pos_in_queue))
    msg = f"В очереди: {len(queue_list)} человек\n"
    last_user_pos = 0
    for pos_in_queue in queue_list:
        user_pos = pos_in_queue.pos_in_queue
        for i in range(last_user_pos, user_pos):
            msg += f"{i + 1} — \n"
        user: User = pos_in_queue.user
        msg += f"{user_pos + 1} — @id{user.user_id} ({user.surname} {user.name})\n"
        last_user_pos = user_pos

    msg += f'----------------------------\n' \
           f'{prefix}q j — чтобы войти следующим!'
    answer = await message.answer(msg)
    queue.last_show_list_cmid = answer.conversation_message_id
    queue.save()


async def user_wants_to_create_queue(message: Message, user_info: UsersUserFull, chat_id) -> Queue | None:
    u = get_orm_user(user_info)
    user_mention = user_mention_obj_str(user_info)
    if u is None:
        await service_message(message, "Пользователь не найден")
        return None
    q = None
    try:
        q = Queue.get(chat_id=chat_id)
    except Exception as _:
        pass
    if q is not None:
        await service_message(message, "Очередь уже создана!")
        return q
    try:
        q = Queue(chat_id=chat_id, created_by=u, created_date=datetime.datetime.now())
        q.save()
        await service_message(message, "Очередь создана!")
    except Exception as _:
        await message.reply("Неизвестная ошибка")
        return None

    return q


async def send_welcome_msg_to_chat(message: Message):
    """
    Сообщение для беседы
    """
    msg = "Привет!\n" \
          "Я Бот EzQueue — Помимо простых оповещений, я сумею создавать очереди для вас!\n" \
          "🔹 !q create — создать очередь\n" \
          "🔹 !q join — войти в очередь\n"
    answer = await message.answer(message=msg)
    pass


def send_cmd_help() -> str:
    pass


# @bot.on.chat_message(FromUserRule(), CommandRule("start", [prefix], 0))
async def test_cmd_handler(message: Message):
    return
    await service_message(message, "TEST")
    await send_welcome_msg_to_chat(message)
    await sleep(5)
    try:
        await api.messages.delete(cmids=[message.conversation_message_id], delete_for_all=True,
                                  peer_id=2000000000 + message.chat_id)
    except Exception as _:
        pass


async def user_wants_to_join_queue(message: Message, user_info: UsersUserFull, try_join_to_pos_or_above: int = 0):
    q = get_orm_queue(message.chat_id)
    if q is None:
        await service_message(message, "Невозможно подключится к несуществующей очереди!\n"
                                       "Чтобы создать очередь !q create")
        return

    u = get_orm_user(user_info)

    pos_in_queue = None
    try:
        pos_in_queue = QueuePosition.get(queue=q, user=u)
    except Exception as _:
        pass
    if pos_in_queue is not None:
        await service_message(message, "Вы уже в очереди!")
        return

    all_positions = list(QueuePosition.select().where(QueuePosition.queue == q))
    pos_in_queue = QueuePosition.push_to_pos_or_above(queue=q, user=u, to_pos=try_join_to_pos_or_above)
    if pos_in_queue == -3:
        await service_message(message, "Максимум можно отступать до 10 слотов от первой сплошной очереди!")
    else:
        await service_message(message, f"Вы встали в очередь {pos_in_queue + 1}-м! Чтобы выйти !q leave")


async def user_wants_to_show_queue(message: Message):
    await queue_list_message(message)


async def idk_msg_to_chat(message: Message):
    """
    Общее сообщение
    """
    rand_msgs = "К сожалению я не понял, что вы имели ввиду.", \
                "Мяу?\nА вы поняли, что я имел в виду? Вот и я также вас.", \
                "Хммм.. даже не знаю что сказать."
    await service_message(message, random.choice(rand_msgs))


async def user_wants_to_close_queue(message, chat_id: int):
    q: Queue | None = Queue.get_or_none(chat_id=chat_id)
    if q is not None:
        q.delete_instance()
        await service_message(message, "Прощай очередь!")
    else:
        await service_message(message, "Очереди и так нету!")


@bot.on.chat_message(FromUserRule(True))
async def cmd_queue_handler(message: Message):
    print(message.chat_id)
    user = await message.get_user()
    msg = message.text
    got_bot_command = False
    try:
        if message.chat_id < 0:
            pass
            # from persenal chat
        else:
            create_alias = ['создать очередь', 'создание очереди', 'create queue', 'qc', 'cq',
                            'очередь появись', 'queue init', 'queue initialization']
            show_queue_alias = ['вывод очереди', 'очередь', 'текущая очередь']
            delete_queue_alias = ['удаление очереди', 'delete queue', 'remove queue', 'clear queue', 'очистить очередь',
                                  'очистка очереди']
            join_queue_alias = ['Встать в очередь', 'join/j', 'занять очередь']
            for _ in range(1):
                if msg in create_alias:
                    got_bot_command = True
                    await user_wants_to_create_queue(message, user, message.chat_id)
                    break
                if msg in show_queue_alias:
                    got_bot_command = True
                    await user_wants_to_show_queue(message)
                    break
                if msg in delete_queue_alias:
                    got_bot_command = True
                    await user_wants_to_close_queue(message, chat_id=message.chat_id)
                if msg in join_queue_alias:
                    got_bot_command = True
                    await user_wants_to_join_queue(message, user)
                if msg.startswith(prefix):
                    got_bot_command = True
                    print("YES")
                    # Это команда
                    clear_msg = msg.removeprefix(prefix)  # Сообщение без префикса
                    cmd_args = clear_msg.split(sep=' ')
                    if len(cmd_args) > 0:
                        cmd = cmd_args[0]
                        if cmd == "start":
                            await send_welcome_msg_to_chat(message)
                            break
                        if cmd == "help":
                            send_cmd_help()
                            break
                        if cmd == "prefix" or cmd == "pr":
                            if len(cmd_args) > 1:
                                sub_cmd = cmd_args[1]
                                if sub_cmd == "change" or sub_cmd == "ch":
                                    if len(cmd_args) > 2:
                                        new_prefix = cmd_args[2]
                                        if len(new_prefix) == 1:
                                            change_prefix(new_prefix=new_prefix)
                                            send_message(f"Теперь у меня новый префикс \"{self.__bot_prefix}\" для "
                                                         f"команд!")
                                        else:
                                            send_message(f"Префикс \"{new_prefix}\" слишком длинный")
                                    else:
                                        send_message("Не указан префикс.")
                            else:
                                send_message(f"Текущий установленный префикс \"{self.__bot_prefix}\".\n"
                                             f"Доступны следующий суб-команды:\n"
                                             f"change {{новый префикс}}")
                            return
                        if cmd == "queue" or cmd == "q":
                            q = None
                            try:
                                q = Queue.get(chat_id=message.chat_id)
                            except Exception as _:
                                pass
                            if len(cmd_args) > 1:
                                sub_cmd = cmd_args[1]
                                if sub_cmd == "create" or sub_cmd == "new":
                                    await user_wants_to_create_queue(message, user, message.chat_id)

                                elif sub_cmd == "join" or sub_cmd == "j":
                                    if len(cmd_args) > 2:
                                        try:
                                            join_to_pos = int(cmd_args[2]) - 1
                                            await user_wants_to_join_queue(message, user,
                                                                           try_join_to_pos_or_above=join_to_pos)
                                        except ValueError:
                                            await service_message(message, f"\"{cmd_args[2]}\" Not A Number!")
                                    else:
                                        await user_wants_to_join_queue(message, user)

                                elif sub_cmd in ("skip", "sk", "skp"):
                                    if len(cmd_args) > 2:
                                        try:
                                            go_back_steps = int(cmd_args[2])
                                            user_wants_to_skip_back(user=self._user, go_back_steps=go_back_steps)
                                        except ValueError:
                                            send_message(f"\"{cmd_args[2]}\" Not A Number!")
                                    else:
                                        user_wants_to_skip_back(user=self._user)
                                elif sub_cmd in ("close", "cl", "c"):
                                    user_wants_to_close_queue()
                                    break
                                elif sub_cmd in ("next", "nxt", "n"):
                                    # self.__send_message("Автор ещё не реализовал эту фичу!")
                                    # Следующий по очереди
                                    user_wants_to_remove_first_from_queue()
                                    break
                                elif sub_cmd in ("leave", "leav", "le", "l"):
                                    user_wants_to_leave_queue()
                                    break
                                elif sub_cmd in ("switch", "sw", "swtch"):
                                    break
                                    if not self.is_queue_running:
                                        self.__send_message(
                                            f"Нету очереди. Чтобы создать очередь {self.__bot_prefix}q create")
                                    if len(cmd_args) > 3:
                                        pos1 = int(cmd_args[2])
                                        pos2 = int(cmd_args[3])
                                        # if type(pos1) is not int:
                                        #     self.__send_message(f"{pos1} не число!")
                                        #     return
                                        # if type(pos2) is not int:
                                        #     self.__send_message(f"{pos2} не число!")
                                        #     return
                                        if not self._all_dialogs_in_chats_controller.switch(pos1 - 1, pos2 - 1):
                                            self.__send_message(
                                                f"Нет столько людей в очереди сколько указали вы позиций! "
                                                f"{max(pos1, pos2)}")
                                            break
                                        await service_message(message,
                                                              f"Были успешно поменяны местами {pos1} и {pos2}!")
                                        await user_wants_to_show_queue(message)
                                    break
                                else:
                                    await service_message(message,
                                                          f"Ожидалось create|new, join|j, skip|sk, next, "
                                                          f"но получил {sub_cmd}.")
                            else:
                                await user_wants_to_show_queue(message)
                                await service_message(message,
                                                      f"Нету очереди. Чтобы создать очередь {prefix}q create")
                                # self.__chat.send_queue_list()
                            break

                    await idk_msg_to_chat(message)  # Не одна команда не сработала
                    break

            # from group chat
    except Exception as e:
        await service_message(message, "Непредвиденная ошибка")
        raise e
    if got_bot_command:
        try:
            await api.messages.delete(cmids=[message.conversation_message_id], delete_for_all=True,
                                      peer_id=message.peer_id)
        except Exception as _:
            pass


bot.run_forever()
