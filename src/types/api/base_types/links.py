from typing import TypedDict, Optional


class links(TypedDict):
    first: str
    last: Optional[str]
    next: Optional[str]
    prev: Optional[str]
