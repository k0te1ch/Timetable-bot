from datetime import datetime, timedelta

from aiogram import F, Router
from aiogram.types import CallbackQuery
from config import TIMEZONE
from database.models import User
from database.services.group import get_group_by_id
from database.services.user import get_users_for_notify
from filters.dispatcherFilters import IsPrivate
from loguru import logger
from utils.schedule_parser import schedule_parser

router = Router(name="schedule_handler")
router.message.filter(IsPrivate)


async def next_para(time: str) -> None:
    from bot import bot
    from database import db

    logger.debug("Начало отправок сообщений")

    async with db.session() as session:
        async with session.begin():
            users: list[User] = await get_users_for_notify(session)

    for user in users:

        import locale

        locale.setlocale(locale.LC_ALL, "ru_RU.UTF-8")  # FIXME: костыль

        selected_day: datetime = datetime.now(TIMEZONE)
        current_week: str = (
            "Знаменатель" if selected_day.isocalendar().week % 2 != 0 else "Числитель"
        )  # FIXME: Костыль

        subject: str | None = await schedule_parser.getScheduleForTime(
            user.group,
            current_week,
            selected_day.strftime("%A").capitalize(),
            time,
        )
        if subject is None:
            logger.debug(
                f"Сообщение не отправлено за 5 минут до начала пары - у пользователя {user.telegram_id} нет пары"
            )
        await bot.send_message(user.telegram_id, subject)
        logger.debug(f"Отправлено сообщение пользователю {user.telegram_id} за 5 минут до начала пары")
    logger.debug("Все сообщения отправлены")


async def next_day() -> None:
    from bot import bot
    from database import db

    # TODO: Тип дня

    logger.debug("Начало отправок сообщений")

    async with db.session() as session:
        async with session.begin():
            users: list[User] = await get_users_for_notify(session)

    for user in users:

        import locale

        locale.setlocale(locale.LC_ALL, "ru_RU.UTF-8")  # FIXME: костыль

        selected_day: datetime = datetime.now(TIMEZONE) + timedelta(hours=2)
        current_week: str = (
            "Знаменатель" if selected_day.isocalendar().week % 2 != 0 else "Числитель"
        )  # FIXME: костыль

        subject = await schedule_parser.getScheduleForDay(
            user.group,
            current_week,
            selected_day.strftime("%A").capitalize(),
        )
        await bot.send_message(user.telegram_id, subject)
        logger.debug(f"Отправлено сообщение пользователю {user.telegram_id} на следующий день")
    logger.debug("Все сообщения отправлены")


# FIXME: что это такое? 👇 (Отрефакторить эту тему)
@router.callback_query(F.data == "timetable_today")
@router.callback_query(F.data == "timetable_nextday")
@router.callback_query(F.data == "timetable_current_week")
@router.callback_query(F.data == "timetable_next_week")
async def timetableForDay(callback: CallbackQuery, username: str, existingUser: User | None, db) -> None:
    logger.opt(colors=True).debug(f"[<y>{username}</y>]: Called <b>timetable</b> callback")

    if existingUser is None:
        return await callback.answer("Вы не зарегистрированы!")

    import locale

    locale.setlocale(locale.LC_ALL, "ru_RU.UTF-8")  # FIXME: костыль

    selected_day: datetime = datetime.now(TIMEZONE)
    current_week: str = "Знаменатель" if selected_day.isocalendar().week % 2 != 0 else "Числитель"  # FIXME: Костыль

    if callback.data == "timetable_today":
        pass
    elif callback.data == "timetable_nextday":
        selected_day += timedelta(days=1)
        current_week: str = (
            "Знаменатель" if selected_day.isocalendar().week % 2 != 0 else "Числитель"
        )  # FIXME: костыль
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
            async with db.session() as session:
                async with session.begin():
                    group = await get_group_by_id(session, existingUser.group_id)
                schedule_for_week_str += (
                    await schedule_parser.getScheduleForDay(
                        group,
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
            async with db.session() as session:
                async with session.begin():
                    group = await get_group_by_id(session, existingUser.group_id)
            schedule_for_week_str += (
                await schedule_parser.getScheduleForDay(
                    group,
                    next_week_type,
                    day.strftime("%A").capitalize(),
                )
                + "\n\n"
            )
        await callback.message.answer(text=schedule_for_week_str.strip())
        return await callback.answer("Ваше расписание")

    schedule_for_week_str = f"Расписание на {selected_day.strftime('%A')} ({current_week}):\n\n"
    async with db.session() as session:
        async with session.begin():
            group = await get_group_by_id(session, existingUser.group_id)

    schedule_for_week_str += (
        await schedule_parser.getScheduleForDay(
            group,
            current_week,
            selected_day.strftime("%A").capitalize(),
        )
        + "\n\n"
    )

    await callback.message.answer(text=schedule_for_week_str.strip())
    await callback.answer("Ваше расписание")
