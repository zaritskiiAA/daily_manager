class InvalidCommand(Exception):
    """Вызывается в случае получения TaskManager невалидной команды."""

    pass


class InvalidInputData(Exception):
    """Вызывается когда неудалось корректно распарсить данные от клиента."""

    pass


class DataDoesNotExists(Exception):
    """Вызывается когда клиент пробует удалить несущствующую задачу в хранилище."""

    pass
