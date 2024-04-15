from aiogram.fsm.state import State, StatesGroup


class Feedback(StatesGroup):
    message = State()
