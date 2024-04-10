# TODO REBUILD THIS
# TODO ПЕРЕДЕЛАТЬ ВСЁ ТУТ

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from loguru import logger

from filters.dispatcherFilters import IsAdmin, IsPrivate
from utils.botMethods import shutdownBot
from utils.context import context
from utils.keyboards import keyboards

# TODO add callback fabric
router = Router(name="admin_panel")
router.message.filter(IsPrivate, IsAdmin)


@router.message(F.text, Command("admin_panel"))
async def start(msg: Message, language: str, username: str):
    logger.opt(colors=True).debug(f"[<y>{username}</y>]: Call admin panel")
    return await msg.answer(context["ru"].admin_panel_open, reply_markup=keyboards["admin"][language].main)


@router.callback_query(F.data == "bot")
async def bot(callback: CallbackQuery, language: str, username: str):
    logger.opt(colors=True).debug(f"[<y>{username}</y>]: Choose bot in admin panel")

    return await callback.message.edit_text(
        "Операции над ботом", reply_markup=keyboards["admin"][language].bot_commands
    )


# TODO IN PROGRESS
@router.callback_query(F.data == "restart_bot")
async def restart(callback: CallbackQuery, language: str, username: str):
    logger.opt(colors=True).debug(f"[<y>{username}</y>]: Restart bot")

    await callback.answer()
    await callback.message.answer("Бот перезагружается", reply_markup=ReplyKeyboardRemove())

    await shutdownBot()


@router.callback_query(F.data == "admin_back")
async def back(callback: CallbackQuery, language: str, username: str):
    logger.opt(colors=True).debug(f"[<y>{username}</y>]: Call back to admin panel")

    await callback.answer()
    return await callback.message.edit_text(
        context[language].admin_panel_open, reply_markup=keyboards["admin"][language].main
    )
