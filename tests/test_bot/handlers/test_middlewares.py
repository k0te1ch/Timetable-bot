import pytest
from aiogram import types

from handlers.middlewares import ChatActionMiddleware, GeneralMiddleware


@pytest.fixture
def general_middleware():
    return GeneralMiddleware()


@pytest.fixture
def chat_action_middleware():
    return ChatActionMiddleware()


@pytest.mark.asyncio
async def test_general_middleware_language_extraction(general_middleware):
    user = types.User(id=123, is_bot=False, first_name="John")
    language = await general_middleware.get_language(user)
    assert language == "ru"


@pytest.mark.asyncio
async def test_general_middleware_default_language(general_middleware):
    user = types.User(id=123, is_bot=False, first_name="John", language_code="fr")
    language = await general_middleware.get_language(user)
    assert language == "ru"
