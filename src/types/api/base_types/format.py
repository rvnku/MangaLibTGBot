from typing import TypedDict
from . import pivot


class format(TypedDict):
    id: int
    name: str
    pivot: pivot
