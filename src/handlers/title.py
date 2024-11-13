from __future__ import annotations
# aiogram
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode
from aiogram import Router, Bot, F
from aiogram.filters.callback_data import (
    CallbackQueryFilter,
    CallbackData
)
from fix.utils.formatting import (
    as_list,
    ExpandableBlockQuote,
    BlockQuote,
    Bold,
    Code,
    Text
)
from aiogram.fsm.state import (
    StatesGroup,
    State
)
from aiogram.filters import (
    CommandObject,
    Command,
    Filter
)
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    LinkPreviewOptions,
    CallbackQuery,
    Message
)

# typing
from src.types import Request
from typing import (
    TypedDict,
    Optional,
    Literal,
    Union,
    Dict,
    List,
    Any,
    override
)

# utils
import urllib.parse
import validators
import re


# Router
router = Router()


# Constants
SITE_IDS = {
    'manga': 1,
    'slash': 2,
    'ranobe': 3,
    'hentai': 4,
    'anime': 5
}

TITLE_DOMENS = {
    'mangalib.org': 'manga',
    'test-front.mangalib.me': 'manga',
    'slashlib.me': 'slash',
    'ranobelib.me': 'ranobe',
    'hentailib.me': 'hentai',
    'anilib.me': 'anime'
}

_ = '?fields[]=background' \
'&fields[]=eng_name' \
'&fields[]=otherNames' \
'&fields[]=summary' \
'&fields[]=releaseDate' \
'&fields[]=type_id' \
'&fields[]=caution' \
'&fields[]=views' \
'&fields[]=close_view' \
'&fields[]=rate_avg' \
'&fields[]=rate' \
'&fields[]=genres' \
'&fields[]=tags' \
'&fields[]=teams' \
'&fields[]=user' \
'&fields[]=franchise' \
'&fields[]=authors' \
'&fields[]=publisher' \
'&fields[]=userRating' \
'&fields[]=moderated' \
'&fields[]=metadata' \
'&fields[]=metadata.count' \
'&fields[]=metadata.close_comments'

INDEX_URL = 'https://api.mangalib.me/api/manga/{slug_url}' + _ + \
'&fields[]=manga_status_id' \
'&fields[]=chap_count' \
'&fields[]=status_id' \
'&fields[]=artists' \
'&fields[]=format'

ANIME_URL = 'https://api.mangalib.me/api/anime/{slug_url}' + _ + \
'&fields[]=anime_status_id' \
'&fields[]=time' \
'&fields[]=episodes' \
'&fields[]=episodes_count' \
'&fields[]=episodesSchedule' \
'&fields[]=shiki_rate'

REQUIRED_URL = {
    'manga': INDEX_URL,
    'slash': INDEX_URL,
    'ranobe': INDEX_URL,
    'hentai': INDEX_URL,
    'anime': ANIME_URL
}

CATALOG_URL = 'https://api.mangalib.me/api/{title_type}' \
'?site_id[]={site_id}' \
'&q={query}' \
'&page={page}' \
'&fields[]=rate' \
'&fields[]=rate_avg' \
'&fields[]=userBookmark'

TITLE_URLS = {
    1: 'https://mangalib.org/ru/manga/{slug_url}',
    2: 'https://v2.slashlib.me/ru/manga/{slug_url}',
    3: 'https://ranobelib.me/ru/book/{slug_url}',
    4: 'https://hentailib.me/ru/manga/{slug_url}',
    5: 'https://anilib.me/ru/anime/{slug_url}'
}

CAUTION = {
    0: 'Нет',
    1: '6+',
    2: '12+',
    3: '16+',
    4: '18+',
    5: '18+ (RX)'
}

TYPES = {
    1: 'Манга',
    5: 'Манхва',
    4: 'OEL-манга',
    6: 'Маньхуа',
    8: 'Руманга',
    9: 'Комикс'
}

FORMAT = {
    1: '4-кома (Ёнкома)',
    2: 'Сборник',
    3: 'Додзинси',
    4: 'В цвете',
    5: 'Сингл',
    6: 'Веб',
    7: 'Вебтун'
}

STATUS = {
    1: 'Онгоинг',
    2: 'Завершён',
    3: 'Анонс',
    4: 'Приостановлен',
    5: 'Выпуск прекращён'
}

