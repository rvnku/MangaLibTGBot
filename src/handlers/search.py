from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.types import (
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
    LinkPreviewOptions
)
from fix.utils.formatting import BotCommand
from src.database.user import User
from src.filters.inline_query import SearchInlineQueryFilter
from src.types.api import anime, manga
from src.utils.config import config
from src.utils.api import requests
from src.utils import get_site_api_type, get_site_name

from typing import Optional, Union, List


router = Router()


def generate_titles_list(
    site: Optional[int],
    query: str,
    offset: int,
    token: Optional[str] = None
) -> List[InlineQueryResultArticle]:
    articles: List[InlineQueryResultArticle] = []
    response: List[Union[anime | manga]] = []

    if site is None:
        for site in (1, 2, 3, 4, 5):
            page_min = offset // 60 + 1
            page_max = (offset + 5) // 60 + 1
            response.extend(sum(
                (requests.get_titles_from_search(
                    query=query,
                    site_id=site,
                    site_api_type=get_site_api_type(site),
                    page=page,
                    token=token
                )['data']
                for page in range(page_min, page_max + 1)),
                start=[]
            )[offset // 5 % 60 : offset // 5 % 60 + 5])
            offset += 5

    else:
        page_min = offset // 60 + 1
        page_max = (offset + 49) // 60 + 1
        response.extend(sum(
            (requests.get_titles_from_search(
                query=query,
                site_id=site,
                site_api_type=get_site_api_type(site),
                page=page,
                token=token
            )['data']
            for page in range(page_min, page_max + 1)),
            start=[]
        )[offset % 60 : offset % 60 + 50])

    for title in response:
        articles.append(InlineQueryResultArticle(
            id=str(title['id']),
            title=title['rus_name'] or title['eng_name'] or title['name'],  # type: ignore
            description='%s  %s' % (title['type']['label'], title['releaseDateString']),
            thumbnail_url=title['cover']['thumbnail'],
            input_message_content=InputTextMessageContent(
                parse_mode=ParseMode.HTML,
                link_preview_options=LinkPreviewOptions(prefer_small_media=True),
                message_text=BotCommand(
                    f'/{get_site_name(title['site'])}@{config.bot_username.lower()} {title['slug_url']}'
                ).as_html()
            )
        ))
    return articles


@router.inline_query(SearchInlineQueryFilter())
async def search_callback(
    inline_query: InlineQuery,
    site: Optional[int],
    query: str
) -> None:
    user = User(inline_query.from_user.id)
    token = await user.get_token()
    offset = int(inline_query.offset or '0')
    results = generate_titles_list(site, query, offset, token)
    await inline_query.answer(results=results, is_personal=False, next_offset=f'{offset + len(results)}')


@router.inline_query()
async def search_callback(inline_query: InlineQuery) -> bool:
    return await inline_query.answer(results=[], is_personal=True)
