from aiogram.fsm.state import StatesGroup, State


class SpiritStates(StatesGroup):
    choose_type = State()
    choose_expansions = State()
    choose_difficulty = State()
    get_spirit = State()
