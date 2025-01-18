import logging
import os
from collections import defaultdict
from random import choice

from aiogram import F, Router, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.fsm.storage.memory import MemoryStorage
from sqlalchemy import intersect, select

from database import SpiritOrm, new_session
from keyboard import build_keybord, choose_mode, item_type
from states import SpiritStates

media_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
router = Router()
query_params = defaultdict(set)

@router.message(Command('start'))
async def cmd_start(message: types.Message, state: FSMContext):
    if state:
        await state.clear()
        query_params.clear()
    await message.answer(
        text='Выберите режим',
        reply_markup=choose_mode
    )
    logging.info(f'Пользователь {message.chat.username} начал работу с ботом')
    new_user_storage_key = StorageKey(message.bot.id, message.chat.id, message.chat.id)
    storage = MemoryStorage()
    new_user_context = FSMContext(storage=storage, key=new_user_storage_key)
    await new_user_context.set_state(SpiritStates.start)
    await state.set_data(data=query_params)


@router.callback_query(F.data == 'beginning')
async def to_the_beginning(callback: types.CallbackQuery, state: FSMContext):
    await cmd_start(message=callback.message, state=state)


@router.callback_query(F.data.endswith('mode'))
async def set_mode(callback: types.CallbackQuery, state: FSMContext):
    if callback.data.startswith('random'):
        await state.set_state(SpiritStates.get_random)
    else:
        await state.set_state(SpiritStates.choose_type)
    await callback.message.answer(
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
    data = await state.get_data()
    if (
        'дух' in data['type']
        and await state.get_state() == SpiritStates.choose_expansions
    ):
        await state.set_state(SpiritStates.choose_difficulty)
        await callback.message.answer(
            text='Выберите сложность',
            reply_markup=build_keybord(
                query_params=data,
                stage='difficulty'
            ).as_markup()
        )
    else:
        photo = await get_spirit(query_params=data)
        if not photo:
            await callback.message.answer(
                'Упс, по заданным параметрам ничего не нашлось'
            )
        else:
            await callback.message.answer_photo(photo)
        data.clear()
        await state.set_data(data)
        await callback.message.answer(
            text='Выберите планшет',
            reply_markup=item_type
        )


@router.callback_query(
        F.data.startswith('get_')
    )
async def choose_type(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    data['type'].add(callback.data.lstrip('get_'))
    await state.set_data(data)
    if await state.get_state() == SpiritStates.get_random:
        await get_photo(callback=callback, state=state)
    else:
        await state.set_state(SpiritStates.choose_expansions)
        await callback.message.answer(
            'Выберите используемые дополнения',
            reply_markup=build_keybord(
                query_params=data,
                stage='source'
            ).as_markup()
        )


@router.callback_query(
        StateFilter(SpiritStates.choose_expansions), F.data.startswith('sou_')
    )
async def choose_expansions(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if callback.data == 'sou_Отметить всё':
        await callback.message.edit_reply_markup(
            reply_markup=build_keybord(
                query_params=data,
                stage='source',
                mark_all=True
            ).as_markup()
        )
        data['source'] = None
        await state.set_data(data)
        return
    data['source'].add(callback.data.lstrip('sou_'))
    await callback.message.edit_reply_markup(
        reply_markup=build_keybord(
            query_params=data,
            stage='source'
        ).as_markup()
    )
    await state.set_data(data)


@router.callback_query(StateFilter(SpiritStates.choose_difficulty))
async def choose_difficulty(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if callback.data == 'dif_Любая':
        await callback.message.edit_reply_markup(
            reply_markup=build_keybord(
                data,
                stage='difficulty',
                mark_all=True
            ).as_markup()
        )
        data['difficulty'] = None
        await state.set_data(data)
        return
    data['difficulty'].add(callback.data.lstrip('dif_'))
    await callback.message.edit_reply_markup(
        reply_markup=build_keybord(
            data,
            stage='difficulty'
        ).as_markup()
    )
    await state.set_data(data)
