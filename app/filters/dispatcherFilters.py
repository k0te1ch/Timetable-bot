from aiogram.enums import ChatType
from aiogram.types import Message
from config import ADMINS, LANGUAGES
from filters.chatType import ChatTypeFilter
from utils.context import context


async def IsGroup(m) -> bool:
    """
    This filter checks whether the chat is group or super group
    :return: bool
    """
    c = ChatTypeFilter([ChatType.GROUP, ChatType.SUPERGROUP])
    return await c(m)


async def IsPrivate(m) -> bool:
    """
    This filter checks whether the chat is private
    :return: bool
    """
    c = ChatTypeFilter(ChatType.PRIVATE)
    return await c(m)


async def IsChannel(m) -> bool:
    """
    This filter checks whether the chat is a channel
    :return: bool
    """
    c = ChatTypeFilter(ChatType.CHANNEL)
    return await c(m)


def IsAdmin(m) -> bool:
    """
    This filter checks whether the user is an administrator (in the list of administrators in the settings)
    :return: bool
    """
    return m.from_user.username in ADMINS


def ContextButton(context_key: str | list, classes: list = LANGUAGES):
    """
    This filter checks button's text when have a multi-language context
    example: ContextButton("cancel", ["ru", "en"])
    """

    def inner(m) -> bool | None:
        if not (isinstance(m, Message) and m.text):
            return

        for cls in classes:
            if isinstance(context_key, str):
                contexts = [context_key]
            else:
                contexts = context_key
            for context1 in contexts:
                attr = getattr(context[cls], context1)
                if isinstance(attr, list):
                    for i in attr:
                        if m.text == i:
                            return True
                else:
                    if m.text == attr:
                        return True

    return inner
