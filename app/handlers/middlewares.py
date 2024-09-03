from collections.abc import Awaitable, Callable
from typing import Any

from aiogram.dispatcher.flags import get_flag
from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.types import Message
from aiogram.utils.chat_action import ChatActionSender
from config import LANGUAGES
from database import db
from database.services.user import get_user_by_telegram_id, is_registered


class GeneralMiddleware(BaseMiddleware):

    async def get_language(self, user):
        if user.language_code in LANGUAGES:
            return user.language_code

        return "ru"

    async def __call__(
        self,
        handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: dict[str, Any],
    ) -> Any:
        handlerArgs = data["handler"].__dict__["params"]

        if "language" in handlerArgs:
            data["language"] = await self.get_language(event.from_user)

        if "username" in handlerArgs:
            data["username"] = event.from_user.username

        if "db" in handlerArgs:
            data["db"] = db

        if "existingUser" in handlerArgs:
            async with db.session() as session:
                async with session.begin():
                    data["existingUser"] = await get_user_by_telegram_id(session, event.from_user.id)

        if "existUser" in handlerArgs:
            async with db.session() as session:
                async with session.begin():
                    data["existUser"] = await is_registered(session, event.from_user.id)

        return await handler(event, data)


class ChatActionMiddleware(BaseMiddleware):

    async def __call__(
        self,
        handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: dict[str, Any],
    ) -> Any:
        long_operation_type = get_flag(data, "long_operation")

        if not long_operation_type:
            return await handler(event, data)

        async with ChatActionSender(action=long_operation_type, chat_id=event.chat.id):
            return await handler(event, data)
