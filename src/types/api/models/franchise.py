from typing import TypedDict, Literal


class franchise(TypedDict):
    id: int
    model: Literal['franchise']
    name: str
    slug: str
    slug_url: str
