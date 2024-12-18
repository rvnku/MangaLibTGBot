from aiogram.enums import ParseMode
from aiogram.types import LinkPreviewOptions
from typing import Optional, Dict, Any
from sqlalchemy import Enum
from src.database.context import Context
from src.database.states import State
from src.types.api import manga, anime
from src.types.context import CatalogFilters, CatalogMeta, CatalogSorting
from src.exceptions import NotFoundError, ApiException
from src.utils.api import requests
from src.utils import (
    get_site_api_type
)
from fix.utils.formatting import (
    as_list,
    ExpandableBlockQuote,
    BlockQuote,
    Bold,
    Code,
    Text
)
from src.constants import (
    AGE_RESTRICTION,
    FORMAT,
    GENRES,
    SCANLATE_STATUS,
    STATUS,
    TAGS,
    TYPES
)
from src.utils.formatting import (
    text,
    marked_fields,
    select_fields,
    other_fields,
    spoiler_fields,
    interval
)
from src.utils.main import filter_section_getter


async def generate_title_header(context: Context) -> Dict[str, Any]:
    filters: CatalogFilters = context.data['filters']
    slug_url: Optional[str] = context.data['slug_url']
    is_catalog: bool = State.catalog_page == context.state

    return {
        'parse_mode': ParseMode.HTML,
        'text': as_list(
            Bold('Поиск в каталоге:' if is_catalog else 'Информация о тайтле:'),
            BlockQuote(filters.get('q') or '' if is_catalog else Code(slug_url))
        ).as_html()
    }


async def generate_title_message(context: Context) -> Dict[str, Any]:
    state: Optional[Enum[State]] = context.state
    token: Optional[str] = context.user_token
    site_id: int = context.site_id
    slug_url: Optional[str] = context.data['slug_url']

    try:
        if state == State.catalog_page:
            meta: CatalogMeta = context.data['meta']
            filters: CatalogFilters = context.data['filters']
            sorting: CatalogSorting = context.data['sorting']

            if meta['item'] >= len(meta['slug_urls']) and not meta['last_page']:
                response = requests.get_titles_from_catalog(
                    site_id=site_id,
                    filters=filters,
                    sorting=sorting,
                    page=meta['item'] // 60 + 1,
                    token=token
                )
                if not response['links']['next']:
                    meta['last_page'] = True
                meta['slug_urls'].extend(map(lambda _: _['slug_url'], response['data']))

            elif meta['item'] >= len(meta['slug_urls']):
                meta['item'] = len(meta['slug_urls']) - 1
            elif meta['item'] < 0:
                meta['item'] = 0

            try:
                context.data['slug_url'] = slug_url = meta['slug_urls'][meta['item']]
            except IndexError:
                context.data['slug_url'] = None
                raise NotFoundError('silent')

        response = requests.get_title(
            site_id=site_id,
            site_api_type=get_site_api_type(site_id),
            slug_url=slug_url,
            token=token
        )
    except NotFoundError:
        return {
            'parse_mode': ParseMode.HTML,
            'text': Text('Ничего не найдено.').as_html()
        }
    except ApiException as exc:
        return {
            'parse_mode': ParseMode.HTML,
            'text': Text(exc.message).as_html()
        }
    else:
        title = response['data']  # type: ignore
        if title['model'] == 'manga':
            title: manga
            return {
                'parse_mode': ParseMode.HTML,
                'link_preview_options': LinkPreviewOptions(
                    url=title['cover']['default'] or title['cover']['thumbnail'],
                    show_above_text=True,
                    prefer_large_media=True
                ),
                'text': as_list(
                    Bold(title['rus_name']),
                    title['name'],
                    BlockQuote(as_list(
                        Text(
                            Code('⭐ %s' % (title['rating']['average'] or '—')),
                            ' %s' % (title['rating']['votesFormated'] or '—')
                        ),
                        Code('🔞 %s' % (title['ageRestriction']['label'] or '—')),
                        sep='  ·  '
                    )),
                    as_list(
                        Bold(title['type']['label'] or '—'),
                        Bold(title['status']['label'] or '—'),
                        Bold(title['releaseDateString']),
                        as_list(
                            *([Bold(format['name']) for format in title['format']] or [Bold('—')]),
                            sep=' '
                        ),
                        sep='  ·  '
                    ),
                    *((ExpandableBlockQuote(title['summary']),) if title['summary'] else ()),
                    ExpandableBlockQuote(
                        *((as_list(
                            *[Code(genre['name']) for genre in title['genres']],
                            *[Code('#' + tag['name']) for tag in title['tags']],
                            sep='  ·  '
                        ),) if title['genres'] or title['tags'] else ())
                    )
                ).as_html()
            }
        elif title['model'] == 'anime':
            title: anime
            return {
                'parse_mode': ParseMode.HTML,
                'link_preview_options': LinkPreviewOptions(
                    url=title['cover']['default'] or title['cover']['thumbnail'],
                    show_above_text=True,
                    prefer_large_media=True
                ),
                'text': as_list(
                    Bold(title['rus_name']),
                    title['name'],
                    BlockQuote(as_list(
                        Text(
                            Code('⭐ %s' % (title['rating']['average'] or '—')),
                            ' %s' % (title['rating']['votesFormated'] or '—')
                        ),
                        Code('🔞 %s' % (title['ageRestriction']['label'] or '—')),
                        sep='  ·  '
                    )),
                    as_list(
                        Bold(title['type']['label'] or '—'),
                        Bold(title['status']['label'] or '—'),
                        Text(
                            Bold(title['items_count']['uploaded'] or 0),
                            ' из ',
                            Bold(title['items_count']['total'] or 0),
                            (f' [{title['time']['formated'] or '—'}]' if 'time' in title else '')
                        ),
                        Bold(title['releaseDateString'] or '—'),
                        sep='  ·  '
                    ),
                    *((ExpandableBlockQuote(title['summary']),) if title['summary'] else ()),
                    ExpandableBlockQuote(
                        *((as_list(
                            *[Code(genre['name']) for genre in title['genres']],
                            *[Code('#' + tag['name']) for tag in title['tags']],
                            sep='  ·  '
                        ),) if title['genres'] or title['tags'] else ())
                    )
                ).as_html()
            }


