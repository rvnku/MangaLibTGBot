from typing import TypedDict, Literal
from src.types.api.base_types import (
    cover,
    details
)


class team(TypedDict):
    cover: cover
    details: details
    id: int
    model: Literal['team']
    name: str
    slug: str
    slug_url: str
