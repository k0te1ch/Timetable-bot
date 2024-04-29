from datetime import datetime, timedelta

from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from loguru import logger

from config import TIMEZONE
from database.models.user import User
from database.services.user import delete_user, get_user_by_id, is_registered
from filters.dispatcherFilters import IsPrivate
from handlers.registerHandler import start
from utils.ScheduleParser import scheduleParser

router = Router(name="mainHandler")
router.message.filter(IsPrivate)


# TODO Убрать дублирование кода с проверкой пользователя на его существование
# TODO Убрать создание клавиатур в keyboards


@router.message(F.text, Command("menu"))
async def menu(msg: Message, username: str, state: FSMContext, db) -> None:

    # TODO: убрать это в отдельный метод в модель User
    async with db.session() as session:
        existUser: bool = await is_registered(session, msg.from_user.id)
    if not existUser:
        from handlers.registerHandler import start

        return await start(msg=msg, state=state, username=username, db=db)

    logger.opt(colors=True).debug(f"[<y>{username}</y>]: Called <b>/menu</b> command")

    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(text="На сегодня", callback_data="timetable_today"))
    keyboard.row(InlineKeyboardButton(text="На завтра", callback_data="timetable_nextday"))
    keyboard.row(InlineKeyboardButton(text="На текущую неделю", callback_data="timetable_current_week"))
    keyboard.row(InlineKeyboardButton(text="На следующую неделю", callback_data="timetable_next_week"))
    keyboard.row(InlineKeyboardButton(text="Найти свободную аудиторию", callback_data="free_audiences"))
    keyboard.row(InlineKeyboardButton(text="Настройки", callback_data="settings"))
    await msg.answer("Меню", reply_markup=keyboard.as_markup())


@router.callback_query(F.data == "menu")
async def menuCallback(callback: CallbackQuery, username: str, state: FSMContext, db) -> None:
    logger.opt(colors=True).debug(f"[<y>{username}</y>]: Called <b>menu</b> callback")

    # TODO: убрать это в отдельный метод в модель User
    async with db.session() as session:
        async with session.begin():
            existUser: bool = await is_registered(session, callback.from_user.id)
    if not existUser:
        from handlers.registerHandler import start

        await callback.answer("Вы не зарегистрированы")
        return await start(msg=callback.message, state=state, username=username, db=db)
    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(text="На сегодня", callback_data="timetable_today"))
    keyboard.row(InlineKeyboardButton(text="На завтра", callback_data="timetable_nextday"))
    keyboard.row(InlineKeyboardButton(text="На текущую неделю", callback_data="timetable_current_week"))
    keyboard.row(InlineKeyboardButton(text="На следующую неделю", callback_data="timetable_next_week"))
    keyboard.row(InlineKeyboardButton(text="Найти свободную аудиторию", callback_data="free_audiences"))
    keyboard.row(InlineKeyboardButton(text="Настройки", callback_data="settings"))
    await callback.message.edit_text("Меню", reply_markup=keyboard.as_markup())


