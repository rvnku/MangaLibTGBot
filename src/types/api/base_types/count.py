from typing import TypedDict
from . import characters, reviews


class count(TypedDict):
    branches: int
    characters: characters
    covers: int
    people: int
    relations: int
    reviews: reviews
