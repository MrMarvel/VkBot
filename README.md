__# VkBot
ВК бот для организации очередей и для других организационных фич:
* Управление очередями в ЛС.

## Первый запуск
Запустить в консоли python setup.py install для установки зависимостей.
Запустить __init__.py из queuevkbot для запуска скрипта.

## Документация
Для генерации документации по проекту в консоли ввести в главной папке проекта ($ProjectFileDir$):
> $ProjectFileDir$/venv/Scripts/sphinx-apidoc.exe -f -o ./docs/source ./src src --ext-autodoc -T -l

> $ProjectFileDir$\docs\make.bat clean

Далее нужно выполнить следующую команду:
> $ProjectFileDir$\docs\make.bat html

## Зависимости
| Modules    | Version  |
|------------|:--------:|
| sphinx     | ==4.5.0  |
| vk_api     | ==11.9.8 |
| Deprecated | ==1.2.13 |
| decohints  | ==1.0.7  |
| requests   | ==2.28.0 |
| SQLAlchemy | ==1.4.37 |
| schedule   | ==1.1.0  |