from fix.utils.formatting import Text, Code, as_list
from typing import Optional, List, Dict, Any


def text(string: Optional[str]) -> Text:
    return Text(string or '')


def spoiler_fields(include: Optional[List[int]], exclude: Optional[List[int]]) -> Text:
    if not include and not exclude:
        return Text('Любые')
    return as_list(
        *filter(lambda _: _, (
            f'Выбрано {len(include)}' if include else '',
            f'Исключено {len(exclude)}' if exclude else ''
        )),
        sep='    '
    )


def interval(minimum: Optional[int], maximum: Optional[int]) -> Optional[Text]:
    match minimum, maximum:
        case None, None:
            return
        case _, None:
            return Text('Больше ', Code(minimum))
        case None, _:
            return Text('Меньше ', Code(maximum))
        case _, _:
            return Text('Больше ', Code(minimum), ' и меньше ', Code(maximum))


def select_fields(fields: Optional[List[int]], constant: List[Dict[str, Any]]) -> Optional[Text]:
    if fields:
        return as_list(*(
            '✅ ' + field['label']
            for field in constant
            if field['id'] in fields
        ))


def marked_fields(include: Optional[List[int]], exclude: Optional[List[int]], constant: List[Dict[str, Any]]) -> Optional[Text]:
    if duo := (include or []) + (exclude or []):
        return as_list(*(
            ('❇️ ' if include and field['id'] in include else '🅾️ ') + field['name']
            for field in constant
            if field['id'] in duo
        ))


def other_fields(long_no_translation: Optional[int], licensed: Optional[int], buy: Optional[int]) -> Optional[Text]:
    if long_no_translation or licensed is not None or buy:
        return as_list(
            *filter(lambda _: _, (
                ('✅ Нет перевода уже 3 месяца' if long_no_translation else None),
                (('❇️ ' if licensed else '🅾️ ') + 'Лицензирован' if licensed is not None else None),
                ('✅ Можно приобрести' if buy else None)
            ))
        )
