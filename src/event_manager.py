from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import List, Dict, Any


class EventType(Enum):
    GOT_MESSAGE_FROM_PERSONAL_CHAT = auto()
    GOT_MESSAGE_FROM_PUBLIC_CHAT = auto()

    @property
    def context(self):
        return self._context

    def __init__(self, context=None):
        self._context = context


class Event(ABC):
    @property
    @abstractmethod
    def event_type(self) -> EventType:
        raise NotImplementedError

    @property
    def context(self):
        return self._context

    def __init__(self, context: Any = None):
        self._context = context


class GotMessageFromPublicChatEvent(Event):

    @property
    def event_type(self) -> EventType:
        return EventType.GOT_MESSAGE_FROM_PUBLIC_CHAT


class GotMessageFromPersonalChatEvent(Event):

    @property
    def event_type(self) -> EventType:
        return EventType.GOT_MESSAGE_FROM_PERSONAL_CHAT


class EventListener(ABC):
    @abstractmethod
    def react_to_event(self, e: Event) -> bool:
        return True


class GotMessageFromPersonalChatListener(EventListener, ABC):

    def react_to_event(self, e: Event):
        e: GotMessageFromPersonalChatEvent
        return self.react_to_got_message_from_personal_chat_event(e)

    @abstractmethod
    def react_to_got_message_from_personal_chat_event(self, e: GotMessageFromPersonalChatEvent):
        pass


class EventManager:
    def __init__(self):
        self._event_listeners: Dict[EventType, List[EventListener]] = {e: list() for e in EventType}

    def register_event_listener(self, listener: EventListener, e: EventType):
        if listener in self._event_listeners[e]:
            print(f"{listener} уже прослушивает событие {e}!")
            return

        self._event_listeners[e].append(listener)

    def unregister_event_listener(self, listener: EventListener, e: EventType):
        if listener not in self._event_listeners[e]:
            print(f"Нету {listener}, который прослушивает {e}!")
            return

        self._event_listeners[e].remove(listener)

    def unregister_all_event_listeners(self):
        for e in self._event_listeners.keys():
            listeners = self._event_listeners[e]
            while len(listeners) > 0:
                self.unregister_event_listener(listeners[0], e)

    def register_event(self, e: Event):
        for listener in self._event_listeners[e.event_type]:
            listener.react_to_event(e)
