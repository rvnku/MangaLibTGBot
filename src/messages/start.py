from aiogram.enums import ParseMode

from typing import Dict, Any
from fix.utils.formatting import (
    as_list,
    as_marked_list,
    Italic
)


async def generate_start_message() -> Dict[str, Any]:
    return {
        'parse_mode': ParseMode.HTML,
        'text': as_list(
            'Приветствую! Это бот посвящённый манге, ранобэ и аниме. В нём ты сможешь:',
            as_marked_list(
                'Найти интересующий тебя тайтл',
                'Прочитать/посмотреть его',
                'Оставить отзывы и комментарии',
                'и многое другое'
            ),
            '',
            Italic('В данный момент бот находится в разработке, и его функционал только появляется.'),
            Italic('По вопросам обращаться на форум в тг: @mangalib_bot_community')
        ).as_html()
    }