SCANLATE_STATUS = {
    1: 'Продолжается',
    2: 'Завершён',
    3: 'Заморожен',
    4: 'Заброшен'
}


# Utils
def get_catalog_url(
    title_type: str,
    site_id: int,
    page: int,
    filters: FiltersData
) -> str:
    data = filters.copy()
    if page > 1:
        data['page'] = page
    if data.get('q'):
        data['q'] = urllib.parse.quote_plus(data['q'])
    data['fields'] = ['rate', 'rate_avg', 'userBookmark']
    result = []
    for section in data:
        if isinstance(data[section], list):
            result.extend([(f'{section}[]', f'{value}') for value in sorted(data[section])])
        else:
            result.append((section, f'{data[section]}'))
    return f'https://api.mangalib.me/api/{title_type}?site_id[]={site_id}' + ''.join([f'&{key}={value}' for key, value in sorted(result)])


# Callback Data Types
class TitleCallbackData(CallbackData, prefix='title'):
    user_id: int

class CatalogCallbackData(CallbackData, prefix='catalog'):
    user_id: int
    action: str

class FiltersCallbackData(CallbackData, prefix='filters'):
    user_id: int
    section: str

class IdsFilterCallbackData(CallbackData, prefix='filter_ids'):
    user_id: int
    section: str
    id: int

class NamedFilterCallbackData(CallbackData, prefix='filter_other'):
    user_id: int
    section: str

class CommandCallbackData(TypedDict):
    site: str
    site_id: int
    slug_url: Optional[str]
    query: Optional[str]


# Other Data Types
class FiltersData(TypedDict, total=False):
    q: str  # текст запроса
    genres: List[int]  # включение жанров
    genres_exclude: List[int]  # исключение жанров
    tags: List[int]  # включение тегов
    tags_exclude: List[int]  # исключение тегов
    chap_count_max: int  # кол-во глав максимум
    chap_count_min: int  # кол-во глав минимум
    year_max: int  # год релиза максимум
    year_min: int  # год релиза минимум
    rating_max: int  # оценка максимум
    rating_min: int  # оценка минимум
    rate_max: int  # кол-во оценок максимум
    rate_min: int  # кол-во оценок минимум
    caution: List[int]  # возрастной рейтинг
    types: List[int]  # тип
    format: List[int]  # вклучение форматов выпуска
    format_exclude: List[int]  # исключение форматов выпуска
    status: List[int]  # статус сайта
    scanlate_status: List[int]  # статус перевода
    long_no_translation: Literal[1]  # "Нет перевода уже 3 месяца"
    licensed: Literal[1]  # "Лицензирован"
    buy: Literal[1]  # "Можно приобрести"
    bookmarks: List[int]  # вклучение списков
    bookmarks_exclude: List[int]  # исключение списков

# State Groups
class TitleState(StatesGroup):
    catalog = State()
    search = State()


# Exceptions
class CommandError(Exception):
    command: CommandObject
    def __init__(self, command: CommandObject) -> None:
        super().__init__()
        self.command = command

class UnknownUrl(CommandError):
    url: str
    def __init__(self, command: CommandObject, url: str):
        super().__init__(command)
        self.url = url

class MismatchUrl(CommandError):
    url: str
    def __init__(self, command: CommandObject, url: str):
        super().__init__(command)
        self.url = url

class TitleNotExist(Exception):
    slug_url: str
    def __init__(self, slug_url: str):
        super().__init__()
        self.slug_url = slug_url

class NoActionRequired(Exception):
    pass


# Filters
class CommandTitle(Command):
    def __init__(self) -> None:
        super().__init__(re.compile(r'manga|slash|ranobe|hentai|anime'))

    async def __call__(self, message: Message, bot: Bot, state: FSMContext) -> bool:
        if not (result := await super().__call__(message, bot)):
            return False

        pattern = r'https://((test-front.mangalib.me|mangalib.org|v2.slashlib.me|hentai.me)/ru/manga|ranobelib.me/ru/book|anilib.me/ru/anime)/(\d+--\w[\w-]+)(/\S*)?'
        command: CommandObject = result['command']
        site = command.command
        site_id = SITE_IDS[site]
        args = command.args or ''

        # when slug_url is used
        if args and re.fullmatch(r'\d+--\w[\w-]+', args):
            slug_url, query = args, None

        # when title url is used
        elif args and (match := re.fullmatch(pattern, args)):
            if site != (site := re.findall(r'manga|slash|ranobe|hentai|anime', match.group(1))[0]):
                raise MismatchUrl(command, args)
            site_id = SITE_IDS[site]
            slug_url, query = match.group(2), None

        # when other URLs are used
        elif args and validators.url(args):
            raise UnknownUrl(command, args)
        
        # when query is used
        else:
            await state.set_state(TitleState.catalog)
            await state.update_data({
                'index': 0,
                'slugs': None,
                'filters': {}
            })
            slug_url, query = None, args

        await state.update_data({
            'main': {
                'site': site,
                'site_id': site_id,
                'slug_url': slug_url
            },
            'filters': {
                'q': query
            }
        })
        return True

