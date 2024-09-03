from aiogram.fsm.state import State, StatesGroup


class Register(StatesGroup):
    faculty = State()
    course = State()
    direction = State()
    profile = State()
    group = State()
    first_name = State()
    middle_name = State()
    last_name = State()
    verify = State()
