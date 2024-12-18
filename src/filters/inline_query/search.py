from aiogram.filters import BaseFilter
from aiogram.types import InlineQuery
from typing import Literal, Union, Dict, Any

from src.utils import get_site_id

import re


class SearchInlineQueryFilter(BaseFilter):
    async def __call__(self, query: InlineQuery) -> Union[Literal[False], Dict[str, Any]]:
        pattern = r'^\s*(?:((manga|yaoi|slash|ranobe|hentai|anime|[1-5]):)\s*(\S.+)|(?!(manga|yaoi|slash|ranobe|hentai|anime|[1-5]):)(\S.+))$'
        if match := re.fullmatch(pattern, query.query):
            if site := match.group(2):
                return {
                    'site': int(site) if site.isdigit() else get_site_id(site),
                    'query': match.group(3)
                }
            else:
                return {
                    'site': None,
                    'query': match.group(5)
                }
