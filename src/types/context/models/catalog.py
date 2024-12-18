from typing import TypedDict, Literal, List


class CatalogMeta(TypedDict):
    item: int
    last_page: bool
    slug_urls: List[str]


class CatalogFilters(TypedDict, total=False):
    bookmarks: List[int]
    bookmarks_exclude: List[int]
    buy: Literal[1]
    caution: List[int]
    chap_count_max: int
    chap_count_min: int
    fields: List[str]
    format: List[int]
    format_exclude: List[int]
    genres: List[int]
    genres_exclude: List[int]
    genres_soft_search: Literal[1]
    licensed: Literal[0, 1]
    long_no_translation: Literal[1]
    q: str
    rate_max: int
    rate_min: int
    rating_max: int
    rating_min: int
    scanlate_status: List[int]
    site_id: List[int]
    status: List[int]
    tags: List[int]
    tags_exclude: List[int]
    tags_soft_search: Literal[1]
    types: List[int]
    year_max: int
    year_min: int


class CatalogSorting(TypedDict, total=False):
    sort_by: str
    sort_type: str


class UserBookmark(TypedDict):
    id: int
    name: str
    site_ids: List[int]


class CatalogData(TypedDict):
    slug_url: str
    slug_title: str
    meta: CatalogMeta
    filters: CatalogFilters
    sorting: CatalogSorting
    bookmarks: List[UserBookmark]
