import os

import pytest

from manager_app.storage import TaskStorage


@pytest.fixture(scope="class")
def storage():
    TaskStorage._filename = "test.json"
    storage = TaskStorage()
    storage.refresh([])
    yield storage
    os.remove(TaskStorage._filename)


@pytest.fixture()
def override_input():
    yield __builtins__
    __builtins__["input"] = input
