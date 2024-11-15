from __future__ import annotations
from typing import TypedDict, Literal, List, Optional, Union, Type


class anime(TypedDict):
    ageRestriction: id_object
    artists: List[people]
    authors: List[people]
    background: file
    close_view: int
    cover: cover
    eng_name: Optional[str]
    episodes_schedule: List
    franchise: List[franchise]
    genres: List[genre_tag]
    id: int
    is_licensed: bool
    items_count: items_count
    metadata: metadata
    model: Literal['anime']
    moderated: id_object
    name: str
    otherNames: List[str]
    publisher: publisher
    rating: rating
    releaseDate: str
    releaseDateString: str
    rus_name: Optional[str]
    shiki_rate: float
    shikimori_href: str
    site: Literal[5]
    slug: str
    slug_url: str
    status: id_object
    summary: str
    tags: List[genre_tag]
    teams: List[team]
    time: time
    type: id_object
    user: user
    views: views

class manga(TypedDict):
    ageRestriction: id_object
    artists: List[people]
    authors: List[people]
    background: file
    close_view: int
    cover: cover
    eng_name: Optional[str]
    format: List[format]
    franchise: List[franchise]
    genres: List[genre_tag]
    id: int
    is_licensed: bool
    items_count: items_count
    metadata: metadata
    model: Literal['manga']
    moderated: id_object
    name: str
    otherNames: List[str]
    publisher: publisher
    rating: rating
    releaseDate: str
    releaseDateString: str
    rus_name: Optional[str]
    scanlateStatus: id_object
    site: Literal[1, 2, 3, 4]
    slug: str
    slug_url: str
    status: id_object
    summary: str
    tags: List[genre_tag]
    teams: List[team]
    type: id_object
    user: user
    views: views

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

class publisher(TypedDict):
    cover: cover
    id: int
    model: Literal['publisher']
    name: str
    rus_name: Optional[str]
    slug: str
    slug_url: str
    subscription: subscription[Literal['publisher']]

class team(TypedDict):
    cover: cover
    details: details
    id: int
    model: Literal['team']
    name: str
    slug: str
    slug_url: str

class franchise(TypedDict):
    id: int
    model: Literal['franchise']
    name: str
    slug: str
    slug_url: str

class id_object(TypedDict):
    id: int
    label: str

class file(TypedDict):
    filename: str
    url: str

class cover(TypedDict):
    default: str
    filename: str
    md: str
    thumbnail: str

class subscription(TypedDict):
    is_subscribed: bool
    relation: None
    source_id: int
    source_type: str

class format(TypedDict):
    id: int
    name: str
    pivot: pivot

class pivot(TypedDict):
    manga_id: int
    format_id: int

class genre_tag(TypedDict):
    adult: bool
    alert: bool
    id: int
    name: str

class items_count(TypedDict):
    uploaded: int
    total: int

class metadata(TypedDict):
    close_comments: int
    count: count

class count(TypedDict):
    branches: int
    characters: characters
    covers: int
    people: int
    relations: int
    reviews: reviews

class characters(TypedDict):
    Main: int
    Supporting: int

class reviews(TypedDict):
    all: int
    negative: int
    neutral: int
    positive: int

class rating(TypedDict):
    average: str
    averageFormated: str
    user: int
    votes: int
    votesFormated: str

class details(TypedDict):
    branch_id: int
    is_active: bool
    subscription_count: None

class user(TypedDict):
    avatar: file
    id: int
    last_online_at: None
    username: str

class views(TypedDict):
    formated: str
    short: str
    total: int

class time(TypedDict):
    value: int
    formated: str


ApiTitleData = Union[manga, anime]
