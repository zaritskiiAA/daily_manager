from typing import Iterable


class mock_input:
    def __init__(self, return_value: Iterable[str]) -> None:
        self.return_value = iter(return_value)
        self.outputs = []

    def __call__(self, string: str) -> str:
        self.outputs.append(string)
        value = next(self.return_value)
        return value
