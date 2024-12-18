from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.filters import ExceptionTypeFilter
from aiogram.types import Message, LinkPreviewOptions, ErrorEvent
from fix.utils.formatting import (
    as_numbered_list, as_list,
    Bold, Code, BotCommand, Text
)
from src.database.user import User
from src.exceptions import UnknownArgument
from src.filters.command import CommandLogin, CommandLogout
from src.utils.api import requests


router = Router()


@router.message(CommandLogin(with_token=True))
async def command_login(message: Message, token: str):
    response = requests.get_user(site_id=1, token=token)
    user = User(message.from_user.id)
    if 'username' in response['data']:
        await user.login(response['data']['id'], token)
        await message.answer(Text(
            f'Вы успешно вошли как «{response['data']['username']}»'
        ).as_html())
        await message.delete()
    else:
        raise UnknownArgument(token)


@router.message(CommandLogin())
async def command_login(message: Message):
    await message.answer(
        parse_mode=ParseMode.HTML,
        link_preview_options=LinkPreviewOptions(is_disabled=True),
        text=as_list(
            Bold('На данный момент доступен только 1 способ авторизации:'),
            as_numbered_list(
                Text('Перейдите на сайт на котором вы авторизованы, либо авторизуйтесь на нём.'),
                Text('Откройте «панель разработчика» горячими клавишами ', Code('Ctrl + Shift + I'), ' или ', Code('Cmd + Shift + I'), '.'),
                Text('Перейдите на вкладку «Сеть» («Network»), в поле «Фильтр» («Filter») введите ', Code('api2.mangalib.me'), ', под ним выберите ', Code('Fetch/XHR'), '.'),
                Text('Перезагрузите страницу, на панели разработчика появятся запросы, нажмите на любой из них в столбце «Имя» («Name»).'),
                Text('В появившемся окне перейдите во вкладку «Заголовки» («Headers») и найдите «Заголовки запросов» («Request Headers»).'),
                Text('Там вы должны найти поле ', Code('Authorization'), ', в значении которого идёт ', Code('Bearer'), ', и за ним – ', Bold('ваш токен'), '!'),
                Text('Копируйте его и присылайте вместе с командой ', BotCommand('/login'), '.')
            ),
        ).as_html()
    )


@router.message(CommandLogout())
async def command_logout(message: Message):
    user = User(message.from_user.id)
    await user.logout()
    await message.answer('Вы успешно вышли из системы. Токен учётной записи удалён.')


@router.error(ExceptionTypeFilter(UnknownArgument), F.update.message.as_('message'))
async def command_login_exception(error: ErrorEvent, message: Message) -> None:
    if isinstance(error.exception, UnknownArgument):
        await message.answer(
            parse_mode=ParseMode.HTML,
            text=as_list(
                Text('Полученное значение токена имеет ошибочный формат или больше не действительно.'),
                Text('Для получения инструкции по авторизации введите ', BotCommand('/login'), '.')
            ).as_html()
        )
