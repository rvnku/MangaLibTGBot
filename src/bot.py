from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from cloudscraper import CloudScraper
from src.middlewares import CloudflareMiddleware, RestrictMiddleware
from src.handlers import start, search, authorization, title
from src.config import config


async def main(scraper: CloudScraper) -> None:
    dp = Dispatcher()
    bot = Bot(
        token=config.bot_token,
        dispatcher=DefaultBotProperties(
            parse_mode=ParseMode.HTML
        )
    )
    dp.update.middleware(CloudflareMiddleware(scraper))
    dp.update.middleware(RestrictMiddleware())
    dp.include_routers(start.router, search.router, authorization.router, title.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
