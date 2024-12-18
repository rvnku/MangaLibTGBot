from typing import TypedDict
from . import file


class user(TypedDict):
    avatar: file
    id: int
    last_online_at: None
    username: str