async def generate_filters_editor_message(
    context: Context
) -> Dict[str, Any]:
    site_id: int = context.site_id
    filters: CatalogFilters = context.data['filters']

    return {
        'parse_mode': ParseMode.HTML,
        'text': as_list(*(
            as_list(
                Bold(f'{title}:'),
                BlockQuote(value)
            )
            for title, value in {
                'Жанры': spoiler_fields(
                    filters.get('genres'),
                    filters.get('genres_exclude')
                ),
                'Теги': spoiler_fields(
                    filters.get('tags'),
                    filters.get('tags_exclude')
                ),
                'Количество глав': interval(
                    filters.get('chap_count_min'),
                    filters.get('chap_count_max')
                ),
                'Год релиза': interval(
                    filters.get('year_min'),
                    filters.get('year_max')
                ),
                'Оценка': interval(
                    filters.get('rating_min'),
                    filters.get('rating_max')
                ),
                'Количество оценок': interval(
                    filters.get('rate_min'),
                    filters.get('rate_max')
                ),
                'Возрастной рейтинг': select_fields(
                    filters.get('caution'),
                    filter_section_getter(AGE_RESTRICTION, site_id)()
                ),
                'Тип': select_fields(
                    filters.get('types'),
                    filter_section_getter(TYPES, site_id)()
                ),
                'Формат выпуска': marked_fields(
                    filters.get('format'),
                    filters.get('format_exclude'),
                    filter_section_getter(FORMAT, site_id)()
                ),
                'Статус тайтла': select_fields(
                    filters.get('status'),
                    filter_section_getter(STATUS, site_id)()
                ),
                'Статус перевода': select_fields(
                    filters.get('scanlate_status'),
                    filter_section_getter(SCANLATE_STATUS, site_id)()
                ),
                'Другое': other_fields(
                    filters.get('long_no_translation'),
                    filters.get('licensed'),
                    filters.get('buy')
                ),
                'Мои списки': marked_fields(
                    filters.get('bookmarks'),
                    filters.get('bookmarks_exclude'),
                    filter_section_getter(context.data['bookmarks'], site_id)()
                )
            }.items()
            if value
        )).as_html()
    }


async def generate_paginated_filters_editor_message(
    context: Context,
    *,
    section: str
) -> Dict[str, Any]:
    site_id: int = context.site_id
    filters: CatalogFilters = context.data['filters']

    header = {
        'genres': 'Жанры',
        'tags': 'Теги'
    }[section]
    strict_mode = {
        'genres': not filters.get('genres_soft_search'),
        'tags': not filters.get('tags_soft_search')
    }[section]
    fields = {
        'genres': marked_fields(
            filters.get('genres'),
            filters.get('genres_exclude'),
            filter_section_getter(GENRES, site_id)()
        ),
        'tags': marked_fields(
            filters.get('tags'),
            filters.get('tags_exclude'),
            filter_section_getter(TAGS, site_id)()
        )
    }[section]

    return {
        'parse_mode': ParseMode.HTML,
        'text': as_list(
            Bold(header),
            Text(('✅ ' if strict_mode else '🔳 ') + 'Строгое совпадение'),
            BlockQuote(fields or Text('ничего не найдено'))
        ).as_html()
    }
