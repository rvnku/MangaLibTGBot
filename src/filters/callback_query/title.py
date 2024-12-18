from aiogram import F
from src.filters.callback_query import BaseCallbackQueryFilter
from src.types.callback_data import (
    CatalogCallbackData,
    FilterCallbackData,
    FieldFilterCallbackData,
    NameFieldFilterCallbackData,
    TitleCallbackData
)


class TitleCallbackQueryFilter(BaseCallbackQueryFilter):
    def __init__(self) -> None:
        super().__init__(callback_data=TitleCallbackData)

class CatalogCallbackQueryFilter(BaseCallbackQueryFilter):
    def __init__(self, *actions: str) -> None:
        super().__init__(callback_data=CatalogCallbackData, rule=F.action.in_(actions) if actions else None)

class FilterCallbackQueryFilter(BaseCallbackQueryFilter):
    def __init__(self, *sections: str) -> None:
        super().__init__(callback_data=FilterCallbackData, rule=F.section.in_(sections) if sections else None)

class FieldFilterCallbackQueryFilter(BaseCallbackQueryFilter):
    def __init__(self, *ids: int) -> None:
        super().__init__(callback_data=FieldFilterCallbackData, rule=F.telegram_id.in_(ids) if ids else None)

class NamedFilterCallbackQueryFilter(BaseCallbackQueryFilter):
    def __init__(self, *sections: str):
        super().__init__(callback_data=NameFieldFilterCallbackData, rule=F.section.in_(sections) if sections else None)
