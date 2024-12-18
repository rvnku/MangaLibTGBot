from typing import TypedDict, Dict


class auth_metadata(TypedDict):
    auth_domains: Dict[int, str]
