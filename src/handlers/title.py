from aiogram import Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message, CallbackQuery

from typing import Union, Literal, Optional, Dict, Any

from src.database.context import Context
from src.database.states import State
from src.filters.command import CommandTitle
from src.filters.callback_query import (
    CatalogCallbackQueryFilter,
    FilterCallbackQueryFilter,
    TitleCallbackQueryFilter, FieldFilterCallbackQueryFilter
)
from src.filters.common import CatalogQueryMessageFilter
from src.messages import (
    generate_filters_editor_message,
    generate_paginated_filters_editor_message,
    generate_title_header,
    generate_title_message
)
from src.keyboards import (
    generate_filter_sections_editor_keyboard_markup,
    generate_filters_editor_keyboard_markup,
    generate_title_keyboard_markup
)
from src.types.callback_data import (
    CatalogCallbackData,
    FilterCallbackData,
    TitleCallbackData, FieldFilterCallbackData
)
from src.types.context import (
    CatalogFilters
)
from src.utils import clear_filters
from src.constants import GENRES, TAGS
from src.utils.main import filter_section_getter

router = Router()


@router.message(CommandTitle())
async def command_title(
    message: Message,
    context: Context
) -> None:
    title_header = await generate_title_header(context)
    title_message = await generate_title_message(context)
    title_keyboard_markup = await generate_title_keyboard_markup(context)

    head_message = await message.answer(**title_header)
    body_message = await message.answer(**title_message, **title_keyboard_markup)

    context.head_message_id = head_message.message_id
    context.body_message_id = body_message.message_id

    await context.save()


@router.callback_query(TitleCallbackQueryFilter())
@router.callback_query(CatalogCallbackQueryFilter('nothing', 'back', 'next', 'close'))
async def callback_title(
    callback_query: CallbackQuery,
    callback_data: Union[TitleCallbackData, CatalogCallbackData],
    context: Context
) -> None:
    if isinstance(callback_data, CatalogCallbackData):
        action: str = callback_data.action

        match action:
            case 'back' | 'next':
                def get_offset():
                    match action:
                        case 'back': return -1
                        case 'next': return +1

                match (context.data['meta'], action):
                    case ({'last_item': True}, 'next') | ({'item': 0}, 'back'):
                        await callback_query.answer()
                        return
                    case (meta, _):
                        meta['item'] += get_offset()
                        context.data['meta'] = meta

            case 'close':
                context.state = State.title_page
                context.data = {
                    'slug_url': context.data['slug_url']
                }

            case 'nothing':
                context.data['meta'] = {
                    'item': 0,
                    'slug_urls': [],
                    'last_page': False
                }

    title_message = await generate_title_message(context)
    title_keyboard_markup = await generate_title_keyboard_markup(context)

    try:
        await callback_query.message.edit_text(**title_message)
    except TelegramBadRequest:
        pass
    try:
        await callback_query.message.edit_reply_markup(**title_keyboard_markup)
    except TelegramBadRequest:
        pass

    await context.save()


@router.callback_query(CatalogCallbackQueryFilter('filters', 'filters_clear'))
async def callback_catalog_filter(
    callback_query: CallbackQuery,
    callback_data: CatalogCallbackData,
    context: Context
) -> None:
    filters: CatalogFilters = context.data['filters']

    if callback_data.action == 'filters_clear':
        context.data['filters'] = clear_filters(filters)

    title_message = await generate_filters_editor_message(context)
    title_keyboard_markup = await generate_filters_editor_keyboard_markup(context)

    try:
        await callback_query.message.edit_text(**title_message)
    except TelegramBadRequest:
        pass
    try:
        await callback_query.message.edit_reply_markup(**title_keyboard_markup)
    except TelegramBadRequest:
        pass

    await context.save()


