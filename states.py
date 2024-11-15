from aiogram.fsm.state import State, StatesGroup


class SpiritStates(StatesGroup):
    choose_type = State()
    choose_expansions = State()
    choose_difficulty = State()
    start = State()
    get_random = State()
