from aiogram.filters import Filter
from aiogram.types import Message, ContentType
from typing import Literal, Union, Dict, Any

from src.database.context import Context
from src.database.states import State
from src.utils.config import config


class CatalogQueryMessageFilter(Filter):
    async def __call__(self, message: Message) -> Union[Literal[False], Dict[str, Any]]:
        if not message.text or message.text.startswith('/') or len(message.text) < 2:
            return False
        if message.content_type != ContentType.TEXT:
            return False

        if message.reply_to_message and message.reply_to_message.from_user.username == config.bot_username:
            context = await Context.get_context_from(message.reply_to_message.message_id)
        else:
            context = await Context.get_last_from(message.from_user.id, message.chat.id)
        if not context or context.state != State.catalog_page:
            return False

        context.data['filters']['q'] = message.text
        context.data['meta'] = {
            'item': 0,
            'slug_urls': [],
            'last_page': False
        }

        return {'context': context}
