from aiogram import Bot
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from src.exceptions import UnknownArgument

from typing import Union, Dict, Any
import re


class CommandLogin(Command):
    def __init__(self, with_token: bool = False):
        super().__init__('login')
        self.with_token = with_token

    async def __call__(self, message: Message, bot: Bot) -> Union[bool, Dict[str, Any]]:
        if not (command_data := await super().__call__(message, bot)):
            return False
        if not self.with_token:
            return True

        command: CommandObject = command_data['command']
        if command.args:
            if search := re.search(r'(Bearer\s)?([-\w.]{512,1024})', command.args):
                return {
                    'token': search[2]
                }
            else:
                raise UnknownArgument(command.args)


class CommandLogout(Command):
    def __init__(self):
        super().__init__('logout')
