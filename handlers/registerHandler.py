from aiogram import F, Router
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from loguru import logger
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton
from forms.register import Register
from utils.context import context
from filters.dispatcherFilters import IsPrivate
from utils.ScheduleParser import scheduleParser


router = Router(name="registerHandler")
router.message.filter(IsPrivate)

from bot import db


@router.message(F.text, CommandStart())
async def start(msg: Message, state: FSMContext, username: str) -> None:  # TODO
    logger.opt(colors=True).debug(f"[<y>{username}</y>]: Called <b>/start</b> command")

    await state.set_state(Register.course)

    tableObj = scheduleParser.getTableObj()
    await state.update_data(tableObj=tableObj)
    keyboard = InlineKeyboardBuilder()
    for num, key in enumerate(tableObj.keys()):
        keyboard.row(InlineKeyboardButton(text=key, callback_data=f"course_{num}"))

    return await msg.answer(
        "Регистрация: Выберете ваш курс",
        reply_markup=keyboard.as_markup(resize_keyboard=True),
    )


@router.callback_query(F.data == "cancel", StateFilter(Register))
async def cancel(callback: CallbackQuery, state: FSMContext, language: str, username: str) -> None:
    logger.opt(colors=True).debug(f"[<y>{username}</y>]: Cancel registration")
    await callback.message.edit_text(
        "Регистрация: " + context[language].canceled,
        reply_markup=ReplyKeyboardRemove(remove_keyboard=True),
    )
    await state.clear()


@router.callback_query(F.data.contains("course_"), Register.course)
async def getCourse(
    callback: CallbackQuery, state: FSMContext, username: str
) -> None:
    
    await state.set_state(Register.direction)
    tableObj = (await state.get_data())["tableObj"]
    course = list(tableObj.keys())[int(callback.data[len("course_"):])]
    tableObj = tableObj[course]
    await state.update_data(course=course)
    keyboard = InlineKeyboardBuilder()
    await state.update_data(tableObj=tableObj)
    for num, key in enumerate(tableObj.keys()):
        keyboard.row(InlineKeyboardButton(text=key, callback_data=f"direction_{num}"))
    logger.opt(colors=True).debug(f"[<y>{username}</y>]: Get course")
    await callback.message.edit_text(
        "Регистрация: Выберете ваше направление",
        reply_markup=keyboard.as_markup(resize_keyboard=True),
    )


@router.callback_query(F.data.contains("direction_"), Register.direction)
async def getDirection(callback: CallbackQuery, state: FSMContext, username: str
) -> None:

    await state.set_state(Register.profile)
    tableObj = (await state.get_data())["tableObj"]
    direction = list(tableObj.keys())[int(callback.data[len("direction_") :])]
    tableObj = tableObj[direction]
    await state.update_data(direction = direction)
    keyboard = InlineKeyboardBuilder()
    await state.update_data(tableObj=tableObj)
    for num, key in enumerate(tableObj.keys()):
        keyboard.row(InlineKeyboardButton(text=key, callback_data=f"profile_{num}"))
    logger.opt(colors=True).debug(f"[<y>{username}</y>]: Get direction")
    await callback.message.edit_text(
        "Регистрация: Выберете ваш профиль",
        reply_markup=keyboard.as_markup(resize_keyboard=True),
    )


@router.callback_query(F.data.contains("profile_"), Register.profile)
async def getProfile(
    callback: CallbackQuery, state: FSMContext, username: str
) -> None:
    await state.set_state(Register.group)
    tableObj = (await state.get_data())["tableObj"]
    profile = list(tableObj.keys())[int(callback.data[len("profile_") :])]
    tableObj = tableObj[profile]
    await state.update_data(profile=profile)
    keyboard = InlineKeyboardBuilder()
    await state.update_data(tableObj=tableObj)
    for num, key in enumerate(tableObj.keys()):
        keyboard.row(InlineKeyboardButton(text=key, callback_data=f"group_{num}"))
    logger.opt(colors=True).debug(f"[<y>{username}</y>]: Get profile")
    await callback.message.edit_text(
        "Регистрация: Выберете вашу группу",
        reply_markup=keyboard.as_markup(resize_keyboard=True),
    )


@router.callback_query(F.data.contains("group_"), Register.group)
async def getGroup(callback: CallbackQuery, state: FSMContext, username: str
) -> None:
    logger.opt(colors=True).debug(f"[<y>{username}</y>]: Get group")
    info: dict[str] = await state.get_data()
    from models.user import User

    userId = callback.from_user.id

    # Создаем нового пользователя на основе данных из сообщения
    new_user = User(
        id=userId,
        course=info["course"],
        direction=info["direction"],
        profile=info["profile"],
        group=list(info["tableObj"].keys())[int(callback.data[len("group_"):])],
    )

    session = db.session()
    existingUser = session.query(User).filter_by(id=userId).first()

    if existingUser is None:
        # Добавляем пользователя в сессию
        session.add(new_user)

        # Подтверждаем изменения (выполняем коммит)
        session.commit()
        from handlers.mainHandler import menuCallback
        session.close()
        await state.clear()
        await callback.answer(
            "Вы успешно зарегистрированы!"
        )
        return await menuCallback(callback, username, state, anotherHandler = True)  # TODO костыль
    await callback.answer("Вы уже зарегистрированы!")
    # Закрываем сессию
    session.close()
    await state.clear()