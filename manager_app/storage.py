import re
import json
from typing import Any

from .exceptions import DataDoesNotExists


class TaskStorage:
    """
    Класс для управления хранилищем задач. Данные содержатся в json формате.
    Для уменьшения нагрузки на файловый дескриптор, данные кешируются.
    """

    _filename = "tasks.json"

    def __init__(self) -> None:
        self._last_id = self._get_last_id()

    @property
    def cache(self):
        if hasattr(self, "_cache"):
            return self._cache
        try:
            self._cache = self._load()
            return self._cache
        except FileNotFoundError:
            self.refresh([])
            self._cache = self._load()
            return self._cache

    def clean_cache(self):
        delattr(self, "_cache")

    def refresh(self, storage_data: list[dict[str]]) -> None:
        self._dump(storage_data)

    def _load(self) -> list[dict[str]] | list:
        with open(self._filename, "r") as f:
            return json.load(f)

    def _dump(self, data: dict[str]) -> None:
        with open(self._filename, "w") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _get_last_id(self) -> int:
        if cache := self.cache:
            return max([task["id"] for task in cache])
        return 0

    def add_task(self, new_data: dict[str]) -> None:
        """Добавляет задачу"""

        storage_data = self.cache
        self._last_id += 1
        new_data["id"] = self._last_id
        storage_data.append(new_data)
        self.refresh(storage_data)
        self.clean_cache()

    def show_tasks(self):
        return self.cache

    def _keywords_search(
        self, storage_data: list[dict[str, Any]], keywords: list[str]
    ) -> list[dict[str, Any]]:
        """
        Метод использует search, когда требуется поиск по ключевым словам.
        Поиск ключевых слов определяется в значения ключей 'title' и 'description'.
        Результат отсортировывает в зависимости от количества совпадений.
        """
        pattern = rf"\b({'|'.join(keywords)})\b"
        count_match_with_data_pos = []
        for idx, task in enumerate(storage_data):
            title_result, desc_result = re.findall(pattern, task["title"]), re.findall(
                pattern, task["description"]
            )
            if title_result or desc_result:
                count_match_with_data_pos.append((idx, max(len(title_result), len(desc_result))))
        count_match_with_data_pos.sort(key=lambda match: (match[1], match[0]), reverse=True)
        return [storage_data[idx] for idx, _ in count_match_with_data_pos]

    def search_task(self, search_data: tuple[str, str], max_return=None) -> list[dict[str, Any]]:
        """
        Поиск задач по ключам.
        Поиск по категориям, по ключевым словам, по статусу.
        В рамках интерфейса, возможен поиск по любому ключу имеющихся в задаче.
        """

        key, value = search_data
        storage_data = self.cache
        if key == "keywords":
            return self._keywords_search(storage_data, value)
        match = []
        for task in storage_data:
            if len(match) == max_return:
                break
            if task.get(key) == value:
                match.append(task)
        return match

    def delete_task(self, delete_data: tuple[str, str]) -> None:
        """
        Удаление задачи по ключам. По id или по категории.
        В рамках интерфейса, возможно удаление по любому ключу имеющихся в задаче.
        """

        storage_data = self.cache
        if "id" in delete_data:
            # т.к. id уникален в дальнейшей проходке по листу нет смысла.
            search_result = self.search_task(delete_data, max_return=1)
        else:
            search_result = self.search_task(delete_data)

        if not search_result:
            raise DataDoesNotExists(f"Задачи с такими данными: {delete_data} не найдена")
        for task in search_result:
            storage_data.remove(task)
        self.refresh(storage_data)
        self.clean_cache()

    def edit_task(self, new_data: tuple[int, str, Any]) -> None:
        """Редактирование задачи."""

        storage_data = self.cache
        task_id, change_key, new_value = new_data
        search_result = self.search_task(("id", task_id), max_return=1)
        if not search_result:
            raise DataDoesNotExists(f"Задачи с id {task_id} не найдена")
        task = search_result.pop()
        task[change_key] = new_value
        self.refresh(storage_data)
        self.clean_cache()

    def done_task(self, task_id: int) -> None:
        """Завершение задачи (установка статуса 'выполнена')."""

        storage_data = self.cache
        search_result = self.search_task(("id", task_id), max_return=1)
        if not search_result:
            raise DataDoesNotExists(f"Задачи с id {task_id} не найдена")
        task = search_result.pop()
        task["status"] = "Выполнена"
        self.refresh(storage_data)
        self.clean_cache()
