import weakref
from _weakref import ReferenceType
from abc import ABCMeta, abstractmethod
from typing import Protocol, final


class ObservationDelegateModel(metaclass=ABCMeta):
    """
    Абстрактный класс Модель из паттерна MVC.
    Работает через делегирование обсервера.
    """

    def __init__(self):
        self._observers: list[ReferenceType[IObserver]] = list()

    @final
    def add_observer(self, obs: 'Observer') -> None:
        self._observers.append(weakref.ref(obs))

    @final
    def remove_observer(self, obs: 'Observer') -> None:
        self._observers.remove(obs)

    @final
    def notify_observers(self) -> None:
        for obs in self._observers:
            obs.model_is_changed()


class IObserver(Protocol):
    """
    Абстрактный класс Наблюдатель из паттерна Наблюдатель для паттерна MVC.
    Наблюдает за параметрами очереди.
    """

    @abstractmethod
    def model_is_changed(self):
        """
        Метод, который вызывается при измении модели
        """
        raise NotImplementedError
