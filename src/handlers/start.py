from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardButton
from fix.utils.formatting import (
    as_list, as_marked_list, Italic,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()


# @router.message(CommandStart(deep_link=True, magic=F.args == 'auth_code_received'))
# async def start_with_auth_handler(message: Message, command: CommandObject):
#     await message.reply(text=f'{html.spoiler(command.args)}')


# @router.message(CommandStart())
# async def start_handler(message: Message):
#     web_app = WebAppInfo(url='https://mangalibbot.github.io/auth/')
#     builder = InlineKeyboardBuilder()
#     builder.add(InlineKeyboardButton(text='inline-mode', switch_inline_query_current_chat=''))
#     builder.add(InlineKeyboardButton(text='WebApp', web_app=web_app))
#     await message.answer(
#         'Привеееет! Нажми на кнопку под этим сообщением, чтобы начать поиск на либе.',
#         reply_markup=builder.as_markup()
#     )


@router.message(CommandStart())
async def cmd_start(message: Message):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(
        text='Поиск манги, ранобэ и аниме',
        switch_inline_query_current_chat=''
    ))
    await message.answer(
        parse_mode=ParseMode.HTML,
        reply_markup=keyboard.as_markup(),
        text=as_list(
            'Приветствую! Это бот посвящённый манге, ранобэ и аниме. В нём ты сможешь:',
            as_marked_list(
                'Найти интересующий тебя тайтл',
                'Прочитать/посмотреть его',
                'Оставить отзывы и комментарии',
                'и многое другое'
            ),
            '',
            Italic('В данный момент бот находится в разработке, и его функционал только появляется.'),
            Italic('По вопросам обращаться на форум в тг: @mangalib_bot_community')
        ).as_html()
    )