class ChangeQueryMessageFilter(Filter):
    async def __call__(self):
        return super().__call__(
            TitleState.catalog,
            not F.text.startswith('/')
        )

class BaseCallbackQueryFilter(CallbackQueryFilter):
    def __init__(self, callback_data: type[CallbackData], key: str, *args: object) -> None:
        super().__init__(
            callback_data=callback_data,
            rule=F.__getattr__(key).in_(args) if args else None
        )

    async def __call__(self, callback: CallbackQuery) -> Union[Literal[False], Dict[str, Any]]:
        if not (result := await super().__call__(callback)):
            return False
        
        if callback.from_user.id != result['callback_data'].user_id:
            return False
        return result

class TitleCallbackQueryFilter(BaseCallbackQueryFilter):
    def __init__(self) -> None:
        super().__init__(TitleCallbackData, '')

class CatalogCallbackQueryFilter(BaseCallbackQueryFilter):
    def __init__(self, *actions: str) -> None:
        super().__init__(CatalogCallbackData, 'action', *actions)

class FiltersCallbackQueryFilter(BaseCallbackQueryFilter):
    def __init__(self, *filters: str) -> None:
        super().__init__(FiltersCallbackData, 'section', *filters)

class IdsFilterCallbackQueryFilter(BaseCallbackQueryFilter):
    def __init__(self, *ids: int) -> None:
        super().__init__(IdsFilterCallbackData, 'id', *ids)

class NamedFilterCallbackQueryFilter(BaseCallbackQueryFilter):
    def __init__(self, *fields: str):
        super().__init__(NamedFilterCallbackData, 'section', *fields)


# Getting Data
async def get_title_data(
    *,
    request: Request,
    state: FSMContext
) -> Optional[Any]:
    data = await state.get_data()
    main = data['main']
    filters = data['filters']
    site, site_id, slug_url = main['site'], main['site_id'], main['slug_url']
    index: int = data.get('index')
    slugs: Optional[List[str]] = data.get('slugs') or []

    # get list of titles
    if await state.get_state() == TitleState.catalog:
        if not slugs or (len(slugs) % 60 == 0 and index >= len(slugs)):
            response: Any = request.get(
                url=get_catalog_url(
                    title_type='anime' if site == 'anime' else 'manga',
                    site_id=site_id,
                    page=index // 60 + 1,
                    filters=filters
                )
            ).json()['data']
            slugs.extend([title['slug_url'] for title in response])
            await state.update_data(slugs=slugs)
        if index >= len(slugs):
            await state.update_data(index=index - 1)
            raise NoActionRequired()
        if index == -1:
            await state.update_data(index=index + 1)
            raise NoActionRequired()
        slug_url = slugs[index]
        await state.update_data(slug_url=slug_url)

    # get the data about this title
    title = request.get(REQUIRED_URL[site].format(
        type='anime' if site == 'anime' else 'manga',
        slug_url=slug_url
    )).json()['data']

    if 'toast' in title:
        raise TitleNotExist()
    return title

async def get_user_folders_data(
    
) -> ...: ...


