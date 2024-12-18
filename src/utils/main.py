from src.config.actual_api_domen_name import ACTUAL_API_DOMEN_NAME
from src.config.actual_domen_names import ACTUAL_DOMEN_NAMES
from src.config.actual_filter_sections import ACTUAL_FILTER_SECTIONS
from src.config.actual_other_filter_section_list import ACTUAL_OTHER_FILTER_SECTION_LIST
from src.types.context import CatalogFilters
from typing import Union, Literal, List, Dict, Any, Optional
import validators, re


def get_site_id(name: str) -> int:
    '''
    Returns the site id
    '''
    match name:
        case 'manga': return 1
        case 'slash': return 2
        case 'ranobe': return 3
        case 'hentai': return 4
        case 'anime': return 5


def get_site_name(site_id: int) -> str:
    '''
    Returns the site name by id
    '''
    match site_id:
        case 1: return 'manga'
        case 2: return 'slash'
        case 3: return 'ranobe'
        case 4: return 'hentai'
        case 5: return 'anime'


def get_site_api_type(site_id: int) -> str:
    '''
    Returns the site type of manga or anime
    '''
    match site_id:
        case 1 | 2 | 3 | 4: return 'manga'
        case 5: return 'anime'


def get_site_content_type(site_id: int) -> str:
    '''
    Returns the site type of manga, book or anime
    '''
    match site_id:
        case 1 | 2 | 4: return 'manga'
        case 3: return 'book'
        case 5: return 'anime'


def fetch_data_of_title(text: str, site_id: int) -> Union[Literal[False], Dict[str, Any]]:
    '''
    Checks the string for a slug_url or title url match,
    otherwise checks that the string is not an url.
    '''
    manga_domens = '|'.join(ACTUAL_DOMEN_NAMES[1] + ACTUAL_DOMEN_NAMES[2] + ACTUAL_DOMEN_NAMES[4])
    book_domens = '|'.join(ACTUAL_DOMEN_NAMES[3])
    anime_domens = '|'.join(ACTUAL_DOMEN_NAMES[5])
    pattern = rf'https://(({manga_domens})/ru/manga|({book_domens})/ru/book|({anime_domens})/ru/anime)/(\d+--\w[\w-]+)(/\S*)?'
    type = 'slug_url'

    # matches slug_url
    if text and re.fullmatch(r'\d+--\w[\w-]+', text):
        pass
    
    # matches the url of the title
    elif text and (match := re.fullmatch(pattern, text)):
        site_id = get_site_id(re.findall(r'manga|slash|ranobe|hentai|anime', match.group(1))[0])
        text = match.group(2)
    
    # external link
    elif text and validators.url(text):
        return False

    # any text
    else:
        type = 'query'

    return {
        'site_id': site_id,
        'args': text,
        'type': type
    }


def get_domen_name(site_id: int) -> str:
    return ACTUAL_DOMEN_NAMES[site_id][0]


def get_api_url() -> str:
    return f'https://{ACTUAL_API_DOMEN_NAME}/api'


def get_title_link(site_id: int, slug_url: str) -> str:
    return f'https://{get_domen_name(site_id)}/ru/{get_site_content_type(site_id)}/{slug_url}'


def clear_filters(filters: CatalogFilters) -> CatalogFilters:
    empty: CatalogFilters = {}
    if 'site_id' in filters: empty['site_id'] = filters['site_id']
    if 'q' in filters: empty['q'] = filters['q']
    return empty


def get_filter_sections_list(site_id: int, authorized: bool) -> List[str]:
    return ACTUAL_FILTER_SECTIONS[site_id] + (['bookmarks'] if authorized else [])


def get_other_filter_section_list() -> List[Dict[str, Any]]:
    return ACTUAL_OTHER_FILTER_SECTION_LIST


def filter_section_getter(storage: List[Dict[str, Any]], site_id: int, per_page: int = 16):
    def wrapper(setting_page: Optional[int] = None) -> List[Dict[str, Any]]:
        storage_section = [field for field in storage if site_id in field['site_ids']]
        if setting_page:
            return storage_section[(setting_page - 1) * per_page : setting_page * per_page]
        return storage_section
    return wrapper
