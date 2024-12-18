from typing import TypedDict


meta = TypedDict('meta', {
    'current_page': int,
    'from': int,
    'has_next_page': bool,
    'page': int,
    'path': str,
    'per_page': int,
    'seed': str,
    'to': int
})