# Generating Message Text
async def generate_title_message(
    *,
    request: Request,
    state: FSMContext
) -> Dict[str, Any]:
    data = await get_title_data(
        request=request,
        state=state
    )
    if not data:
        return

    return {
        'parse_mode': ParseMode.HTML,
        'link_preview_options': LinkPreviewOptions(
            url=data['cover']['default'] or data['cover']['thumbnail'],
            show_above_text=True,
            prefer_large_media=True
        ),
        'text': as_list(
            Bold(data['rus_name']),
            data['name'],
            BlockQuote(as_list(
                Text(
                    Code('⭐ %s' % (data['rating']['average'] or '—')),
                    ' %s' % (data['rating']['votesFormated'] or '—')
                ),
                Code('🔞 %s' % (data['ageRestriction']['label'] or '—')),
                sep='  ·  '
            )),
            as_list(
                Bold(data['type']['label'] or '—'),
                Bold(data['status']['label'] or '—'),
                Text(
                    Bold(data['items_count']['uploaded'] or 0),
                    ' из ',
                    Bold(data['items_count']['total'] or 0),
                    (f' [{data['time']['formated'] or '—'}]' if 'time' in data else '')
                ),
                Bold(data['releaseDateString'] or '—'),
                sep='  ·  '
            ),
            *((ExpandableBlockQuote(data['summary']),) if data['summary'] else ()),
            ExpandableBlockQuote(
                *((as_list(
                    *[Code(genre['name']) for genre in data['genres']],
                    *[Code('#' + tag['name']) for tag in data['tags']],
                    sep='  ·  '
                ),) if data['genres'] or data['tags'] else ())
            )
        ).as_html()
    }

async def generate_filters_message(
    *,
    request: Request,
    state: FSMContext
) -> Dict[str, Any]:
    filters = (await state.get_data())['filters']

    def text(text: Optional[str]) -> Optional[Text]:
        return Text(text) if text else Text('')
    
    def spoiler_fields(include: Optional[List[int]], exclude: Optional[List[int]]) -> Optional[Text]:
        if not include and not exclude:
            return Text('Любые')
        return as_list(
            f'Выбрано {len(include)}' if include else '',
            f'Исключено {len(exclude)}' if exclude else '',
            sep='    '
        )
    
    def interval(minimum: Optional[int], maximum: Optional[int]) -> Optional[Text]:
        match minimum, maximum:
            case None, None:
                return
            case _, None:
                return Text('Начиная с ', Code(minimum))
            case None, _:
                return Text('Заканчивая на ', Code(maximum))
            case _, _:
                return Text('Начиная с ', Code(minimum), ' и заканчивая на ', Code(maximum))

    def select_fields(fields: Optional[List[int]], storage: Dict[int, str]) -> Optional[Text]:
        if fields:
            return as_list(*('✅ ' + storage[id] for id in sorted(fields)))

    def marked_fields(include: Optional[List[int]], exclude: Optional[List[int]], storage: Dict[int, str]) -> Optional[Text]:
        if include or exclude:
            return as_list(*(('❇️ ' if id in include else '🅾️ ') + storage[id] for id in sorted(include or [] + exclude or [])))

    def other_fields(long_no_translation: Optional[int], licensed: Optional[int], buy: Optional[int]) -> Text:
        if long_no_translation or licensed is not None or buy:
            return as_list(
                # ('✅ ' if long_no_translation else '🔳 ') + 'Нет перевода уже 3 месяца',
                # ('❇️ ' if licensed else '🅾️ ' if licensed == 0 else '🔳 ') + 'Лицензирован',
                # ('✅ ' if buy else '🔳 ') + 'Можно приобрести'
                *filter(lambda _: _, (
                    ('✅ Нет перевода уже 3 месяца' if long_no_translation else ''),
                    (('❇️ ' if licensed else '🅾️ ') + 'Лицензирован' if licensed is not None else ''),
                    ('✅ Можно приобрести' if buy else '')
                ))
            )

    def render_sections(sections: Dict[str, Optional[Text]]) -> Text:
        return as_list(*(as_list(Bold(f'{title}:'), BlockQuote(value)) for title, value in sections.items() if value is not None))

    sections = {
        'Текст запроса': text(
            filters.get('q')
        ),
        'Жанры': spoiler_fields(
            filters.get('genres'),
            filters.get('genres_exclude')
        ),
        'Теги': spoiler_fields(
            filters.get('tags'),
            filters.get('tags_exclude')
        ),
        'Количество глав': interval(
            filters.get('chap_count_min'),
            filters.get('chap_count_max')
        ),
        'Год релиза': interval(
            filters.get('year_min'),
            filters.get('year_max')
        ),
        'Оценка': interval(
            filters.get('rating_min'),
            filters.get('rating_max')
        ),
        'Количество оценок': interval(
            filters.get('rate_min'),
            filters.get('rate_max')
        ),
        'Возрастной рейтинг': select_fields(
            filters.get('caution'),
            CAUTION
        ),
        'Тип': select_fields(
            filters.get('types'),
            TYPES
        ),
        'Формат выпуска': marked_fields(
            filters.get('format'),
            filters.get('format_exclude'),
            FORMAT
        ),
        'Статус тайтла': select_fields(
            filters.get('status'),
            STATUS
        ),
        'Статус перевода': select_fields(
            filters.get('scanlate_status'),
            SCANLATE_STATUS
        ),
        'Другое': other_fields(
            filters.get('long_no_translation'),
            filters.get('licensed'),
            filters.get('buy')
        ),
        # 'Мои списки': marked_fields(
        #     filters.get('bookmarks'),
        #     filters.get('bookmarks_exclude'),
        #     ...
        # )
    }

    return {
        'parse_mode': ParseMode.HTML,
        'text': render_sections(sections).as_html()
    }


