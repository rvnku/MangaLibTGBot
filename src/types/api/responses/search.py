from typing import TypedDict, Union, List
from src.types.api.models import anime, manga
from src.types.api.base_types import links, meta


class SearchResponse(TypedDict):
    data: List[Union[anime, manga]]
    links: links
    meta: meta
