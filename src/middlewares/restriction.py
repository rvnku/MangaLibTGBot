from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update
from typing import Callable, Dict, Any, Awaitable, Literal
from src.config import config
import re


class RestrictMiddleware(BaseMiddleware):
    def __init__(self):
        super().__init__()
        self.mode: Literal['production', 'development'] = config.mode
        self.author_id: str = config.author_id
        self.forum_id: str = config.forum_id
        self.flood_topic_id: str = config.flood_topic_id

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        bot_username: str = (await event.bot.get_me()).username
        if self.mode == 'development':
            if isinstance(event, Update) and (message := event.message):
                if (message.chat.type == 'private' and str(message.from_user.id) != self.author_id) or \
                    (message.chat.type in ('group', 'supergroup') and (match := re.fullmatch(r'/\w{1,32}@(\w{5,32}).*', message.text.lower())) and match.group(1) == bot_username):
                    await event.message.reply(
                        text='Бот находится в режиме тестирования.\n'
                                'Используйте более стабильную версию бота: @MangaLibDevBot.\n'
                                'Вся информация есть на форуме в телеграм: @mangalib_bot_community.'
                    )
                    return
        if isinstance(event, Update) and (message := event.message):
            if str(message.chat.id) == self.forum_id and str(message.message_thread_id) != self.flood_topic_id:
                return
        await handler(event, data)
        return
