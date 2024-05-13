from typing import Any

from aiogram import F, Router
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database.services.user import create_user, is_registered
from filters.dispatcherFilters import IsPrivate
from forms.form_utils import handle_step
from forms.register import Register
from loguru import logger
from utils.ScheduleParser import scheduleParser

router = Router(name="registerHandler")
router.message.filter(IsPrivate)


# TODO: Вынести form_maker в botMethods
# TODO: Добавить логирование


async def handle_registration_step(callback: CallbackQuery, state: FSMContext) -> None:

    steps: tuple[str] = Register.__state_names__
    current_state: str = await state.get_state()
    indexStep: int = steps.index(current_state)
    state_data: dict[str, Any] = await state.get_data()
    tableObj: dict[str, Any] = state_data["tableObj"]

    if callback.data == "back":

        await state.clear()
        indexStep -= 1
        current_state = steps[indexStep]
        state_data.pop(current_state.split(":")[-1])
        tableObj = state_data["tableObjGlob"]
        for key in Register.__states__:
            if key._state in state_data:
                tableObj = tableObj[state_data[key._state]]

        state_data["tableObj"] = tableObj
        await state.set_state(current_state)

        await state.update_data(state_data)
        # TODO: Автоматом скипать кнопку, если она одна
        callback_text = "Вы вернулись на предыдущий этап регистрации"
        while len(tableObj) == 1 and indexStep != 0:
            # Автоматически выбираем единственный вариант
            await state.clear()
            indexStep -= 1
            current_state = steps[indexStep]
            state_data.pop(current_state.split(":")[-1])
            tableObj = state_data["tableObjGlob"]
            for key in Register.__states__:
                if key._state in state_data:
                    tableObj = tableObj[state_data[key._state]]

            state_data["tableObj"] = tableObj
            await state.set_state(current_state)
            await state.update_data(state_data)

    elif callback.data.startswith(f"{current_state.split(':')[-1]}_"):
        selected_value = list(tableObj.keys())[int(callback.data.split("_")[-1])]
        tableObj = tableObj[selected_value]
        await state.update_data({current_state.split(":")[-1]: selected_value, "tableObj": tableObj})
        indexStep += 1
        current_state = steps[indexStep]
        await state.set_state(current_state)
        callback_text = f'Вы выбрали "{selected_value}"'

        while len(tableObj) == 1 and indexStep != 3:
            # Автоматически выбираем единственный вариант
            next_selected_value = list(tableObj.keys())[0]
            tableObj = tableObj[next_selected_value]
            await state.update_data({current_state.split(":")[-1]: next_selected_value, "tableObj": tableObj})
            indexStep += 1
            current_state = steps[indexStep]
            await state.set_state(current_state)
    else:
        return

    keyboard = InlineKeyboardBuilder()
    for num, key in enumerate(tableObj.keys()):
        keyboard.row(InlineKeyboardButton(text=key, callback_data=f"{current_state.split(':')[-1]}_{num}"))

    if indexStep != 0:
        keyboard.row(InlineKeyboardButton(text="Назад", callback_data="back"))

    step_text = "Регистрация: Выберете " + ["ваш курс", "ваше направление", "ваш профиль", "вашу группу"][indexStep]
    await callback.message.edit_text(step_text, reply_markup=keyboard.as_markup(resize_keyboard=True))
    await callback.answer(callback_text)


# Universal function to handle registration steps
# form_maker


# Handle /start command
@router.message(F.text, CommandStart())
async def start(msg: Message, state: FSMContext, username: str, db) -> None:
    logger.opt(colors=True).debug(f"[<y>{username}</y>]: Called <b>/start</b> command")

    async with db.session() as session:
        async with session.begin():
            existUser: bool = await is_registered(session, msg.from_user.id)

    if existUser:
        from handlers.mainHandler import menu

        return await menu(msg=msg, username=username, state=state, db=db)

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
    await handle_step(
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
    await handle_step(callback, state)


@router.callback_query(F.data.contains("direction_"), Register.direction)
async def get_direction(callback: CallbackQuery, state: FSMContext, username: str) -> None:
    await handle_step(callback, state)


@router.callback_query(F.data.contains("profile_"), Register.profile)
async def get_profile(callback: CallbackQuery, state: FSMContext, username: str) -> None:
    await handle_step(callback, state)


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
        from handlers.mainHandler import menuCallback

        return await menuCallback(callback=callback, username=username, state=state, db=db)

    await callback.answer("Вы уже зарегистрированы!")