# Generating Keyboard Markup
async def generate_catalog_keyboard_markup(
    *,
    state: FSMContext,
    user_id: int
) -> InlineKeyboardMarkup:
    main = (await state.get_data())['main']
    site_id, slug_url = main['site_id'], main['slug_url']
    keyboard = InlineKeyboardBuilder()
    if await state.get_state() == TitleState.catalog:
        buttons = [
            {
                'filters': 'Фильтры',
                'sorting': 'Сортировка'
            },
            {
                'back': '🡠 Предыдущий',
                'close': '✖',
                'next': 'Следующий 🡢'
            }
        ]
        for row in buttons:
            keyboard.row(*(
                InlineKeyboardButton(
                    text=text,
                    callback_data=CatalogCallbackData(
                        user_id=user_id,
                        action=action
                    ).pack()
                ) for action, text in row.items()
            ))
    keyboard.row(
        InlineKeyboardButton(
            text='Начать ' + ('смотреть' if site_id == 5 else 'читать'),
            callback_data=f'abcd'
        ),
        InlineKeyboardButton(
            text='На страницу тайтла',
            url=TITLE_URLS[site_id].format(slug_url=slug_url)
        )
    )
    return keyboard.as_markup()

async def generate_filters_keyboard_markup(
    *,
    user_id: int
) -> InlineKeyboardMarkup:
    buttons = {
        'q': 'Текст запроса',
        'genres': 'Жанры',
        'tags': 'Теги',
        'chap_count': 'Количество глав',
        'year': 'Год релиза',
        'rating': 'Оценка',
        'rate': 'Количество оценок',
        'caution': 'Возрастной рейтинг',
        'types': 'Тип',
        'format': 'Формат выпуска',
        'status': 'Статус тайтла',
        'scanlate_status': 'Статус перевода',
        'other': 'Другое'
    }
    keyboard = InlineKeyboardBuilder()
    keyboard.add(*(
        InlineKeyboardButton(
            text=text,
            callback_data=FiltersCallbackData(
                user_id=user_id,
                section=section
            ).pack()
        ) for section, text in buttons.items()
    ))
    keyboard.adjust(1)
    keyboard.row(
        InlineKeyboardButton(
            text='Сбросить',
            callback_data=CatalogCallbackData(
                user_id=user_id,
                action='filters_clear'
            ).pack()
        ),
        InlineKeyboardButton(
            text='Применить',
            callback_data=TitleCallbackData(
                user_id=user_id
            ).pack()
        )
    )
    return keyboard.as_markup()

async def generate_filter_fields_keyboard_markup(
    *,
    user_id: int,
    section: str
) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    match section:
        case 'q':
            ...
        case 'genres' | 'tags':
            ...
        case 'chap_count' | 'year' | 'rating' | 'rate':
            ...
        case 'caution' | 'types' | 'format' | 'status' | 'scanlate_status':
            storage = {
                'caution': CAUTION,
                'types': TYPES,
                'format': FORMAT,
                'status': STATUS,
                'scanlate_status': SCANLATE_STATUS
            }[section]
            keyboard.add(*(
                InlineKeyboardButton(
                    text=text,
                    callback_data=IdsFilterCallbackData(
                        user_id=user_id,
                        section=section,
                        id=id
                    ).pack()
                ) for id, text in storage.items()
            ))
            keyboard.adjust(2)
        case 'other':
            buttons = {
                'long_no_translation': 'Нет перевода уже 3 месяца',
                'licensed': 'Лицензирован',
                'buy': 'Можно приобрести'
            }
            keyboard.add(*(
                InlineKeyboardButton(
                    text=text,
                    callback_data=NamedFilterCallbackData(
                        user_id=user_id,
                        section=field
                    ).pack()
                ) for field, text in buttons.items()
            ))
            keyboard.adjust(1)

    keyboard.row(
        InlineKeyboardButton(
            text='🡠 Назад',
            callback_data=CatalogCallbackData(
                user_id=user_id,
                action='filters'
            ).pack()
        ),
        InlineKeyboardButton(
            text='Применить',
            callback_data=TitleCallbackData(
                user_id=user_id
            ).pack()
        )
    )

    return keyboard.as_markup()


