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
from src.types.api import ApiTitleData
from typing import (
    TypedDict,
    Optional,
    Literal,
    Union,
    Dict,
    List,
    Any
)

# utils
import urllib.parse
import validators
import re

# constants
from src.constants import *


# Router
router = Router()


# Exceptions
class UnknownUrl(Exception):
    url: str
    def __init__(self, url: str):
        super().__init__()
        self.url = url

class MismatchUrl(Exception):
    url: str
    def __init__(self, url: str):
        super().__init__()
        self.url = url

class TitleNotExist(Exception):
    slug_url: str
    def __init__(self, slug_url: str):
        super().__init__()
        self.slug_url = slug_url

class NoActionRequired(Exception):
    pass


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

class ReadCallbackData(CallbackData, prefix='read'):
    user_id: int


# Data Types
class MetaData(TypedDict):
    index: int
    slugs: List[str]

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
    licensed: Literal[0, 1]  # "Лицензирован"
    buy: Literal[1]  # "Можно приобрести"
    bookmarks: List[int]  # вклучение списков
    bookmarks_exclude: List[int]  # исключение списков

class SortingData(TypedDict, total=False):
    sort_by: sort_by
    sort_type: sort_type

# State Groups
class TitleState(StatesGroup):
    main_page = State()
    in_catalog = State()


# Filters
class CommandTitle(Command):
    def __init__(self) -> None:
        super().__init__(re.compile(r'manga|slash|ranobe|hentai|anime'))

    async def __call__(self, message: Message, bot: Bot, state: FSMContext) -> bool:
        if not (command_data := await super().__call__(message, bot)):
            return False

        command: CommandObject = command_data['command']

        await smart_update_state_by_query_string(
            site_id=get_site_id_by(command.command),
            query=command.args or '',
            state=state
        )
        return True

