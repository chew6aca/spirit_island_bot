import os
from collections import defaultdict
from aiogram import Router, types, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from random import choice
from sqlalchemy import select, intersect
from keyboard import item_type, build_keybord
from database import new_session, SpiritOrm
from states import SpiritStates

media_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
router = Router()
query_params = defaultdict(set)


@router.message(Command('start'))
async def cmd_start(message: types.Message, state: FSMContext):
    if state:
        await state.clear()
        query_params.clear()
    await state.set_state(SpiritStates.choose_type)
    await message.answer(
        text='Выберите планшет',
        reply_markup=item_type
    )


async def get_spirit(query_params: defaultdict[set[str]]):
    async with new_session() as session:
        queries = [
            eval(
                f'select(SpiritOrm).filter(SpiritOrm.{key}.in_(list({value})))'
            ) if value else None for key, value in query_params.items()
        ]
        queries = list(filter(lambda x: x is not None, queries))
        query = intersect(*queries)
        res2 = await session.execute(query)
        result2 = res2.all()
        try:
            photo = types.FSInputFile(
                path=os.path.join(media_dir, choice(result2).picture)
            )
        except IndexError:
            photo = None
        return photo


@router.callback_query(F.data.endswith('Готово'))
async def get_photo(callback: types.CallbackQuery, state: FSMContext):
    if (
        'дух' in query_params['type']
        and await state.get_state() == SpiritStates.choose_expansions
    ):
        await state.set_state(SpiritStates.choose_difficulty)
        await callback.message.answer(
            text='Выберите сложность',
            reply_markup=build_keybord(
                query_params=query_params,
                stage='difficulty'
            ).as_markup()
        )
    else:
        await state.set_state(SpiritStates.get_spirit)
        photo = await get_spirit(query_params=query_params)
        if not photo:
            await callback.message.answer(
                'Упс, по заданным параметрам ничего не нашлось'
            )
        else:
            await callback.message.answer_photo(photo)
        query_params.clear()
        await cmd_start(message=callback.message, state=state)


@router.callback_query(
        StateFilter(SpiritStates.choose_type), F.data.startswith('get_')
    )
async def choose_type(callback: types.CallbackQuery, state: FSMContext):
    query_params['type'].add(callback.data.lstrip('get_'))
    await state.set_state(SpiritStates.choose_expansions)
    await callback.message.answer(
        'Выберите используемые дополнения',
        reply_markup=build_keybord(
            query_params=query_params,
            stage='source'
        ).as_markup()
    )


@router.callback_query(
        StateFilter(SpiritStates.choose_expansions), F.data.startswith('sou_')
    )
async def choose_expansions(callback: types.CallbackQuery, state: FSMContext):
    if callback.data == 'sou_Отметить всё':
        await callback.message.edit_reply_markup(
            reply_markup=build_keybord(
                query_params=query_params,
                stage='source',
                mark_all=True
            ).as_markup()
        )
        query_params['source'] = None
        await get_photo(callback=callback, state=state)
        return
    query_params['source'].add(callback.data.lstrip('sou_'))
    await callback.message.edit_reply_markup(
        reply_markup=build_keybord(
            query_params=query_params,
            stage='source'
        ).as_markup()
    )


@router.callback_query(StateFilter(SpiritStates.choose_difficulty))
async def choose_difficulty(callback: types.CallbackQuery, state: FSMContext):
    if callback.data == 'dif_Любая':
        await callback.message.edit_reply_markup(
            reply_markup=build_keybord(
                query_params,
                stage='difficulty',
                mark_all=True
            ).as_markup()
        )
        query_params['difficulty'] = None
        await get_photo(callback=callback, state=state)
        return
    query_params['difficulty'].add(callback.data.lstrip('dif_'))
    await callback.message.edit_reply_markup(
        reply_markup=build_keybord(
            query_params,
            stage='difficulty'
        ).as_markup()
    )