@router.callback_query(FilterCallbackQueryFilter())
async def callback_catalog_filter_section(
    callback_query: CallbackQuery,
    callback_data: FilterCallbackData,
    context: Context
) -> None:
    site_id: int = context.site_id
    section: str = callback_data.section

    title_header: Optional[Dict[str, Any]] = None
    title_message: Optional[Dict[str, Any]] = None
    title_keyboard_markup: Optional[Dict[str, Any]] = None

    match section:
        case 'q':
            if 'q' in context.data['filters']:
                del context.data['filters']['q']
            else:
                await callback_query.answer()
                return

            title_header = await generate_title_header(context)
            title_message = await generate_filters_editor_message(context)
            title_keyboard_markup = await generate_filters_editor_keyboard_markup(context)

        case 'genres' | 'tags':
            storage = {
                'genres': filter_section_getter(GENRES, site_id),
                'tags': filter_section_getter(TAGS, site_id)
            }[section]
            if callback_data.setting_page <= 0:
                callback_data.setting_page = 0
                await callback_query.answer()
                return
            if callback_data.setting_page > (len(storage()) - 1) // 16 + 1:
                callback_data.setting_page = (len(storage()) - 1) // 16 + 1
                await callback_query.answer()
                return

            title_message = await generate_paginated_filters_editor_message(
                context, section=section
            )
            title_keyboard_markup = await generate_filter_sections_editor_keyboard_markup(
                context, section=section, setting_page=callback_data.setting_page
            )
        case _:
            title_keyboard_markup = await generate_filter_sections_editor_keyboard_markup(
                context, section=section, setting_page=callback_data.setting_page
            )

    if title_header:
        try:
            await callback_query.bot.edit_message_text(
                **title_header,
                chat_id=callback_query.message.chat.id,
                message_id=context.head_message_id
            )
        except TelegramBadRequest:
            pass
    if title_message:
        try:
            await callback_query.message.edit_text(**title_message)
        except TelegramBadRequest:
            pass
    if title_keyboard_markup:
        try:
            await callback_query.message.edit_reply_markup(**title_keyboard_markup)
        except TelegramBadRequest:
            pass

    await context.save()


@router.callback_query(FieldFilterCallbackQueryFilter())
async def callback_catalog_filter_field(
    callback_query: CallbackQuery,
    callback_data: FieldFilterCallbackData,
    context: Context
) -> None:
    filters: CatalogFilters = context.data['filters']
    setting_page: int = callback_data.setting_page
    section: str = callback_data.section
    id: int = callback_data.id

    match section:
        case 'caution' | 'types' | 'status' | 'scanlate_status':
            section: Literal['caution', 'types', 'status', 'scanlate_status']

            # include -> empty
            if section in filters and id in filters[section]:
                filters[section].remove(id)
                if not filters[section]:
                    del filters[section]

            # emtpy -> include
            else:
                if section not in filters:
                    filters[section] = []
                filters[section].append(id)

        case 'genres' | 'tags' | 'format' | 'bookmarks':
            section: Literal['genres', 'tags', 'format', 'bookmarks']
            section_exclude: Literal[
                'genres_exclude', 'tags_exclude', 'format_exclude', 'bookmarks_exclude'
            ] = section + '_exclude'  # type: ignore

            # include -> exclude
            if section in filters and id in filters[section]:
                filters[section].remove(id)
                if not filters[section]:
                    del filters[section]
                if section_exclude not in filters:
                    filters[section_exclude] = []
                filters[section_exclude].append(id)

            # exclude -> empty
            elif section_exclude in filters and id in filters[section_exclude]:
                filters[section_exclude].remove(id)
                if not filters[section_exclude]:
                    del filters[section_exclude]

            # empty -> include
            else:
                if section not in filters:
                    filters[section] = []
                filters[section].append(id)

    if section in ('genres', 'tags'):
        title_message = await generate_paginated_filters_editor_message(
            context, section=section
        )
    else:
        title_message = await generate_filters_editor_message(context)
    title_keyboard_markup = await generate_filter_sections_editor_keyboard_markup(
        context, section=section, setting_page=setting_page
    )

    try:
        await callback_query.message.edit_text(**title_message)
    except TelegramBadRequest:
        pass
    try:
        await callback_query.message.edit_reply_markup(**title_keyboard_markup)
    except TelegramBadRequest:
        pass

    await context.save()


@router.message(CatalogQueryMessageFilter())
async def callback_catalog_search(
    message: Message,
    context: Context
) -> None:
    title_header = await generate_title_header(context)
    title_message = await generate_title_message(context)
    title_keyboard_markup = await generate_title_keyboard_markup(context)

    try:
        await message.bot.edit_message_text(
            **title_header,
            chat_id=message.chat.id,
            message_id=context.head_message_id
        )
    except TelegramBadRequest:
        pass
    try:
        await message.bot.edit_message_text(
            **title_message,
            chat_id=message.chat.id,
            message_id=context.body_message_id
        )
    except TelegramBadRequest:
        pass
    try:
        await message.bot.edit_message_reply_markup(
            **title_keyboard_markup,
            chat_id=message.chat.id,
            message_id=context.body_message_id
        )
    except TelegramBadRequest:
        pass
    await message.delete()

    await context.save()
