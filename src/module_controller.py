from threading import Thread
from typing import List, Dict

from utils.module import Module


class ModuleController:
    """
    Простой контроллер модулей, который просто запускает модули в отдельных потоках.
    """

    def __init__(self):
        self._modules: List[Module] = list()
        self._threads: Dict[Module, Thread] = dict()

    def start_module(self, module: Module):
        if module in self._modules:
            print("")
        self._modules.append(module)
        try:
            module.module_will_load()
            module_thread = Thread(target=module.module_infinite_run, args=(), daemon=True)
            self._threads[module] = module_thread
            module_thread.start()
            print(f"Модуль \"{module.name}\" был загружен!")
        except Exception as e:
            print(f"\"{module.name}\" вызвал ошибку во время запуска: {e}")

    def destroy_modules(self):
        for m in self._modules:
            try:
                t = self._threads.get(m, None)
                if t is not None:
                    print(f"Поток модуля \"{m.name}\" останется рабочим "
                          f"после завершение основной программы (возможно)!")
                m.module_will_unload()
            finally:
                print(f"Модуль \"{m.name}\" был выгружен!")

    def join(self):
        for t in self._threads.values():
            t.join()
