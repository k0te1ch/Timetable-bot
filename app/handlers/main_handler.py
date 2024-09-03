from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from filters.dispatcherFilters import IsPrivate
from loguru import logger

router = Router(name="mainHandler")
router.message.filter(IsPrivate)


# TODO Убрать дублирование кода
# TODO Убрать создание клавиатур в keyboards


async def _menu(msg: Message, callback: CallbackQuery, username: str, state: FSMContext, db, existUser: bool) -> None:
    if msg is None and callback is not None:
        msg = callback.message
        call = True
    elif msg is not None and callback is None:
        call = False

    if not existUser:
        from handlers.register_handler import start

        if call:
            await callback.answer("Вы не зарегистрированы")
        return await start(msg=msg, state=state, username=username, db=db, existUser=existUser)

    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(text="На сегодня", callback_data="timetable_today"))
    keyboard.row(InlineKeyboardButton(text="На завтра", callback_data="timetable_nextday"))
    keyboard.row(InlineKeyboardButton(text="На текущую неделю", callback_data="timetable_current_week"))
    keyboard.row(InlineKeyboardButton(text="На следующую неделю", callback_data="timetable_next_week"))
    keyboard.row(InlineKeyboardButton(text="Найти свободную аудиторию", callback_data="free_audiences"))
    keyboard.row(InlineKeyboardButton(text="Настройки", callback_data="settings"))
    if call:
        await callback.message.edit_text("Меню", reply_markup=keyboard.as_markup())
    else:
        await msg.answer("Меню", reply_markup=keyboard.as_markup())


@router.message(F.text, Command("menu"))
async def menu(msg: Message, username: str, state: FSMContext, db, existUser: bool) -> None:
    logger.opt(colors=True).debug(f"[<y>{username}</y>]: Called <b>/menu</b> command")

    await _menu(msg=msg, callback=None, username=username, state=state, db=db, existUser=existUser)


@router.callback_query(F.data == "menu")
async def menuCallback(callback: CallbackQuery, username: str, state: FSMContext, db, existUser: bool) -> None:
    logger.opt(colors=True).debug(f"[<y>{username}</y>]: Called <b>menu</b> callback")

    await _menu(msg=None, callback=callback, username=username, state=state, db=db, existUser=existUser)
