from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from src.middlewares import RestrictMiddleware
from src.handlers import start, search, auth, title
from src.utils.config import config
from src.database import init_database


async def main() -> None:
    dp = Dispatcher()
    bot = Bot(
        token=config.bot_token,
        dispatcher=DefaultBotProperties(
            parse_mode=ParseMode.HTML
        )
    )
    dp.update.middleware(RestrictMiddleware())
    dp.include_routers(start.router, search.router, auth.router, title.router)

    await init_database()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
