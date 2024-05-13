from aiogram.fsm.state import State, StatesGroup


class FreeAudiences(StatesGroup):
    day = State()
    time = State()
    numerator = State()
