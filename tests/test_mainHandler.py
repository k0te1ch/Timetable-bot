import pytest
from aiogram_tests.types.dataset import MESSAGE, DatasetItem, USER, CHAT
from aiogram.fsm.context import FSMContext
from unittest.mock import AsyncMock
from aiogram import types
from bot import dp

from handlers.mainHandler import menu

@pytest.fixture
def message():
    return DatasetItem(
        {
            "message_id": 11223,
            "from": USER,
            "chat": CHAT,
            "date": 1508709711,
            "text": "Hi, world!",
        },
        model=types.Message,
    )

@pytest.fixture
def state():
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
