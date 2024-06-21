from datetime import datetime, timedelta

from aiogram import F, Router
from aiogram.types import CallbackQuery
from config import TIMEZONE
from database.models.user import User
from database.services.user import get_users_for_notify
from filters.dispatcherFilters import IsPrivate
from loguru import logger
from utils.ScheduleParser import scheduleParser

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
                # TODO: Если выходной - не присылать каждую пару о паре, объединить воедино

                import locale

                locale.setlocale(locale.LC_ALL, "ru_RU.UTF-8")  # FIXME: костыль

                selected_day: datetime = datetime.now(TIMEZONE)
                current_week: str = "Знаменатель" if selected_day.isocalendar().week % 2 == 0 else "Числитель"

                subject: str | None = scheduleParser.getScheduleForTime(
                    user.course,
                    user.direction,
                    user.profile,
                    user.group,
                    current_week,
                    selected_day.strftime("%A").capitalize(),
                    time,
                )
                if subject is None:
                    logger.debug(
                        f"Сообщение не отправлено за 5 минут до начала пары - у пользователя {user.id} нет пары"
                    )
                await bot.send_message(user.id, subject)
                logger.debug(f"Отправлено сообщение пользователю {user.id} за 5 минут до начала пары")
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
                current_week: str = "Знаменатель" if selected_day.isocalendar().week % 2 == 0 else "Числитель"

                subject = scheduleParser.getScheduleForDay(
                    user.course,
                    user.direction,
                    user.profile,
                    user.group,
                    current_week,
                    selected_day.strftime("%A").capitalize(),
                )
                await bot.send_message(user.id, subject)
<<<<<<< HEAD
                logger.debug(f"Отправлено сообщение пользователю {user.id} на следующий день")
=======
                logger.debug("Отправлено сообщение пользователю {user.id} на следующий день")
>>>>>>> Timetable-bot/main
    logger.debug("Все сообщения отправлены")


# FIXME: что это такое? 👇 (Отрефакторить эту тему)
@router.callback_query(F.data == "timetable_today")
@router.callback_query(F.data == "timetable_nextday")
@router.callback_query(F.data == "timetable_current_week")
@router.callback_query(F.data == "timetable_next_week")
async def timetableForDay(callback: CallbackQuery, username: str, existingUser: User | None) -> None:
    logger.opt(colors=True).debug(f"[<y>{username}</y>]: Called <b>timetable</b> callback")

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
