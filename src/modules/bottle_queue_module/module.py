from abc import abstractmethod, ABC


class Module(ABC):

    def __init__(self):
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """
        :return строку, имя модуля
        """
        return "Неизвестный модуль"

    @abstractmethod
    def module_will_load(self):
        """
        Подгрузить данные
        """
        raise NotImplementedError

    @abstractmethod
    def module_will_unload(self):
        """
        Сохранить данные перед выходом
        (Фактически никогда не вызывается,
        но по логике должно быть)
        """
        raise NotImplementedError

    @abstractmethod
    def module_infinite_run(self):
        """
        Запуск цикла без надежды выхода
        """
        raise NotImplementedError