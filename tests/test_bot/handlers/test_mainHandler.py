from unittest.mock import AsyncMock

import pytest
from aiogram.fsm.context import FSMContext
from aiogram_tests.types.dataset import MESSAGE

from handlers.mainHandler import menu


@pytest.fixture
def message():
    return MESSAGE.as_object(text="Hi, world!")


@pytest.fixture
def state():
    from bot import dp

    return FSMContext(storage=dp.storage, key=778921250)


@pytest.mark.asyncio
async def test_menu_handler_ru(message, state):
    message.text = "/menu"
    message.answer = AsyncMock()

    await menu(message, "username", state)

    message.answer.assert_called_once_with("Меню", reply_markup=None)


# Тест проверяет обработчик menu для английского языка
@pytest.mark.asyncio
async def test_menu_handler_en(message, state):
    message.text = "/menu"
    message.answer = AsyncMock()

    await menu(message, "username", state)

    message.answer.assert_called_once_with("Menu", reply_markup=None)
