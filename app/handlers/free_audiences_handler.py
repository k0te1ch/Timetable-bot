from typing import Any

from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from filters.dispatcherFilters import IsPrivate
from forms.free_audiences import FreeAudiences
from loguru import logger
from utils.ScheduleParser import scheduleParser

# TODO: Добавить кнопку отмены


async def handle_registration_step(callback: CallbackQuery, state: FSMContext) -> None:

    steps: tuple[str] = FreeAudiences.__state_names__
    current_state: str = await state.get_state()
    indexStep: int = steps.index(current_state)
    state_data: dict[str, Any] = await state.get_data()
    free_audiences: dict[str, Any] = state_data["free_audiences"]

    if callback.data == "back":

        await state.clear()
        indexStep -= 1
        current_state = steps[indexStep]
        state_data.pop(current_state.split(":")[-1])
        free_audiences = state_data["free_audiences_Glob"]
        for key in FreeAudiences.__states__:
            if key._state in state_data:
                free_audiences = free_audiences[state_data[key._state]]

        state_data["free_audiences"] = free_audiences
        await state.set_state(current_state)

        await state.update_data(state_data)
        callback_text = "Вы вернулись на предыдущий этап поиска свободной аудитории"
        while len(free_audiences) == 1 and indexStep != 0:
            await state.clear()
            indexStep -= 1
            current_state = steps[indexStep]
            state_data.pop(current_state.split(":")[-1])
            free_audiences = state_data["free_audiences_Glob"]
            for key in FreeAudiences.__states__:
                if key._state in state_data:
                    free_audiences = free_audiences[state_data[key._state]]

            state_data["free_audiences"] = free_audiences
            await state.set_state(current_state)
            await state.update_data(state_data)

    elif callback.data.startswith(f"{current_state.split(':')[-1]}_"):
        selected_value = list(free_audiences.keys())[int(callback.data.split("_")[-1])]
        free_audiences = free_audiences[selected_value]
        await state.update_data({current_state.split(":")[-1]: selected_value, "free_audiences": free_audiences})
        indexStep += 1
        current_state = steps[indexStep]
        await state.set_state(current_state)
        callback_text = f'Вы выбрали "{selected_value}"'

        while len(free_audiences) == 1 and indexStep != 3:
            # Автоматически выбираем единственный вариант
            next_selected_value = list(free_audiences.keys())[0]
            free_audiences = free_audiences[next_selected_value]
            await state.update_data(
                {current_state.split(":")[-1]: next_selected_value, "free_audiences": free_audiences}
            )
            indexStep += 1
            current_state = steps[indexStep]
            await state.set_state(current_state)
    else:
        return

    keyboard = InlineKeyboardBuilder()
    for num, key in enumerate(free_audiences.keys()):
        keyboard.row(InlineKeyboardButton(text=key, callback_data=f"{current_state.split(':')[-1]}_{num}"))

    if indexStep != 0:
        keyboard.row(InlineKeyboardButton(text="Назад", callback_data="back"))

    step_text = "Поиск свободной аудитории: Выберете " + ["день", "нужное время", "числитель/знаменатель"][indexStep]
    await callback.message.edit_text(step_text, reply_markup=keyboard.as_markup(resize_keyboard=True))
    await callback.answer(callback_text)


router = Router(name="free_audiences_handler")
router.message.filter(IsPrivate)


@router.callback_query(F.data == "free_audiences")
async def free_audiences(callback: CallbackQuery, state: FSMContext):
    await state.set_state(FreeAudiences.day)

    free_audiences = scheduleParser.getFreeAudiencesObj()
    await state.update_data(free_audiences=free_audiences, free_audiences_glob=free_audiences)

    keyboard = InlineKeyboardBuilder()
    for num, key in enumerate(free_audiences.keys()):
        keyboard.row(InlineKeyboardButton(text=key, callback_data=f"day_{num}"))

    await callback.message.answer(
        "Поиск свободной аудитории: Выберете день",
        reply_markup=keyboard.as_markup(resize_keyboard=True),
    )

    await callback.answer()


@router.callback_query(F.data == "back", StateFilter(FreeAudiences))
async def handle_back(callback: CallbackQuery, state: FSMContext, username: str) -> None:
    logger.opt(colors=True).debug(f"[<y>{username}</y>]: Go to back state")
    await handle_registration_step(callback, state)


@router.callback_query(F.data.contains("day_"), FreeAudiences.day)
async def get_day(callback: CallbackQuery, state: FSMContext, username: str) -> None:
    logger.opt(colors=True).debug(f"[<y>{username}</y>]: Get day")
    await handle_registration_step(callback, state)


@router.callback_query(F.data.contains("time_"), FreeAudiences.time)
async def get_time(callback: CallbackQuery, state: FSMContext, username: str) -> None:
    logger.opt(colors=True).debug(f"[<y>{username}</y>]: Get time")
    await handle_registration_step(callback, state)


@router.callback_query(F.data.contains("numerator_"), FreeAudiences.numerator)
async def get_numerator(callback: CallbackQuery, state: FSMContext, username: str) -> None:
    logger.opt(colors=True).debug(f"[<y>{username}</y>]: Get numerator")

    state_data = await state.get_data()

    await state.clear()
    numerator = list(state_data["free_audiences"].keys())[int(callback.data[len("numerator_") :])]
    await callback.answer("Готово!")
    await callback.message.edit_text(scheduleParser.getFreeAudiences(state_data["day"], state_data["time"], numerator))
