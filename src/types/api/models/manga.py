from typing import TypedDict, Literal, Optional, List
from src.types.api.base_types import (
    cover,
    file,
    format,
    genre_tag,
    id_label,
    items_count,
    title_metadata,
    rating,
    user,
    views
)
from src.types.api.models import (
    franchise,
    people,
    publisher,
    team
)


class manga(TypedDict):
    ageRestriction: id_label
    artists: Optional[List[people]]
    authors: Optional[List[people]]
    background: Optional[file]
    close_view: Optional[int]
    cover: cover
    eng_name: Optional[str]
    format: Optional[List[format]]
    franchise: Optional[List[franchise]]
    genres: Optional[List[genre_tag]]
    id: int
    is_licensed: bool
    items_count: Optional[items_count]
    metadata: Optional[title_metadata]
    model: Literal['manga']
    moderated: Optional[id_label]
    name: str
    otherNames: Optional[List[str]]
    publisher: Optional[publisher]
    rating: Optional[rating]
    releaseDate: Optional[str]
    releaseDateString: str
    rus_name: Optional[str]
    scanlateStatus: Optional[id_label]
    site: Literal[1, 2, 3, 4]
    slug: str
    slug_url: str
    status: Optional[id_label]
    summary: Optional[str]
    tags: Optional[List[genre_tag]]
    teams: Optional[List[team]]
    type: id_label
    user: Optional[user]
    views: Optional[views]
