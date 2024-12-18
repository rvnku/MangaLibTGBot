from typing import TypedDict, Literal, Optional
from src.types.api.base_types import (
    cover,
    subscription
)


class publisher(TypedDict):
    cover: cover
    id: int
    model: Literal['publisher']
    name: str
    rus_name: Optional[str]
    slug: str
    slug_url: str
    subscription: subscription[Literal['publisher']]
