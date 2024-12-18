from typing import TypedDict, Union, Literal
from src.types.api.models import anime, manga


class meta(TypedDict):
    country: Literal['RU']

class TitleResponse(TypedDict):
    data: Union[anime, manga]
    meta: meta
