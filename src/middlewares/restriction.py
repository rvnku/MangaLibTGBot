from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update
from typing import Callable, Dict, Any, Awaitable
from src.utils.config import config
import re


class RestrictMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        if config.mode == 'development':
            if isinstance(event, Update) and (message := event.message):
                if ((
                    message.chat.type == 'private'
                    and str(message.from_user.id) not in (config.author_id, config.develop_id)
                ) or (
                    message.chat.type in ('group', 'supergroup')
                    and (match := re.fullmatch(r'/\w{1,32}@(\w{5,32}).*', message.text.lower()))
                    and match.group(1) == config.bot_username
                )):
                    await event.message.reply(
                        text='Бот находится в режиме тестирования.\n'
                             'Используйте более стабильную версию бота: @MangaLibDevBot.\n'
                             'Вся информация есть на форуме в телеграм: @mangalib_bot_community.'
                    )
                    return
        if isinstance(event, Update) and (message := event.message):
            if str(message.chat.id) == config.forum_id and str(message.message_thread_id) != config.flood_topic_id:
                return
        await handler(event, data)
        return
