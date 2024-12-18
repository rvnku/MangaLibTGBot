from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton

from src.database.context import Context
from src.database.states import State
from src.types.callback_data.title import (
    CatalogCallbackData,
    FilterCallbackData,
    FieldFilterCallbackData,
    ReadCallbackData
)
from src.utils import (
    get_filter_sections_list,
    get_other_filter_section_list,
    get_title_link
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
from typing import Optional, Dict, Any
import regex

from src.utils.main import filter_section_getter


async def generate_title_keyboard_markup(
    context: Context,
) -> Dict[str, Any]:
    slug_url: Optional[str] = context.data['slug_url']
    is_catalog: bool = State.catalog_page == context.state
    site_id: int = context.site_id

    keyboard = InlineKeyboardBuilder()
    if is_catalog:
        buttons = [
            {
                'filters': 'Фильтры',
                'sorting': 'Сортировка'
            },
            {
                'back': '🡠 Предыдущий',
                'close': '✖',
                'next': 'Следующий 🡢'
            }
        ]
        for row in buttons:
            keyboard.row(*(
                InlineKeyboardButton(
                    text=text,
                    callback_data=CatalogCallbackData(action=action).pack()
                ) for action, text in row.items()
            ))
    keyboard.row(
        InlineKeyboardButton(
            text='Начать ' + ('смотреть' if site_id == 5 else 'читать'),
            callback_data=ReadCallbackData().pack()
        ),
        InlineKeyboardButton(
            text='На страницу тайтла',
            url=get_title_link(
                site_id=site_id,
                slug_url=slug_url
            )
        )
    )
    return {
        'reply_markup': keyboard.as_markup()
    }


async def generate_filters_editor_keyboard_markup(
    context: Context
) -> Dict[str, Any]:
    site_id: int = context.site_id
    authorized: bool = not not context.user_id
    buttons = {
        'q': 'Очистить запрос',
        'genres': 'Жанры',
        'tags': 'Теги',
        'chap_count': 'Количество глав',
        'episodes': 'Количество эпизодов',
        'year': 'Год релиза',
        'rating': 'Оценка',
        'rate': 'Количество оценок',
        'caution': 'Возрастной рейтинг',
        'types': 'Тип',
        'format': 'Формат выпуска',
        'status': 'Статус тайтла',
        'scanlate_status': 'Статус перевода',
        'other': 'Другое',
        'bookmarks': 'Мои списки'
    }
    keyboard = InlineKeyboardBuilder()
    keyboard.add(*(
        InlineKeyboardButton(
            text=text,
            callback_data=FilterCallbackData(section=section).pack()
        )
        for section, text in buttons.items()
        if section in get_filter_sections_list(site_id, authorized)
    ))
    keyboard.adjust(1)
    keyboard.row(
        InlineKeyboardButton(
            text='Сбросить',
            callback_data=CatalogCallbackData(action='filters_clear').pack()
        ),
        InlineKeyboardButton(
            text='Применить',
            callback_data=CatalogCallbackData(action='nothing').pack()
        )
    )
    return {
        'reply_markup': keyboard.as_markup()
    }


async def generate_filter_sections_editor_keyboard_markup(
    context: Context,
    *,
    section: str,
    setting_page: Optional[int] = None
) -> Dict[str, Any]:
    site_id: int = context.site_id
    keyboard = InlineKeyboardBuilder()
    storage = {
        'bookmarks': filter_section_getter(context.data['bookmarks'], site_id),
        'caution': filter_section_getter(AGE_RESTRICTION, site_id),
        'format': filter_section_getter(FORMAT, site_id),
        'genres': filter_section_getter(GENRES, site_id),
        'other': filter_section_getter(get_other_filter_section_list(), site_id),
        'scanlate_status': filter_section_getter(SCANLATE_STATUS, site_id),
        'status': filter_section_getter(STATUS, site_id),
        'tags': filter_section_getter(TAGS, site_id),
        'types': filter_section_getter(TYPES, site_id)
    }[section]

    match section:
        case 'q':
            ...
        case 'genres' | 'tags':
            keyboard.add(*(
                InlineKeyboardButton(
                    text=field['name'],
                    callback_data=FieldFilterCallbackData(
                        section=section,
                        id=field['id'],
                        setting_page=setting_page
                    ).pack()
                )
                for field in storage(setting_page)
            ))
            keyboard.adjust(2)
            keyboard.row(
                InlineKeyboardButton(
                    text='🡠 Предыдущая',
                    callback_data=FilterCallbackData(
                        section=section,
                        setting_page=(setting_page or 0) - 1
                    ).pack()
                ),
                InlineKeyboardButton(
                    text='Следующая 🡢',
                    callback_data=FilterCallbackData(
                        section=section,
                        setting_page=(setting_page or 0) + 1
                    ).pack()
                )
            )
        case 'chap_count' | 'episodes' | 'year' | 'rating' | 'rate':
            ...
        case 'caution' | 'types' | 'format' | 'status' | 'scanlate_status' | 'format' | 'bookmarks' | 'other':
            named = section in ('format', 'bookmarks', 'other')
            keyboard.add(*(
                InlineKeyboardButton(
                    text=field['name'] if named else field['label'],
                    callback_data=FieldFilterCallbackData(
                        section=section,
                        id=field['id']
                    ).pack()
                )
                for field in [
                    {**field, 'name': '.' if regex.fullmatch(r'[\p{Z}\p{C}]*', field['name']) else field['name']} if 'name' in field else field
                    for field in storage()
                ]
            ))
            keyboard.adjust(1 if section == 'other' else 2)

    keyboard.row(
        InlineKeyboardButton(
            text='🡠 Назад',
            callback_data=CatalogCallbackData(action='filters').pack()
        ),
        InlineKeyboardButton(
            text='Применить',
            callback_data=CatalogCallbackData(action='nothing').pack()
        )
    )
    return {
        'reply_markup': keyboard.as_markup()
    }
