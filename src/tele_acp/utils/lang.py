from typing import Any, TypeVar

_T = TypeVar("_T")


def try_cast(val: Any, typ: type[_T]) -> _T | None:
    if isinstance(val, typ):
        return val
    return None
