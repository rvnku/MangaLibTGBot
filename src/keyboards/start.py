from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton
from typing import Dict, Any


async def generate_start_keyboard_markup() -> Dict[str, Any]:
    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        InlineKeyboardButton(
            text='Поиск на всех сайтах',
            switch_inline_query_current_chat=''
        )
    )
    buttons = {
        'manga': 'Манга',
        'ranobe': 'Ранобэ',
        'anime': 'Аниме'
    }
    keyboard.row(*(
        InlineKeyboardButton(
            text=name,
            switch_inline_query_current_chat=code + ': '
        )
        for code, name in buttons.items()
    ))
    return {
        'reply_markup': keyboard.as_markup()
    }
