from typing import TypedDict, Literal, Optional
from src.types.api.base_types import (
    cover,
    subscription
)


class people(TypedDict):
    alt_name: Optional[str]
    confirmed: Optional[bool]
    cover: cover
    id: int
    model: Literal['people']
    name: str
    rus_name: Optional[str]
    slug: str
    slug_url: str
    subscription: subscription
    user_id: int
