from src.utils.module import Module


class MyModule(Module):
    @property
    def name(self) -> str:
        return "Мой модуль1"

    def module_will_load(self):
        print("Я жив!")

    def module_will_unload(self):
        print("Я мёртв!")

    def module_infinite_run(self):
        x = 1
        print("Когда конец?")
        while 1:
            x += 1

