from typing import TypedDict, List


class bookmark(TypedDict):
    color: str
    count: int
    id: int
    name: str
    notify: bool
    order: int
    public: bool
    site_ids: List[int]
    textColor: str
