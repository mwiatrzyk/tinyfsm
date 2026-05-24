from typing import TypeVar

T = TypeVar("T")


class ExportList(list):

    def __call__(self, func_or_cls: T) -> T:
        name = getattr(func_or_cls, "__name__")
        self.append(name)
        return func_or_cls
