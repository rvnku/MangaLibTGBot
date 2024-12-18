from typing import TypedDict, List

from src.types.api.base_types import bookmark


class UserBookmarksResponse(TypedDict):
    data: List[bookmark]
