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
    for code, name in buttons.items():
        keyboard.add(
            InlineKeyboardButton(
                text=name,
                switch_inline_query_current_chat=code + ': '
            )
        )
    return {
        'keyboard': keyboard.as_markup()
    }