# FIXME: что это такое? 👇 (Отрефакторить эту тему)
@router.callback_query(F.data == "timetable_today")
@router.callback_query(F.data == "timetable_nextday")
@router.callback_query(F.data == "timetable_current_week")
@router.callback_query(F.data == "timetable_next_week")
async def timetableForDay(callback: CallbackQuery, username: str, db) -> None:
    logger.opt(colors=True).debug(f"[<y>{username}</y>]: Called <b>timetable</b> callback")

    # TODO: убрать это в отдельный метод в модель User
    async with db.session() as session:
        async with session.begin():
            existingUser: User = await get_user_by_id(session, callback.from_user.id)
    if existingUser is None:
        return await callback.answer("Вы не зарегистрированы!")

    import locale

    locale.setlocale(locale.LC_ALL, "ru_RU.UTF-8")  # FIXME: костыль

    selected_day: datetime = datetime.now(TIMEZONE)
    current_week: str = "Знаменатель" if selected_day.isocalendar().week % 2 == 0 else "Числитель"

    if callback.data == "timetable_today":
        pass
    elif callback.data == "timetable_nextday":
        selected_day += timedelta(days=1)
        current_week: str = "Знаменатель" if selected_day.isocalendar().week % 2 == 0 else "Числитель"
    elif callback.data == "timetable_current_week":
        start_of_week = selected_day - timedelta(days=selected_day.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        schedule_for_week_str = f"Расписание на текущую неделю ({current_week}) с {start_of_week.strftime('%d.%m.%Y')} по {end_of_week.strftime('%d.%m.%Y')}:\n\n"
        for i in range(7):
            day = start_of_week + timedelta(days=i)
            if i == 6 and day.strftime("%A") == "Воскресенье":
                continue
            if i != 0 and day.strftime("%A")[0].isupper():
                schedule_for_week_str += f"{day.strftime('%A')} ({current_week}):\n"
            schedule_for_week_str += (
                scheduleParser.getScheduleForDay(
                    existingUser.course,
                    existingUser.direction,
                    existingUser.profile,
                    existingUser.group,
                    current_week,
                    day.strftime("%A").capitalize(),
                )
                + "\n\n"
            )
        await callback.message.answer(text=schedule_for_week_str.strip())
        return await callback.answer("Ваше расписание")

    elif callback.data == "timetable_next_week":
        start_of_week = selected_day - timedelta(days=selected_day.weekday()) + timedelta(weeks=1)
        end_of_week = start_of_week + timedelta(days=6)
        next_week_type = "Знаменатель" if current_week == "Числитель" else "Числитель"
        schedule_for_week_str = f"Расписание на следующую неделю ({next_week_type}) с {start_of_week.strftime('%d.%m.%Y')} по {end_of_week.strftime('%d.%m.%Y')}:\n\n"
        for i in range(7):
            day = start_of_week + timedelta(days=i)
            if i == 6 and day.strftime("%A") == "Воскресенье":
                continue
            if i != 0 and day.strftime("%A")[0].isupper():
                schedule_for_week_str += f"{day.strftime('%A')} ({next_week_type}):\n"
            schedule_for_week_str += (
                scheduleParser.getScheduleForDay(
                    existingUser.course,
                    existingUser.direction,
                    existingUser.profile,
                    existingUser.group,
                    next_week_type,
                    day.strftime("%A").capitalize(),
                )
                + "\n\n"
            )
        await callback.message.answer(text=schedule_for_week_str.strip())
        return await callback.answer("Ваше расписание")

    schedule_for_week_str = f"Расписание на {selected_day.strftime('%A')} ({current_week}):\n\n"
    schedule_for_week_str += (
        scheduleParser.getScheduleForDay(
            existingUser.course,
            existingUser.direction,
            existingUser.profile,
            existingUser.group,
            current_week,
            selected_day.strftime("%A").capitalize(),
        )
        + "\n\n"
    )

    await callback.message.answer(text=schedule_for_week_str.strip())
    await callback.answer("Ваше расписание")


@router.callback_query(F.data == "settings")
async def settings(callback: CallbackQuery, username: str, db) -> None:
    logger.opt(colors=True).debug(f"[<y>{username}</y>]: Called <b>settings</b> callback")

    # TODO: убрать это в отдельный метод в модель User
    async with db.session() as session:
        async with session.begin():
            existUser: bool = await is_registered(session, callback.from_user.id)
    if not existUser:
        return await callback.answer("Вы не зарегистрированы!")
    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(text="Обратная связь", callback_data="feedback"))
    keyboard.row(InlineKeyboardButton(text="Удалить аккаунт", callback_data="delete_user"))
    keyboard.row(InlineKeyboardButton(text="Назад", callback_data="menu"))
    await callback.message.edit_text("Настройки", reply_markup=keyboard.as_markup())
    return await callback.answer()


@router.callback_query(F.data == "delete_user")
async def deleteUser(callback: CallbackQuery, username: str, state: FSMContext, db, bot: Bot) -> None:
    logger.opt(colors=True).debug(f"[<y>{username}</y>]: Called <b>delete_user</b> callback")
    user_id = callback.from_user.id
    # TODO: убрать это в отдельный метод в модель User
    async with db.session() as session:
        async with session.begin():
            existUser: bool = await is_registered(session, user_id)
            if not existUser:
                await callback.answer("Вы не зарегистрированы!")
            else:
                await delete_user(session, user_id)
                await callback.answer("Вы успешно удалили свой аккаунт")

    await callback.message.delete()

    return await start(msg=callback.message, state=state, username=username, db=db)
