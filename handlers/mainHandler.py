import keyboards
import os
import shutil
from datetime import datetime, timedelta
from typing import cast

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from loguru import logger
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton
from filters.dispatcherFilters import IsPrivate
from utils.ScheduleParser import scheduleParser
from config import TIMEZONE

router = Router(name="mainHandler")
router.message.filter(IsPrivate)

#FIXME Ошибка с кнопкой назад в настройках

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
    keyboard.row(
        InlineKeyboardButton(text="На сегодня", callback_data="timetable_today")
    )
    keyboard.row(
        InlineKeyboardButton(text="На завтра", callback_data="timetable_nextday")
    )
    keyboard.row(
        InlineKeyboardButton(text="На текущую неделю", callback_data="timetable_current_week")
    )
    keyboard.row(
        InlineKeyboardButton(text="На следующую неделю", callback_data="timetable_next_week")
    )
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
    keyboard.row(
        InlineKeyboardButton(text="Расписание на сегодня", callback_data="timetable_today")
    )
    keyboard.row(
        InlineKeyboardButton(text="Расписание на завтра", callback_data="timetable_nextday")
    )
    keyboard.row(
        InlineKeyboardButton(text="Расписание на эту неделю", callback_data="timetable_current_week")
    )
    keyboard.row(
        InlineKeyboardButton(text="Расписание на следующую неделю", callback_data="timetable_next_week")
    )
    keyboard.row(InlineKeyboardButton(text="Настройки", callback_data="settings"))
    if not anotherHandler:
        await callback.answer()
    await callback.message.edit_text("Меню", reply_markup=keyboard.as_markup())


from datetime import datetime, timedelta

@router.callback_query(F.data == "timetable_today")
@router.callback_query(F.data == "timetable_nextday")
@router.callback_query(F.data == "timetable_current_week")
@router.callback_query(F.data == "timetable_next_week")
async def timetable(callback: CallbackQuery, username: str) -> None:
    logger.opt(colors=True).debug(
        f"[<y>{username}</y>]: Called <b>timetable</b> callback"
    )
    from bot import db
    from models.user import User

    session = db.session()
    userId = callback.from_user.id
    existingUser = session.query(User).filter_by(id=userId).first()
    session.close()
    if existingUser is None:
        return await callback.answer("Вы не зарегистрированы!")

    import locale

    locale.setlocale(locale.LC_ALL, "ru")

    current_week = "Знаменатель" if datetime.now().isocalendar()[1] % 2 == 0 else "Числитель"

    selected_day = datetime.now(TIMEZONE)
    if callback.data == "timetable_today":
        pass  
    elif callback.data == "timetable_nextday":
        selected_day += timedelta(days=1)
    elif callback.data == "timetable_current_week":
        start_of_week = selected_day - timedelta(days=selected_day.weekday())  
        end_of_week = start_of_week + timedelta(days=6)  
        schedule_for_week_str = f"Расписание на текущую неделю ({current_week}) с {start_of_week.strftime('%d.%m.%Y')} по {end_of_week.strftime('%d.%m.%Y')}:\n\n"
        for i in range(7):
            day = start_of_week + timedelta(days=i)
            if i == 6 and day.strftime('%A') == 'Sunday':  
                continue
            if i != 0 and day.strftime('%A')[0].isupper():  
                schedule_for_week_str += f"{day.strftime('%A')} ({current_week}):\n"
            schedule_for_week_str += scheduleParser.getScheduleForDay(
                existingUser.course,
                existingUser.direction,
                existingUser.profile,
                existingUser.group,
                current_week,
                day.strftime("%A").capitalize()
            ) + "\n\n"
        await callback.message.answer(text=schedule_for_week_str.strip())
        return await callback.answer("Ваше расписание")

    elif callback.data == "timetable_next_week":
        start_of_week = selected_day - timedelta(days=selected_day.weekday()) + timedelta(weeks=1)
        end_of_week = start_of_week + timedelta(days=6)
        next_week_type = "Знаменатель" if (selected_day + timedelta(weeks=1)).isocalendar()[1] % 2 == 0 else "Числитель"
        schedule_for_week_str = f"Расписание на следующую неделю ({next_week_type}) с {start_of_week.strftime('%d.%m.%Y')} по {end_of_week.strftime('%d.%m.%Y')}:\n\n"
        for i in range(7):
            day = start_of_week + timedelta(days=i)
            if i == 6 and day.strftime('%A') == 'Sunday':  
                continue
            if i != 0 and day.strftime('%A')[0].isupper():  
                schedule_for_week_str += f"{day.strftime('%A')} ({next_week_type}):\n"
            schedule_for_week_str += scheduleParser.getScheduleForDay(
                existingUser.course,
                existingUser.direction,
                existingUser.profile,
                existingUser.group,
                next_week_type,
                day.strftime("%A").capitalize()
            ) + "\n\n"
        await callback.message.answer(text=schedule_for_week_str.strip())
        return await callback.answer("Ваше расписание")

    schedule_for_week_str = f"Расписание на {selected_day.strftime('%A')} ({current_week}):\n\n"
    schedule_for_week_str += scheduleParser.getScheduleForDay(
        existingUser.course,
        existingUser.direction,
        existingUser.profile,
        existingUser.group,
        current_week,
        selected_day.strftime("%A").capitalize()
    ) + "\n\n"

    await callback.message.answer(text=schedule_for_week_str.strip())
    await callback.answer("Ваше расписание")


@router.callback_query(F.data == "settings")
async def settings(callback: CallbackQuery, username: str) -> None:
    logger.opt(colors=True).debug(
        f"[<y>{username}</y>]: Called <b>settings</b> callback"
    )
    from bot import db
    from models.user import User

    session = db.session()
    userId = callback.from_user.id
    existingUser = session.query(User).filter_by(id=userId).first()
    session.close()
    if existingUser is None:
        return await callback.answer("Вы не зарегистрированы!")
    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(text = "Удалить аккаунт", callback_data= "delete_user"))
    keyboard.row(InlineKeyboardButton(text = "Назад", callback_data = "menu"))
    await callback.message.edit_text("Настройки", reply_markup=keyboard.as_markup())
    return await callback.answer()


@router.callback_query(F.data == "delete_user")
async def deleteUser(callback: CallbackQuery, username: str, state: FSMContext) -> None:
    logger.opt(colors=True).debug(
        f"[<y>{username}</y>]: Called <b>delete_user</b> callback"
    )
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