# Handlers
@router.message(CommandTitle())
async def cmd_title(
    message: Message,
    state: FSMContext,
    request: Request
) -> None:
    try:
        kwargs = await generate_title_message(
            request=request,
            state=state
        )
    except TitleNotExist:
        await message.reply(
            parse_mode=ParseMode.HTML,
            text=Text('Тайтла с данным ', Code('slug_url'), ' не существует.').as_html()
        )
        return
    reply_markup = await generate_catalog_keyboard_markup(
        user_id=message.from_user.id,
        state=state
    )
    await message.answer(**kwargs, reply_markup=reply_markup)

@router.callback_query(TitleCallbackQueryFilter())
async def callback_title(
    callback: CallbackQuery,
    callback_data: TitleCallbackData,
    state: FSMContext,
    request: Request
) -> None:
    try:
        kwargs = await generate_title_message(
            request=request,
            state=state
        )
    except TitleNotExist:
        await callback.message.edit_text(
            parse_mode=ParseMode.HTML,
            text=BlockQuote('Ничего не найдено').as_html()
        )
    reply_markup = await generate_catalog_keyboard_markup(
        user_id=callback_data.user_id,
        state=state
    )
    await callback.message.edit_text(**kwargs)
    await callback.message.edit_reply_markup(reply_markup=reply_markup)

@router.callback_query(CatalogCallbackQueryFilter('back', 'next'))
async def callback_catalog_navigate(
    callback: CallbackQuery,
    callback_data: CatalogCallbackData,
    request: Request,
    state: FSMContext
) -> None:
    index = (await state.get_data())['index']
    offset = {
        'back': -1,
        'next': +1
    }
    await state.update_data(index=index + offset[callback_data.action])
    try:
        kwargs = await generate_title_message(
            request=request,
            state=state
        )
    except NoActionRequired:
        await callback.answer()
    else:
        reply_markup = await generate_catalog_keyboard_markup(
            state=state,
            user_id=callback_data.user_id
        )
        await callback.message.edit_text(**kwargs)
        await callback.message.edit_reply_markup(reply_markup=reply_markup)

@router.callback_query(CatalogCallbackQueryFilter('close'))
async def callback_catalog_close(
    callback: CallbackQuery,
    callback_data: CatalogCallbackData,
    state: FSMContext
) -> None:
    await state.set_state(None)
    reply_markup = await generate_catalog_keyboard_markup(
        state=state,
        user_id=callback_data.user_id
    )
    await callback.message.edit_reply_markup(reply_markup=reply_markup)

@router.callback_query(CatalogCallbackQueryFilter('filters', 'filters_clear'))
async def callback_catalog_filters(
    callback: CallbackQuery,
    callback_data: CatalogCallbackData,
    state: FSMContext,
    request: Request
) -> None:
    await state.update_data({
        'slugs': None,
        'index': 0
    })
    if callback_data.action == 'filters_clear':
        filters = (await state.get_data())['filters']
        await state.update_data(filters={'q': filters['q']} if 'q' in filters else {})
    kwargs = await generate_filters_message(
        request=request,
        state=state
    )
    reply_markup = await generate_filters_keyboard_markup(
        user_id=callback_data.user_id
    )
    await callback.message.edit_text(**kwargs)
    await callback.message.edit_reply_markup(reply_markup=reply_markup)

