from unittest.mock import MagicMock, patch

import pytest
from aiogram.types import InlineKeyboardMarkup

from keyboards.adminPanel import en, ru
from utils.context import _Context


@pytest.fixture
def mocked_context():
    context_mock = MagicMock()
    context_mock.ru.admin_panel_main = [("Button 1", "callback_data_1"), ("Button 2", "callback_data_2")]
    context_mock.ru.bot_commands = [("Command 1", "command_1"), ("Command 2", "command_2")]
    return context_mock


def test_ru_keyboard(mocked_context):
    with patch.object(_Context, "__getitem__", return_value=mocked_context):
        keyboard = ru.main
        assert isinstance(keyboard, InlineKeyboardMarkup)
        assert len(keyboard.inline_keyboard) == 1


def test_en_keyboard(mocked_context):
    with patch.object(_Context, "__getitem__", return_value=mocked_context):
        keyboard = en.main
        assert isinstance(keyboard, InlineKeyboardMarkup)
        assert len(keyboard.inline_keyboard) == 1


def test_ru_commands_keyboard(mocked_context):
    with patch.object(_Context, "__getitem__", return_value=mocked_context):
        keyboard = ru.bot_commands
        assert isinstance(keyboard, InlineKeyboardMarkup)
        assert len(keyboard.inline_keyboard) == 1


def test_en_commands_keyboard(mocked_context):
    with patch.object(_Context, "__getitem__", return_value=mocked_context):
        keyboard = en.bot_commands
        assert isinstance(keyboard, InlineKeyboardMarkup)
        assert len(keyboard.inline_keyboard) == 1
