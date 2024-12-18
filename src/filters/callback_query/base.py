from aiogram.filters.callback_data import CallbackQueryFilter
from aiogram.types import CallbackQuery
from typing import Literal, Union, Dict, Any

from src.database.context import Context


class BaseCallbackQueryFilter(CallbackQueryFilter):
    async def __call__(self, callback: CallbackQuery) -> Union[Literal[False], Dict[str, Any]]:
        if not (result := await super().__call__(callback)):
            return False

        context: Context = await Context.get_context_from(callback.message.message_id)
        if context.telegram_id != callback.from_user.id:
            return False

        return {**result, 'context': context}