@router.callback_query(FiltersCallbackQueryFilter(
    'q',
    'chap_count',
    'yeor',
    'rating',
    'rate',
    'caution',
    'types',
    'format',
    'status',
    'scanlate_status',
    'other'
))
async def callback_catalog_filter_section(
    callback: CallbackQuery,
    callback_data: FiltersCallbackData
) -> None:
    # if callback_data.section == 'q':
    #     await callback.answer(text='Для изменения текста запроса, просто отправьте боту сообщение с запросом', show_alert=True)
    #     return
    reply_markup = await generate_filter_fields_keyboard_markup(
        user_id=callback_data.user_id,
        section=callback_data.section
    )
    await callback.message.edit_reply_markup(reply_markup=reply_markup)

@router.callback_query(FiltersCallbackQueryFilter(
    'genres',
    'tags'
))
async def callback_catalog_filter_spoilered_section(
    callback: CallbackQuery,
    callback_data: FiltersCallbackData,
    state: FSMContext,
    request: Request
) -> None:
    data = await state.get_data()
    kwargs = ...
    reply_markup = ...
    await callback.message.edit_text(**kwargs)
    await callback.message.edit_reply_markup(reply_markup=reply_markup)

@router.callback_query(IdsFilterCallbackQueryFilter())
async def callback_catalog_filter_ids_field(
    callback: CallbackQuery,
    callback_data: IdsFilterCallbackData,
    state: FSMContext,
    request: Request
) -> None:
    filters = (await state.get_data())['filters']
    section, id = callback_data.section, callback_data.id
    match section:
        case 'caution' | 'types' | 'status' | 'scanlate_status':
            
            if id in (filters.get(section) or []):
                # remove id from list
                filters[section].remove(id)
                if not filters[section]:
                    del filters[section]

            else:
                # append id to list
                if section not in filters:
                    filters[section] = []
                filters[section].append(id)

        case 'format':

            if id in (filters.get('format') or []):
                # remove id from 'format' list...
                filters['format'].remove(id)
                if not filters['format']:
                    del filters['format']
                # ...and append it to 'format_exclude' list
                if 'format_exclude' not in filters:
                    filters['format_exclude'] = []
                filters['format_exclude'].append(id)

            elif id in (filters.get('format_exclude') or []):
                # remove id from 'format_exclude' list
                filters['format_exclude'].remove(id)
                if not filters['format_exclude']:
                    del filters['format_exclude']

            else:
                # append id to 'format' list
                if 'format' not in filters:
                    filters['format'] = []
                filters['format'].append(id)

    await state.update_data(filters=filters)
    
    kwargs = await generate_filters_message(
        request=request,
        state=state
    )
    reply_keyboard = await generate_filter_fields_keyboard_markup(
        user_id=callback_data.user_id,
        section=section
    )
    await callback.message.edit_text(**kwargs)
    await callback.message.edit_reply_markup(reply_markup=reply_keyboard)

@router.callback_query(NamedFilterCallbackQueryFilter())
async def callback_catalog_filter_named_field(
    callback: CallbackQuery,
    callback_data: NamedFilterCallbackData,
    state: FSMContext,
    request: Request
) -> None:
    filters = (await state.get_data())['filters']
    section = callback_data.section
    match section:
        case 'long_no_translation':
            if 'long_no_translation' in filters:
                del filters['long_no_translation']
            else:
                filters['long_no_translation'] = 1
        case 'licensed':
            if 'licensed' in filters:
                if filters['licensed'] == 1:
                    filters['licensed'] = 0
                    if 'buy' in filters:
                        del filters['buy']
                else:
                    del filters['licensed']
            else:
                filters['licensed'] = 1
        case 'buy':
            if 'buy' in filters:
                del filters['buy']
            else:
                filters['buy'] = 1
                filters['licensed'] = 1

    await state.update_data(filters=filters)

    kwargs = await generate_filters_message(
        request=request,
        state=state
    )
    reply_markup = await generate_filter_fields_keyboard_markup(
        user_id=callback_data.user_id,
        section='other'
    )
    await callback.message.edit_text(**kwargs)
    await callback.message.edit_reply_markup(reply_markup=reply_markup)

# @router.callback_query(CatalogCallbackQuery('sorting'))
# async def callback_catalog_sorting(
#     callback: CallbackQuery,
#     callback_data: CatalogCallbackData,
#     state: FSMContext,
#     request: Request
# )

# @router.message(ChangeQueryMessageFilter())
# async def message_receive(
#     message: Message,
#     state: FSMContext
# ) -> None:
#     filters = (await state.get_data())['filters']
#     filters['q'] = message.text
#     await state.update_data(filters=filters)
