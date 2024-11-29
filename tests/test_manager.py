import datetime as dt
from datetime import timedelta

import pytest

from manager_app.manager import TaskManager
from manager_app.exceptions import DataDoesNotExists, InvalidInputData
from .utils import mock_input


class TestTaskManager:
    def test_add_task(self, storage):
        task_data = {
            "title": "test task",
            "description": "first test task",
            "category": "test category",
            "due_date": dt.datetime.strftime((dt.datetime.now() + timedelta(days=1)), "%Y-%m-%d"),
            "priority": "высокий",
            "status": "Не выполнена",
        }
        storage.add_task(task_data)
        assert (
            len(storage.cache) == 1
        ), "Убедитесь, что при добавлении задачи с валидными данными задача была добавлена."
        assert (
            task_data == storage.cache[0]
        ), "Убедитесь, что структура полей и их значения соответствуют требованиям."

    def test_show_task(self, storage):
        task_data = {
            "id": 1,
            "title": "test task",
            "description": "first test task",
            "category": "test category",
            "due_date": dt.datetime.strftime((dt.datetime.now() + timedelta(days=1)), "%Y-%m-%d"),
            "priority": "высокий",
            "status": "Не выполнена",
        }
        assert (
            task_data == storage.show_tasks()[0]
        ), "Убедитесь, что при запросе получить все задачи данные возвращаются."

    @pytest.mark.parametrize(
        "search_data",
        [
            ("category", "test category"),
            ("status", "Не выполнена"),
            ("keywords", ["test", "first"]),
        ],
    )
    def test_search_task(self, storage, search_data):
        task_data = {
            "id": 1,
            "title": "test task",
            "description": "first test task",
            "category": "test category",
            "due_date": dt.datetime.strftime((dt.datetime.now() + timedelta(days=1)), "%Y-%m-%d"),
            "priority": "высокий",
            "status": "Не выполнена",
        }
        search_result = storage.search_task(search_data)
        print(search_result)
        assert (
            len(search_result) == 1
        ), f"Убедитесь, что при поиске по ключу {search_data} возвращает результат."
        assert (
            search_result[0] == task_data
        ), f"Убедитесь, что при поиске по ключу {search_data} возвращается корректный результат."

    def test_done_task(self, storage):
        storage.done_task(1)
        assert (
            storage.cache[0]["status"] == "Выполнена"
        ), "Убедитесь, что done_task метод завершает задачу."

    @pytest.mark.parametrize(
        "change_key, change_value",
        [
            ("title", "new title"),
            ("description", "new description"),
            ("category", "new category"),
            ("priority", "низкий"),
            ("status", "не выполнена"),
            ("due_date", dt.datetime.strftime((dt.datetime.now() + timedelta(days=2)), "%Y-%m-%d")),
        ],
    )
    def test_edit_task(self, storage, change_key, change_value):
        expected_value = {
            "title": "new title",
            "description": "new description",
            "category": "new category",
            "priority": "низкий",
            "status": "не выполнена",
            "due_date": dt.datetime.strftime((dt.datetime.now() + timedelta(days=2)), "%Y-%m-%d"),
        }
        storage.edit_task((1, change_key, change_value))
        task = storage.cache[0]
        assert (
            task[change_key] == expected_value[change_key]
        ), f"Убедитесь, что при изменении задачи по ключу {change_key} данные успешно обновляются."

    @pytest.mark.parametrize(
        "key, invalid_data",
        [
            ("priority", "invalid priority"),
            ("status", "invalid status"),
            ("due_date", "invalid_due_date"),
        ],
    )
    def test_invalid_input_data(self, key, invalid_data, override_input):
        override_input["input"] = mock_input(["1", key, invalid_data])
        task_manager = TaskManager()
        try:
            task_manager.edit_task()
        except InvalidInputData:
            pass
        else:
            assert (
                False
            ), f"Убедитесь, что при передачи невалидных {key, invalid_data} возникает исключение."

    @pytest.mark.parametrize(
        "invalid_due_date", ("1995-01-01", "24-11-15", "2024-11", "2024_11_30")
    )
    def test_early_due_date(self, override_input, invalid_due_date):
        override_input["input"] = mock_input(["1", "due_date", invalid_due_date])
        task_manager = TaskManager()
        try:
            task_manager.edit_task()
        except InvalidInputData:
            pass
        else:
            assert False, "Убедитесь, что невалидные даты недопускаются."

    def test_delete_task(self, storage):
        storage.delete_task(("id", 1))
        assert not storage.cache, "Убедитесь, что задача удаляется."

    @pytest.mark.parametrize(
        "search_data",
        [
            ("category", "test category"),
            ("status", "Не выполнена"),
            ("keywords", ["test", "first"]),
        ],
    )
    def test_search_not_exists_task(self, storage, search_data):
        storage.search_task(search_data)
        assert (
            not storage.cache
        ), "Убедитесь, что поиск по несуществующим значения не находит задачи."

    @pytest.mark.parametrize("delete_data", [("id", 1), ("category", "some category")])
    def test_delete_not_exists_task(self, storage, delete_data):
        try:
            storage.delete_task(delete_data)
        except DataDoesNotExists:
            pass
        else:
            assert False, "Убедитесь, что при удаление несуществующей задачи возникает исключение."

    def test_edit_not_exists_task(self, storage):
        edit_data = (1, "category", "some category")
        try:
            storage.edit_task(edit_data)
        except DataDoesNotExists:
            pass
        else:
            assert False, "Убедитесь, что при изменении несуществующей задачи возникает исключение."
