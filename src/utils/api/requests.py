from src.exceptions import ApiException, NotFoundError
from src.types.api.responses import (
    TitleResponse,
    SearchResponse,
    UserAuthResponse,
    UserBookmarksResponse
)
from src.types.context import CatalogFilters, CatalogSorting
from src.utils import get_api_url

from typing import Optional
from cloudscraper import requests as rq
import urllib.parse


def request(url: str, site_id: int, token: Optional[str] = None):
    headers = {'Site-Id': str(site_id)}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    if url.startswith('/'):
        url = url[1:]
    response = rq.get(f'{get_api_url()}/{url}', headers=headers).json()
    match response:
        case {'data': {'toast': toast}}:
            match toast:
                case {'type': type, 'message': 'Not Found'}:
                    raise NotFoundError(type)
                case {'type': type, 'message': message}:
                    raise ApiException(type, message)
        case _:
            return response


class requests:
    @staticmethod
    def get_user(
        *,
        site_id: int,
        token: Optional[str] = None
    ) -> UserAuthResponse:
        return request('/auth/me', site_id, token)

    @staticmethod
    def get_titles_from_search(
        *,
        query: str,
        site_id: int,
        site_api_type: str,
        page: Optional[int] = 1,
        token: Optional[str] = None,
    ) -> SearchResponse:
        return request(
            f'/{site_api_type}'
            f'?fields[]=rate_avg'
            f'&fields[]=rate'
            f'&fields[]=releaseDate'
            f'&q={query}'
            f'&site_id[]={site_id}'
            f'&page={page}',
            site_id, token
        )

    @staticmethod
    def get_titles_from_catalog(
        *,
        site_id: int,
        filters: CatalogFilters,
        sorting: CatalogSorting,
        page: int = 1,
        token: Optional[str] = None
    ) -> SearchResponse:
        site_api_type = 'anime' if filters['site_id'][0] == 5 else 'manga'
        args = [
            ('fields[]', 'rate'),
            ('fields[]', 'rate_avg'),
            ('fields[]', 'userBookmark')
        ]
        if page != 1:
            args.append(('page', str(page)))
        for section, value in filters.items():
            if section == 'q':
                args.append(('q', urllib.parse.quote_plus(str(value))))
            elif isinstance(value, list):
                args.extend([(f'{section}[]', str(value)) for value in sorted(value)])
            else:
                args.append((section, str(value)))
        for parameter, value in sorting.items():
            args.append((parameter, value))
        return request(
            f'/{site_api_type}?' + '&'.join(f'{key}={value}' for key, value in sorted(args)),
            site_id, token
        )

    @staticmethod
    def get_title(
        *,
        site_id: int,
        site_api_type: str,
        slug_url: str,
        token: Optional[str] = None
    ) -> TitleResponse:
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
                fields += (
                    'artists',
                    'chap_count',
                    'format',
                    'manga_status_id',
                    'status_id'
                )
            case 'anime':
                fields += (
                    'anime_status_id',
                    'episodes',
                    'episodes_count',
                    'episodesSchedule',
                    'shiki_rate',
                    'time'
                )
        return request(
            f'/{site_api_type}/{slug_url}?' + '&'.join(f'fields[]={value}' for value in fields),
            site_id, token
        )

    @staticmethod
    def get_user_bookmarks(
        *,
        site_id: int,
        user_id: int,
        token: Optional[str] = None
    ) -> UserBookmarksResponse:
        return request(f'/bookmarks/folder/{user_id}', site_id, token)
