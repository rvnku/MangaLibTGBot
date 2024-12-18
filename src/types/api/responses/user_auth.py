from typing import TypedDict
from src.types.api.base_types import user_auth


class UserAuthResponse(TypedDict):
    data: user_auth
