from aiogram.fsm.state import State, StatesGroup


class Register(StatesGroup):
    course = State()
    direction = State()
    profile = State()
    group = State()
