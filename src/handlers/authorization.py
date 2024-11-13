from aiogram import Router, Bot
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandObject
from aiogram.types import Message, LinkPreviewOptions
from fix.utils.formatting import (
    as_numbered_list, as_list,
    Bold, Code, Italic, BotCommand, TextLink, Text, Spoiler
)
from typing import Union, Dict
import re


router = Router(name=__name__)


class CommandLogin(Command):
    def __init__(self, with_token: bool = False):
        super().__init__('login')
        self.with_token = with_token

    async def __call__(self, message: Message, bot: Bot) -> Union[bool, Dict[str, str]]:
        if not (result := await super().__call__(message, bot)):
            return False
        if not self.with_token:
            return True
        command: CommandObject = result['command']
        if command.args and re.fullmatch(r'[-\w.]{988}', command.args):
            return {
                **result,
                'token': command.args
            }
        return False


class CommandLogout(Command):
    def __init__(self):
        super().__init__('logout')


@router.message(CommandLogin(with_token=True))
async def cmd_login(message: Message, token: str):
    await message.delete()
    await message.answer(
        parse_mode=ParseMode.HTML,
        text=Text('Токен успешно получен: ', Spoiler(token)).as_html()
    )


@router.message(CommandLogin())
async def cmd_login(message: Message):
    await message.answer(
        parse_mode=ParseMode.HTML,
        link_preview_options=LinkPreviewOptions(is_disabled=True),
        text=as_list(
            Bold('На данный момент доступен только 1 способ авторизации:'),
            as_numbered_list(
                Text('Перейдите на сайт в ', Italic('новой версии'), ', на котором вы авторизованы, либо авторизируйтесь на нём.'),
                Text('Откройте «панель разработчика» горячими клавишами ', Code('Ctrl + Shift + I'), ' или ', Code('Cmd + Shift + I'), '.'),
                Text('Перейдите на вкладку «Сеть» («Network»), в поле «Фильтр» («Filter») введите ', Code('api.mangalib.me'), ', под ним выберите ', Code('Fetch/XHR'), '.'),
                Text('Перезагрузите страницу, на панели разработчика появятся запросы, нажмите на любой из них в столбце «Имя» («Name»).'),
                Text('В появившемся окне перейдите во вкладку «Заголовки» («Headers») и найдите «Заголовки запросов» («Request Headers»).'),
                Text('Там вы должны найти поле ', Code('Authorization:'), ', в значении которого идёт ', Code('Bearer'), ', и за ним – ', Bold('ваш токен'), '!'),
                Text('Копируйте его и присылайте вместе с командой ', BotCommand('/login'), '.')
            ),
            '',
            Text('К ', Italic('новой версии'), ' сайта относятся домены:'),
            as_list(
                TextLink('test-front.mangalib.me', url='https://test-front.mangalib.me'),
                TextLink('mangalib.org', url='https://mangalib.org'),
                TextLink('v2.slashlib.me', url='https://v2.slashlib.me'),
                TextLink('hentailib.me', url='https://hentailib.me'),
                TextLink('v1.hentailib.org', url='https://v1.hentailib.org'),
                TextLink('ranobelib.me', url='https://ranobelib.me'),
                TextLink('anilib.me', url='https://anilib.me'),
                sep=', '
            )
        ).as_html()
    )


@router.message(CommandLogout())
async def cmd_logout(message: Message):
    await message.answer(
        text=Text('Вы успешно вышли из системы. Токен учётной записи удалён.').as_html()
    )
