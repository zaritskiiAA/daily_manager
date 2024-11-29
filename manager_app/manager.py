import re
import sys
import datetime as dt
from typing import Any

from prettytable import PrettyTable

from .storage import TaskStorage
from .exceptions import InvalidCommand, InvalidInputData, DataDoesNotExists


class TaskManager:

    """Класс для взаимодействия с пользователем через консоль."""

    VALID_COMMANDS = (
        "show tasks",
        "add task",
        "edit task",
        "delete task",
        "search tasks",
        "done task",
        "cmd",
        "leave",
    )
    VALID_SUBCOMMANDS_MAP = {
        "show_tasks": ("all", "by category"),
        "edit_task": ("payload", "status"),
        "delete_task": ("by id", "by category"),
        "search_tasks": ("by keywords", "by category", "by status"),
    }
    COMMANDS_DESCRIPTION = (
        "Просмотр всех задач или по категориям",
        "Добавление новой задачи",
        "Редактирование задачи",
        "Удаление задачи по идентификатору или категории",
        "Поиск по ключевым словам, категории или статусу выполнения",
        "Отметить задачу как 'Выполненая'",
        "Посмотреть список команд",
        "Завершить работу менеджера",
    )

    @property
    def storage(self):
        if hasattr(self, "_storage"):
            return self._storage
        self._storage = TaskStorage()
        return self._storage

    @staticmethod
    def leave() -> None:
        print("РАБОТА МЕНЕДЖЕРА ЗАДАЧ ОСТАНОВЛЕНА.")
        sys.exit()

    def check_command(self, cmd: str, valid_commands: tuple[str]) -> bool:
        if cmd in valid_commands:
            cmd = re.sub("\\s", "_", cmd)
            self._current_cmd = cmd
            return True
        raise InvalidCommand(
            f"Неизвестная команда: '{cmd}'. Используйте команды из меню. Запросить меню команда 'cmd'."
        )

    def command_execute(self) -> None:
        getattr(self, self._current_cmd)()

    @staticmethod
    def _check_input_data(data: str, pattern: str) -> str:
        if match := re.fullmatch(pattern, data):
            return match.group()
        raise InvalidInputData(f"Неудалось считать переданные данные {data}")

    @staticmethod
    def _check_due_date(date: str) -> None:
        try:
            if dt.datetime.strptime(date, "%Y-%m-%d") <= dt.datetime.now():
                raise InvalidInputData(
                    f"Дата выполнения задачи {date} не может быть меньше текущей"
                )
        except ValueError:
            raise InvalidInputData(
                f"Невалидный формат даты {date}. Используйте шаблон в подсказке ввода."
            )

    def search_tasks(self) -> None:
        search_indicator = input(
            "Укажите критерий по которым искать задачи 'by keywords', 'by category', 'by status': "
        )
        self.check_command(
            search_indicator.lower(), self.VALID_SUBCOMMANDS_MAP.get(self._current_cmd)
        )
        if "by category" in search_indicator:
            category = input("Укажите категорию: ").capitalize()
            data = ("category", category)
        elif "by status" in search_indicator:
            status = self._check_input_data(
                input("Укажите статус: ").capitalize(), r"Выполнена|Не выполнена"
            )
            data = ("status", status)
        else:
            keywords = input("Перечислите ключевые слова через пробел: ").split(" ")
            data = ("keywords", keywords)
        head = ["ID", "TITLE", "DESCRIPTION", "CATEGORY", "DUE_DATE", "PRIORITY", "STATUS"]
        search_result = [tuple(task.values()) for task in self.storage.search_task(data)]
        print(self.output_table(head, search_result))

    def show_tasks(self) -> None:
        head = ["ID", "TITLE", "DESCRIPTION", "CATEGORY", "DUE_DATE", "PRIORITY", "STATUS"]
        result = [tuple(task.values()) for task in self.storage.show_tasks()]
        print(self.output_table(head, result))

    def edit_task(self) -> None:
        task_id = self._check_input_data(input("Укажите id задачи: "), r"[0-9]+")
        task_key = self._check_input_data(
            input(
                "Укажите поле которое требуется изменить "
                "(title, description, category, due_date, priority, status): "
            ),
            r"\b(title|description|category|priority|status|due_date)\b",
        )
        new_data = input("Укажите новое значение: ")
        if task_key == "priority":
            new_data = self._check_input_data(new_data.capitalize(), r"Низкий|Средний|Высокий")
        elif task_key == "status":
            new_data = self._check_input_data(new_data.capitalize(), r"Выполнена|Не выполнена")
        elif task_key == "due_date":
            new_data = self._check_input_data(new_data, r"[0-9]{4}-[0-9]{2}-[0-9]{2}")
            self._check_due_date(new_data)
        self.storage.edit_task((int(task_id), task_key, new_data))
        print(f"Задача {task_id} обновлена")

    def done_task(self) -> None:
        task_id = self._check_input_data(input("Укажите id задачи: "), r"[0-9]+")
        self.storage.done_task(int(task_id))
        print(f"Задача {task_id} завершена")

    def add_task(self) -> None:
        task_name = input("Введите название задачи: ")
        task_desc = input("Введите описание задачи: ")
        task_category = input("Введите название категории задачи: ").capitalize()
        task_due_date = self._check_input_data(
            input("Введите срок выполнения задачи в формате '2024-11-30': "),
            r"[0-9]{4}-[0-9]{2}-[0-9]{2}",
        )
        task_priorty = self._check_input_data(
            input("Укажите приоритет задачи: 'низкий/средний/высокий': ").capitalize(),
            r"Низкий|Средний|Высокий",
        )
        self._check_due_date(task_due_date)
        self.storage.add_task(
            {
                "id": None,
                "title": task_name,
                "description": task_desc,
                "category": task_category,
                "due_date": task_due_date,
                "priority": task_priorty,
                "status": "Не выполнена",
            }
        )
        print(f"Новая задача {task_name} добавлена в менеджера задач.")

    def delete_task(self) -> None:
        delete_key = input("Укажите критерий по которому удалять задачи 'by id или by category': ")
        self.check_command(delete_key.lower(), self.VALID_SUBCOMMANDS_MAP.get(self._current_cmd))
        if 'by id' == delete_key:
            id = self._check_input_data(input("Укажите id задачи: "), r"[0-9]+")
            data = ("id", int(id))
            msg = f"Задача с {id} успешно удалена."
        else:
            category = input("Укажите категорию: ")
            data = ("category", category)
            msg = f"Задачи с категорией {category} успешно удалена."
        self.storage.delete_task(data)
        print(msg)

    def output_table(self, head: list[str], rows: list[tuple[Any]]) -> str:
        table = PrettyTable()
        table.field_names = head
        table.add_rows(rows)
        return table

    def cmd(self) -> None:
        print(
            self.output_table(
                ["КОМАНДА", "ОПИСАНИЕ"],
                [(cmd, desc) for cmd, desc in zip(self.VALID_COMMANDS, self.COMMANDS_DESCRIPTION)],
            )
        )

    def start(self) -> None:
        print("МЕНЕДЖЕРА ЗАДАЧ ЗАПУЩЕН\n")
        self.cmd()
        while True:
            cmd = input("Введите команду: ")
            try:
                self.check_command(cmd.lower(), self.VALID_COMMANDS)
            except InvalidCommand as exc:
                print(exc)
            else:
                try:
                    self.command_execute()
                except (InvalidInputData, DataDoesNotExists, InvalidCommand) as exc:
                    print(exc)


if __name__ == "__main__":
    task_manager = TaskManager()
    task_manager.start()
