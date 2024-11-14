from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from collections import defaultdict

item_type = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Дух', callback_data='get_дух'
            ),
            InlineKeyboardButton(
                text='Противник', callback_data='get_противник'
            ),
            InlineKeyboardButton(
                text='Сценарий', callback_data='get_сценарий'
            )
        ]
    ]

)

params = {
    'source': (
        'База', 'Гиблый край', 'Ветви и когти',
        'Перо и пламя', 'Отметить всё', 'Готово'
    ),
    'difficulty': (
        'Низкая', 'Средняя', 'Высокая',
        'Очень высокая', 'Любая', 'Готово'
    )
}


def build_keybord(
        query_params: defaultdict[str, set[str]],
        stage: str = 'difficulty',
        mark_all: bool = False
):
    builder = InlineKeyboardBuilder()
    for item in params[stage]:
        if item == 'Готово':
            prefix = ''
        elif (
            not query_params.get(stage)
            or item not in query_params.get(stage)
        ) and not mark_all:
            prefix = '☑️'
        else:
            prefix = '✅'
        builder.button(
            text=f'{prefix}{item}', callback_data=f'{stage[:3]}_{item}'
        )
    builder.adjust(1)
    return builder