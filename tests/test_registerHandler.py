import pytest
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from unittest.mock import MagicMock, patch, AsyncMock
from handlers.registerHandler import Router


@pytest.fixture(scope='module')
def state():
    return MagicMock(spec=FSMContext)


@pytest.fixture(scope='module')
def message():
    return MagicMock(spec=types.Message)


@pytest.fixture(scope='module')
def callback_query():
    return MagicMock(spec=CallbackQuery)


@pytest.mark.asyncio
async def test_start():
    message = MagicMock()
    state = MagicMock()
    username = "test_user"
    
    with patch("handlers.registerHandler.scheduleParser.getTableObj", new=AsyncMock()) as mocked_getTableObj:
        router = Router()  # Создание экземпляра класса Router
        await router.propagate_event("message", message)



@pytest.mark.asyncio
async def test_cancel():
    callback_query = MagicMock()
    state = MagicMock()
    username = "test_user"
    language = "en"

    router = Router()

    with patch.object(state, 'clear') as mock_clear, \
         patch.object(callback_query, 'answer') as mock_answer, \
         patch.object(callback_query.message, 'edit_text') as mock_edit_text:

        await router.propagate_event("callback_query", callback_query)

"""
@pytest.mark.asyncio
async def test_get_course():
    callback_query = MagicMock()
    state = MagicMock()
    username = "test_user"
    
    router = Router()  
    
    with patch.object(state, 'set_state') as mock_set_state, \
         patch.object(state, 'update_data') as mock_update_data, \
         patch.object(callback_query.message, 'edit_text') as mock_edit_text:
    
        await router.propagate_event("callback_query", callback_query)
        
        mock_set_state.assert_called_once()
        mock_update_data.assert_called_once()
        mock_edit_text.assert_called_once()
"""

