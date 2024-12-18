from aiogram import Bot
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from src.database.context import Context
from src.database.states import State
from src.exceptions import UnknownArgument
from src.utils import (
    fetch_data_of_title,
    get_site_id
)

from typing import Union, Literal, Dict, Any
import re

from src.utils.api import requests


class CommandTitle(Command):
    def __init__(self) -> None:
        super().__init__(re.compile(r'manga|slash|ranobe|hentai|anime'))

    async def __call__(self, message: Message, bot: Bot) -> Union[Literal[False], Dict[str, Any]]:
        if not (command_data := await super().__call__(message, bot)):
            return False

        command: CommandObject = command_data['command']
        if not (data := fetch_data_of_title(command.args or '', get_site_id(command.command))):
            raise UnknownArgument(command.args)

        context = Context(telegram_id=message.from_user.id, chat_id=message.chat.id, site_id=data['site_id'])
        await context.load()

        match data:
            case {'type': 'slug_url', 'site_id': _, 'args': slug_url}:
                context.state = State.title_page
                context.data = {
                    'slug_url': slug_url
                }
            case {'type': 'query', 'site_id': site_id, 'args': query}:
                context.state = State.catalog_page
                context.data = {
                    'slug_url': None,
                    'meta': {
                        'item': 0,
                        'last_page': False,
                        'slug_urls': []
                    },
                    'filters': {
                        'site_id': [site_id],
                        'q': query
                    },
                    'sorting': {},
                    'bookmarks': list(map(
                        lambda bookmark: {
                            'id': bookmark['id'],
                            'name': bookmark['name'],
                            'site_ids': bookmark['site_ids']
                        },
                        requests.get_user_bookmarks(
                            site_id=site_id,
                            user_id=context.user_id,
                            token=context.user_token
                        )['data']
                    )) if context.user_id else []
                }

        return {
            'context': context
        }
