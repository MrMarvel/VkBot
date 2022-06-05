import weakref
from _weakref import ReferenceType
from abc import ABCMeta, abstractmethod


class ObservationModel(metaclass=ABCMeta):
    """
    Абстрактный класс Модель из паттерна MVC.
    """

    def __init__(self):
        self._observers: list[ReferenceType[Observer]] = list()

    def add_observer(self, obs: 'Observer') -> None:
        self._observers.append(weakref.ref(obs))

    def remove_observer(self, obs: 'Observer') -> None:
        self._observers.remove(obs)

    def notify_observers(self) -> None:
        for obs in self._observers:
            obs.model_is_changed()


class Observer(metaclass=ABCMeta):
    """
    Абстрактный класс Наблюдатель из паттерна Наблюдатель для паттерна MVC.
    Наблюдает за параметрами очереди.
    """

    @abstractmethod
    def model_is_changed(self):
        """
        Метод, который вызывается при измении модели
        """
        pass
