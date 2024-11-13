from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from typing import Callable, Dict, Any, Awaitable
from cloudscraper import CloudScraper


class CloudflareMiddleware(BaseMiddleware):
    def __init__(self, scraper: CloudScraper):
        super().__init__()
        self.scraper = scraper

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        data['request'] = self.scraper
        await handler(event, data)
        return