class ChangeQueryMessageFilter(Filter):
    async def __call__(self):
        return super().__call__(
            TitleState.in_catalog,
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


# Types
site_name = Literal['manga', 'slash', 'ranobe', 'hentai', 'anime']
site_id = Literal[1, 2, 3, 4, 5]
site_api_type = Literal['manga', 'anime']
site_content_type = Literal['manga', 'book', 'anime']

caution_filter_id = Literal[0, 1, 2, 3, 4, 5]
type_filter_id = Literal[1, 4, 5, 6, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22]
format_filter_id = Literal[1, 2, 3, 4, 5, 6, 7]
status_filter_id = Literal[1, 2, 3, 4, 5]
scanlate_status_filter_id = Literal[1, 2, 3, 4]

caution_filter_text = Literal['Нет', '6+', '12+', '16+', '18+', '18+ (RX)']
type_filter_text = Literal['Манга', 'OEL-манга', 'Манхва', 'Маньхуа', 'Руманга', 'Комикс', 'Япония', 'Корея', 'Китай', 'Английский', 'Авторский', 'Фанфик', 'TV-сериал', 'Фильм', 'Корометражка', 'Спешл', 'OVA', 'ONA', 'Клип']
format_filter_text = Literal['4-кома (Ёнкома)', 'Сборник', 'Додзинси', 'В цвете', 'Сингл', 'Веб', 'Вебтун']
status_filter_text = Literal['Онгоинг', 'Завершён', 'Анонс', 'Приостановлен', 'Выпуск прекращён']
scanlate_status_filter_text = Literal['Продолжается', 'Завершён', 'Заморожен', 'Заброшен']

sort_by = Literal['rate_avg', 'views', 'chap_count', 'releaseDate', 'last_chapter_at', 'created_at', 'name', 'rus_name']
sort_type = Literal['asc']

sort_by_names = Literal['По популярности', 'По рейтингу', 'По просмотрам', 'По количеству глав', 'По дате релиза', 'По дате обновления', 'По дате добавления', 'По зазванию (A-Z)', 'По названию (А-Я)']
sort_type_names = Literal['По убыванию', 'По воврастанию']


# Utils
def get_site_id_by(site_name: site_name) -> site_id:
    match site_name:
        case 'manga': return 1
        case 'slash': return 2
        case 'ranobe': return 3
        case 'hentai': return 4
        case 'anime': return 5

def get_site_api_type_by(site_id: site_id) -> site_api_type:
    match site_id:
        case 1 | 2 | 3 | 4: return 'manga'
        case 5: return 'anime'

def get_site_content_type_by(site_id: site_id) -> site_content_type:
    match site_id:
        case 1 | 2 | 4: return 'manga'
        case 3: return 'book'
        case 5: return 'anime'

def get_caution_filter_text_by(caution_filter_id: caution_filter_id) -> caution_filter_text:
    return CAUTION[caution_filter_id]

def get_type_filter_text_by(type_filter_id: type_filter_id) -> type_filter_text:
    return TYPES[type_filter_id]

def get_format_filter_text_by(format_filter_id: format_filter_id) -> format_filter_text:
    return FORMAT[format_filter_id]

def get_status_filter_text_by(status_filter_id: status_filter_id) -> status_filter_text:
    return STATUS[status_filter_id]

def get_scanlate_status_filter_text_by(scanlate_status_filter_id: scanlate_status_filter_id) -> scanlate_status_filter_text:
    return SCANLATE_STATUS[scanlate_status_filter_id]

def get_sort_by_name_by(sort_by: Optional[sort_by]) -> sort_by_names:
    match sort_by:
        case None: return 'По популярности'
        case 'rate_avg': return 'По рейтингу'
        case 'views': return 'По просмотрам'
        case 'chap_count': return 'По количеству глав'
        case 'releaseDate': return 'По дате релиза'
        case 'last_chapter_at': return 'По дате обновления'
        case 'created_at': return 'По дате добавления'
        case 'name': return 'По зазванию (A-Z)'
        case 'rus_name': return 'По названию (А-Я)'

def get_sort_type_name_by(sort_type: Optional[sort_type]) -> sort_by_names:
    match sort_type:
        case None: return 'По убыванию'
        case 'asc': return 'По возрастанию'

def get_api_catalog_url(
    *,
    meta: MetaData,
    filters: FiltersData,
    sorting: SortingData
) -> str:
    args = [
        ('fields[]', 'rate'),
        ('fields[]', 'rate_avg'),
        ('fields[]', 'userBookmark')
    ]
    if meta['index'] > 60:
        args.append(('page', str(meta['index'] // 60 + 1)))
    for section, value in filters.items():
        if section == 'q':
            args.append(('q', urllib.parse.quote_plus(value)))
        elif isinstance(value, list):
            args.extend([(f'{section}[]', str(value)) for value in sorted(value)])
        else:
            args.append((section, str(value)))
    for parameter, value in sorting.items():
        args.append((parameter, value))
    return f'https://api.mangalib.me/api/{get_site_api_type_by(filters['site_id'][0])}?' + '&'.join(
        f'{key}={value}' for key, value in sorted(args)
    )

def get_api_title_url(
    *,
    site_api_type: site_api_type,
    slug_url: str
) -> str:
    fields = (
        'authors',
        'background',
        'caution',
        'close_view',
        'eng_name',
        'franchise',
        'genres',
        'metadata',
        'metadata.close_comments',
        'metadata.count',
        'moderated',
        'otherNames',
        'publisher',
        'rate',
        'rate_avg',
        'releaseDate',
        'summary',
        'tags',
        'teams',
        'type_id',
        'user',
        'userRating',
        'views'
    )
    match site_api_type:
        case 'manga':
            fields += ('artists', 'chap_count', 'format', 'manga_status_id', 'status_id')
        case 'anime':
            fields += ('anime_status_id', 'episodes', 'episodes_count', 'episodesSchedule', 'shiki_rate', 'time')
    return f'https://api.mangalib.me/api/{site_api_type}/{slug_url}?' + '&'.join(
        f'fields[]={value}' for value in fields
    )

def get_link_to_title(
    *,
    site_id: site_id,
    slug_url: str
) -> str:
    match site_id:
        case 1: return f'https://mangalib.org/ru/manga/{slug_url}'
        case 2: return f'https://v2.slashlib.me/ru/manga/{slug_url}'
        case 3: return f'https://ranobelib.me/ru/book/{slug_url}'
        case 4: return f'https://hentailib.me/ru/manga/{slug_url}'
        case 5: return f'https://anilib.me/ru/anime/{slug_url}'

def get_all_filter_fields_by(site_id: site_id) -> Dict[str, List[Union[int, str]]]:
    match site_id:
        case 1:
            return {
                'caution': [0, 1, 2, 3, 4, 5],
                'types': [1, 4, 5, 6, 8, 9],
                'format': [1, 2, 3, 4, 5, 6, 7],
                'status': [1, 2, 3, 4, 5],
                'scanlate_status': [1, 2, 3, 4],
                'other': ['long_no_translation', 'licensed', 'buy']
            }
        case 2:
            return {
                'caution': [0, 1, 2, 3, 4, 5],
                'types': [1, 4, 5, 6, 8, 9],
                'format': [1, 2, 3, 4, 5, 6, 7],
                'status': [1, 2, 3, 4, 5],
                'scanlate_status': [1, 2, 3, 4],
                'other': ['long_no_translation']
            }
        case 3:
            return {
                'caution': [0, 1, 2, 3, 4, 5],
                'types': [10, 11, 12, 13, 14, 15],
                'format': [1, 2, 3, 4, 5, 6, 7],
                'status': [1, 2, 3, 4, 5],
                'scanlate_status': [1, 2, 3, 4],
                'other': ['long_no_translation', 'licensed', 'buy']
            }
        case 4:
            return {
                'types': [1, 4, 5, 6, 8, 9],
                'format': [1, 2, 3, 4, 5, 6, 7],
                'status': [1, 2, 3, 4, 5],
                'scanlate_status': [1, 2, 3, 4],
                'other': ['long_no_translation']
            }
        case 5:
            return {
                'caution': [0, 1, 2, 3, 4, 5],
                'types': [1, 4, 5, 6, 8, 9],
                'status': [1, 2, 3],
                'other': ['licensed']
            }

async def smart_update_state_by_query_string(
    *,
    site_id: site_id,
    query: Optional[str],
    state: FSMContext
) -> None:
    pattern = r'https://((test-front.mangalib.me|mangalib.org|v2.slashlib.me|hentai.me)/ru/manga|ranobelib.me/ru/book|anilib.me/ru/anime)/(\d+--\w[\w-]+)(/\S*)?'

    # get the filters from state
    if await state.get_state() == TitleState.in_catalog:
        data = await state.get_data()
        filters = data['filters']
        sorting = data['sorting']
    else:
        filters = {}
        sorting = {}

    # when slug_url is used
    if query and re.fullmatch(r'\d+--\w[\w-]+', query):
        slug_url = query

    # when title url is used
    elif query and (match := re.fullmatch(pattern, query)):
        if site_id != (site_id := get_site_id_by(re.findall(r'manga|slash|ranobe|hentai|anime', match.group(1))[0])):
            raise MismatchUrl(query)
        slug_url = match.group(2)

    # when other URLs are used
    elif query and validators.url(query):
        raise UnknownUrl(query)

    # when query is used
    else:
        await state.set_state(TitleState.in_catalog)
        await state.set_data({
            'site_id': site_id,
            'slug_url': None,
            'meta': {
                'index': 0,
                'ended': False,
                'slugs': []
            },
            'filters': {
                **filters,
                'site_id': [site_id],
                'q': query
            },
            'sorting': sorting
        })
        return

    await state.set_state(TitleState.main_page)
    await state.set_data({
        'site_id': site_id,
        'slug_url': slug_url
    })


# Getting Data
async def get_title_data(
    *,
    request: Request,
    state: FSMContext
) -> ApiTitleData:
    data = await state.get_data()
    site_id: site_id = data['site_id']
    meta: MetaData = data['meta']
    slug_url: str = data['slug_url']
    filters: FiltersData = data['filters']
    sorting: SortingData = data['sorting']

    # there is a separate check for the catalog
    if await state.get_state() == TitleState.in_catalog:

        # getting a list of slugs from the api
        if meta['index'] >= len(meta['slugs']) and not meta['ended']:
            titles = request.get(get_api_catalog_url(
                meta=meta,
                filters=filters,
                sorting=sorting
            )).json()['data']
            meta['slugs'].extend([title['slug_url'] for title in titles])

        # checking that the title index has not gone beyond the slugs list
        if meta['index'] >= len(meta['slugs']):
            await state.update_data(meta={ **meta, 'ended': True, 'index': meta['index'] - 1 })
            raise NoActionRequired()
        elif meta['index'] < 0:
            await state.update_data(meta={ **meta, 'index': 0 })
            raise NoActionRequired()
        
        # updating the data
        slug_url = meta['slugs'][meta['index']]
        await state.update_data({ 'meta': meta, 'slug_url': slug_url })
    
    title = request.get(get_api_title_url(
        site_api_type=get_site_api_type_by(site_id),
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
    filters: FiltersData = (await state.get_data())['filters']

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

    def select_fields(fields: Optional[List[int]], getter: Dict[int, str]) -> Optional[Text]:
        if fields:
            return as_list(*('✅ ' + getter(id) for id in sorted(fields)))

    def marked_fields(include: Optional[List[int]], exclude: Optional[List[int]], getter: Dict[int, str]) -> Optional[Text]:
        if include or exclude:
            return as_list(*(('❇️ ' if id in include else '🅾️ ') + getter(id) for id in sorted(include or [] + exclude or [])))

    def other_fields(long_no_translation: Optional[int], licensed: Optional[int], buy: Optional[int]) -> Text:
        if long_no_translation or licensed is not None or buy:
            return as_list(
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
            get_caution_filter_text_by
        ),
        'Тип': select_fields(
            filters.get('types'),
            get_type_filter_text_by
        ),
        'Формат выпуска': marked_fields(
            filters.get('format'),
            filters.get('format_exclude'),
            get_format_filter_text_by
        ),
        'Статус тайтла': select_fields(
            filters.get('status'),
            get_status_filter_text_by
        ),
        'Статус перевода': select_fields(
            filters.get('scanlate_status'),
            get_scanlate_status_filter_text_by
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
    data = await state.get_data()
    site_id: int = data['site_id']
    slug_url: str = data['slug_url']
    keyboard = InlineKeyboardBuilder()
    if await state.get_state() == TitleState.in_catalog:
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
            callback_data=ReadCallbackData(user_id=user_id).pack()
        ),
        InlineKeyboardButton(
            text='На страницу тайтла',
            url=get_link_to_title(
                site_id=site_id,
                slug_url=slug_url
            )
        )
    )
    return keyboard.as_markup()

async def generate_filters_keyboard_markup(
    *,
    user_id: int,
    site_id: site_id
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
    keys = get_all_filter_fields_by(site_id).keys()
    keyboard = InlineKeyboardBuilder()
    keyboard.add(*(
        InlineKeyboardButton(
            text=text,
            callback_data=FiltersCallbackData(
                user_id=user_id,
                section=section
            ).pack()
        ) for section, text in buttons.items() if section in keys
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
    site_id: site_id,
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
                'scanlate_status': SCANLATE_STATUS,
                'other': OTHER
            }[section]
            get_all_filter_fields_by(site_id).items()
            keyboard.add(*(
                InlineKeyboardButton(
                    text=storage[id],
                    callback_data=IdsFilterCallbackData(
                        user_id=user_id,
                        section=section,
                        id=id
                    ).pack()
                ) for id in get_all_filter_fields_by(site_id)[section]
            ))
            keyboard.adjust(2)
        case 'other':
            keyboard.add(*(
                InlineKeyboardButton(
                    text=OTHER[field],
                    callback_data=NamedFilterCallbackData(
                        user_id=user_id,
                        section=field
                    ).pack()
                ) for field in get_all_filter_fields_by(site_id)[section]
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
    meta = (await state.get_data())['meta']
    offset = {
        'back': -1,
        'next': +1
    }
    await state.update_data({
        'meta': {
            **meta,
            'index': meta['index'] + offset[callback_data.action]
        }
    })
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
    # await state.update_data({
    #     'slugs': None,
    #     'index': 0
    # })
    data = await state.get_data()
    site_id: site_id = data['site_id']
    if callback_data.action == 'filters_clear':
        filters: FiltersData = data['filters']
        await state.update_data(filters={'q': filters['q']} if 'q' in filters else {})
    kwargs = await generate_filters_message(
        request=request,
        state=state
    )
    reply_markup = await generate_filters_keyboard_markup(
        site_id=site_id,
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
    callback_data: FiltersCallbackData,
    state: FSMContext
) -> None:
    site_id: site_id = (await state.get_data())['site_id']
    # if callback_data.section == 'q':
    #     await callback.answer(text='Для изменения текста запроса, просто отправьте боту сообщение с запросом', show_alert=True)
    #     return
    reply_markup = await generate_filter_fields_keyboard_markup(
        user_id=callback_data.user_id,
        site_id=site_id,
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
    data = await state.get_data()
    filters: FiltersData = data['filters']
    site_id: site_id = data['site_id']
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
        site_id=site_id,
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
    data = await state.get_data()
    filters: FiltersData = data['filters']
    site_id: site_id = data['site_id']
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
        site_id=site_id,
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
