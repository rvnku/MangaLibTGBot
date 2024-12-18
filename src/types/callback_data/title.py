from aiogram.filters.callback_data import CallbackData
from typing import Optional


class CatalogCallbackData(CallbackData, prefix='catalog'):
    action: str

class FilterCallbackData(CallbackData, prefix='filter'):
    section: str
    setting_page: Optional[int] = 1

class FieldFilterCallbackData(CallbackData, prefix='filter_id'):
    section: str
    id: int
    setting_page: Optional[int] = 1

class NameFieldFilterCallbackData(CallbackData, prefix='filter_other'):
    section: str

class ReadCallbackData(CallbackData, prefix='read'):
    pass

class TitleCallbackData(CallbackData, prefix='title'):
    pass
