from datetime import datetime, timedelta

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from loguru import logger

from config import TIMEZONE
from filters.dispatcherFilters import IsPrivate
from utils.ScheduleParser import scheduleParser

router = Router(name="mainHandler")
router.message.filter(IsPrivate)

# FIXME Ошибка с кнопкой назад в настройках


@router.message(F.text, Command("menu"))
async def menu(msg: Message, username: str, state: FSMContext) -> None:
    from bot import db
    from models.user import User

    session = db.session()
    userId = msg.from_user.id
    existingUser = session.query(User).filter_by(id=userId).first()
    session.close()
    if existingUser is None:
        from handlers.registerHandler import start

        return await start(msg, state, username)

    logger.opt(colors=True).debug(f"[<y>{username}</y>]: Called <b>/menu</b> command")

    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(text="Расписание на сегодня", callback_data="timetable_today"))
    keyboard.row(InlineKeyboardButton(text="Расписание на завтра", callback_data="timetable_nextday"))
    keyboard.row(InlineKeyboardButton(text="Настройки", callback_data="settings"))
    await msg.answer("Меню", reply_markup=keyboard.as_markup())


@router.callback_query(F.data == "menu")
async def menuCallback(
    callback: CallbackQuery,
    username: str,
    state: FSMContext,
    anotherHandler: bool = False,
) -> None:
    logger.opt(colors=True).debug(f"[<y>{username}</y>]: Called <b>menu</b> callback")

    from bot import db
    from models.user import User

    session = db.session()
    userId = callback.message.from_user.id
    existingUser = session.query(User).filter_by(id=userId).first()
    session.close()
    if existingUser is None and not anotherHandler:
        from handlers.registerHandler import start

        await callback.answer("Вы не зарегистрированы")
        return await start(callback.message, state, username)
    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(text="Расписание на сегодня", callback_data="timetable_today"))
    keyboard.row(InlineKeyboardButton(text="Расписание на завтра", callback_data="timetable_nextday"))
    keyboard.row(InlineKeyboardButton(text="Настройки", callback_data="settings"))
    if not anotherHandler:
        await callback.answer()
    await callback.message.edit_text("Меню", reply_markup=keyboard.as_markup())


@router.callback_query(F.data == "timetable_today")
@router.callback_query(F.data == "timetable_nextday")
async def timetableForDay(callback: CallbackQuery, username: str) -> None:
    logger.opt(colors=True).debug(f"[<y>{username}</y>]: Called <b>timetable_day</b> callback")
    from bot import db
    from models.user import User

    session = db.session()
    userId = callback.from_user.id
    existingUser = session.query(User).filter_by(id=userId).first()
    session.close()
    if existingUser is None:
        return await callback.answer("Вы не зарегистрированы!")
    import locale

    locale.setlocale(locale.LC_ALL, "ru")  # TODO исправить ёбаный костыль!
    day: datetime = datetime.now(TIMEZONE)
    if callback.data == "timetable_nextday":
        day += timedelta(days=1)
    await callback.message.answer(
        text=scheduleParser.getScheduleForDay(
            existingUser.course,
            existingUser.direction,
            existingUser.profile,
            existingUser.group,
            ("Знаменатель" if day.isocalendar().week % 2 == 0 else "Числитель"),  # TODO исправить!
            day.strftime("%A").capitalize(),  # TODO Исправить
        )
    )
    return await callback.answer("Ваше расписание")


@router.callback_query(F.data == "settings")
async def settings(callback: CallbackQuery, username: str) -> None:
    logger.opt(colors=True).debug(f"[<y>{username}</y>]: Called <b>settings</b> callback")
    from bot import db
    from models.user import User

    session = db.session()
    userId = callback.from_user.id
    existingUser = session.query(User).filter_by(id=userId).first()
    session.close()
    if existingUser is None:
        return await callback.answer("Вы не зарегистрированы!")
    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(text="Удалить аккаунт", callback_data="delete_user"))
    keyboard.row(InlineKeyboardButton(text="Назад", callback_data="menu"))
    await callback.message.edit_text("Настройки", reply_markup=keyboard.as_markup())
    return await callback.answer()


@router.callback_query(F.data == "delete_user")
async def deleteUser(callback: CallbackQuery, username: str, state: FSMContext) -> None:
    logger.opt(colors=True).debug(f"[<y>{username}</y>]: Called <b>delete_user</b> callback")
    from bot import db
    from models.user import User

    session = db.session()
    userId = callback.from_user.id
    existingUser = session.query(User).filter_by(id=userId).first()
    if existingUser is None:
        await callback.answer("Вы не зарегистрированы!")
    else:
        session.delete(existingUser)
        session.commit()
        await callback.answer("Вы успешно удалили свой аккаунт")
    session.close()
    await callback.message.delete()
    from handlers.registerHandler import start

    return await start(callback.message, state, username)
