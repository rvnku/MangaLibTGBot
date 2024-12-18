from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from src.database.user import User
from src.keyboards.start import generate_start_keyboard_markup
from src.messages.start import generate_start_message


router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    user = User(message.from_user.id)
    await user.create()
    await message.answer(
        **(await generate_start_message()),
        **(await generate_start_keyboard_markup())
    )
