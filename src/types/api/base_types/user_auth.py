from typing import TypedDict, List, Any
from . import file, id_name, enabled, auth_metadata


class user_auth(TypedDict):
    avatar: file
    balance: int
    id: int
    last_online_at: str
    metadata: auth_metadata
    permissions: List[id_name]
    premium: enabled
    roles: List[Any]
    rolesInTeams: List[Any]
    teams: List[Any]
    username: str
