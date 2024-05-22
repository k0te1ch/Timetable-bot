from aiogram import F, Router
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database.services.user import create_user
from filters.dispatcherFilters import IsPrivate
from forms.form_utils import form_step
from forms.register import Register
from loguru import logger
from utils.ScheduleParser import scheduleParser

router = Router(name="registerHandler")
router.message.filter(IsPrivate)


# TODO: Добавить логирование


# Handle /start command
@router.message(F.text, CommandStart())
async def start(msg: Message, state: FSMContext, username: str, db, existUser: bool) -> None:
    logger.opt(colors=True).debug(f"[<y>{username}</y>]: Called <b>/start</b> command")

    if existUser:
        from handlers.main_handler import menu

        return await menu(msg=msg, username=username, state=state, db=db, existUser=existUser)

    await state.set_state(Register.course)

    tableObj = scheduleParser.getTableObj()
    await state.update_data(tableObj=tableObj, tableObjGlob=tableObj)

    keyboard = InlineKeyboardBuilder()
    for num, key in enumerate(tableObj.keys()):
        keyboard.row(InlineKeyboardButton(text=key, callback_data=f"course_{num}"))

    await msg.answer(
        "Регистрация: Выберете ваш курс",
        reply_markup=keyboard.as_markup(resize_keyboard=True),
    )


# Handle registration steps
@router.callback_query(F.data == "back", StateFilter(Register))
async def handle_back(callback: CallbackQuery, state: FSMContext) -> None:
    await form_step(
        callback,
        state,
        Register,
        "tableObj",
        "tableObjGlob",
        ["ваш курс", "ваше направление", "ваш профиль", "вашу группу"],
        "Регистрация: Выберете ",
        "регистрации",
    )


@router.callback_query(F.data.contains("course_"), Register.course)
async def get_course(callback: CallbackQuery, state: FSMContext, username: str) -> None:
    await form_step(
        callback,
        state,
        Register,
        "tableObj",
        "tableObjGlob",
        ["ваш курс", "ваше направление", "ваш профиль", "вашу группу"],
        "Регистрация: Выберете ",
        "регистрации",
    )


@router.callback_query(F.data.contains("direction_"), Register.direction)
async def get_direction(callback: CallbackQuery, state: FSMContext, username: str) -> None:
    await form_step(
        callback,
        state,
        Register,
        "tableObj",
        "tableObjGlob",
        ["ваш курс", "ваше направление", "ваш профиль", "вашу группу"],
        "Регистрация: Выберете ",
        "регистрации",
    )


@router.callback_query(F.data.contains("profile_"), Register.profile)
async def get_profile(callback: CallbackQuery, state: FSMContext, username: str) -> None:
    await form_step(
        callback,
        state,
        Register,
        "tableObj",
        "tableObjGlob",
        ["ваш курс", "ваше направление", "ваш профиль", "вашу группу"],
        "Регистрация: Выберете ",
        "регистрации",
    )


@router.callback_query(F.data.contains("group_"), Register.group)
async def get_group(callback: CallbackQuery, state: FSMContext, username: str, db) -> None:
    logger.opt(colors=True).debug(f"[<y>{username}</y>]: Get group")

    state_data = await state.get_data()

    group = list(state_data["tableObj"].keys())[int(callback.data[len("group_") :])]

    async with db.session() as session:
        async with session.begin():
            result: bool = await create_user(
                session=session,
                user_id=callback.from_user.id,
                course=state_data["course"],
                direction=state_data["direction"],
                profile=state_data["profile"],
                group=group,
            )
    await state.clear()
    if result:
        await callback.answer("Вы успешно зарегистрированы!")
        from handlers.main_handler import menuCallback

        return await menuCallback(callback=callback, username=username, state=state, db=db, existUser=True)

    await callback.answer("Вы уже зарегистрированы!")
