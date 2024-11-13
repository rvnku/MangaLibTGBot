from aiogram import Router, Bot
from aiogram.enums import ParseMode
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent, LinkPreviewOptions
from typing import List, Any, Dict
from fix.utils.formatting import BotCommand
from src.types import Request
import urllib.parse

router = Router()


def fetch_titles_all_sites(query: str, page: int = 1, *, request: Request) -> Dict[int, List[Any]]:
    if len(query) < 2:
        return dict()
    url = 'https://api.lib.social/api/{type}?fields[]=rate_avg&fields[]=rate&fields[]=releaseDate&q={q}&site_id[]={id}&page={page}'
    sites = [
        {'type': 'manga', 'id': 1},
        # {'type': 'manga', 'id': 2},
        {'type': 'manga', 'id': 3},
        # {'type': 'manga', 'id': 4},
        {'type': 'anime', 'id': 5},
    ]
    return {
        site['id']: request.get(url.format(**site, q=urllib.parse.quote_plus(query), page=page)).json()['data']
        for site in sites
    }


def get_list_of_titles(query: str, offset: int, count: int = 5, *, request: Request, username: str):
    command = {
        1: 'manga',
        2: 'slash',
        3: 'ranobe',
        4: 'hentai',
        5: 'anime'
    }
    results = []
    page = offset // (60 // count) + 1
    offset %= 60 // count
    for site_id, title_list in fetch_titles_all_sites(query, page=page, request=request).items():
        for title in title_list[offset*count:offset*count+count]:
            results.append(InlineQueryResultArticle(
                id=str(title['id']),
                title=title['rus_name'] or title['eng_name'] or title['name'],
                description='%s  %s' % (title['type']['label'], title['releaseDateString']),
                thumbnail_url=title['cover']['thumbnail'],
                input_message_content=InputTextMessageContent(
                    parse_mode=ParseMode.HTML,
                    link_preview_options=LinkPreviewOptions(prefer_small_media=True),
                    message_text=BotCommand(
                        f'/{command[title['site']]}@{username} {title['slug_url']}'
                    ).as_html()
                )
            ))
    return results


@router.inline_query()
async def search(query: InlineQuery, request: Request, bot: Bot):
    if len(query.query) < 2:
        return await query.answer(results=[], is_personal=True)
    offset = int(query.offset) if query.offset else 0
    results = get_list_of_titles(query.query, offset, request=request, username=(await bot.me()).username.lower())
    await query.answer(results=results, is_personal=False, next_offset=f'{offset + 1}')
