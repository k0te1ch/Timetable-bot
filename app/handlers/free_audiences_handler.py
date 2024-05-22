from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from filters.dispatcherFilters import IsPrivate
from forms.form_utils import form_step
from forms.free_audiences import FreeAudiences
from loguru import logger
from utils.ScheduleParser import scheduleParser

# TODO: Добавить кнопку отмены


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
    await form_step(
        callback,
        state,
        FreeAudiences,
        "free_audiences",
        "free_audiences_glob",
        ["день", "нужное время", "числитель/знаменатель"],
        "Поиск свободной аудитории: Выберете ",
        "поиска свободной аудитории",
    )


@router.callback_query(F.data.contains("day_"), FreeAudiences.day)
async def get_day(callback: CallbackQuery, state: FSMContext, username: str) -> None:
    logger.opt(colors=True).debug(f"[<y>{username}</y>]: Get day")
    await form_step(
        callback,
        state,
        FreeAudiences,
        "free_audiences",
        "free_audiences_glob",
        ["день", "нужное время", "числитель/знаменатель"],
        "Поиск свободной аудитории: Выберете ",
        "поиска свободной аудитории",
    )


@router.callback_query(F.data.contains("time_"), FreeAudiences.time)
async def get_time(callback: CallbackQuery, state: FSMContext, username: str) -> None:
    logger.opt(colors=True).debug(f"[<y>{username}</y>]: Get time")
    await form_step(
        callback,
        state,
        FreeAudiences,
        "free_audiences",
        "free_audiences_glob",
        ["день", "нужное время", "числитель/знаменатель"],
        "Поиск свободной аудитории: Выберете ",
        "поиска свободной аудитории",
    )


@router.callback_query(F.data.contains("numerator_"), FreeAudiences.numerator)
async def get_numerator(callback: CallbackQuery, state: FSMContext, username: str) -> None:
    logger.opt(colors=True).debug(f"[<y>{username}</y>]: Get numerator")

    state_data = await state.get_data()

    await state.clear()
    numerator = list(state_data["free_audiences"].keys())[int(callback.data[len("numerator_") :])]
    await callback.answer("Готово!")
    await callback.message.edit_text(scheduleParser.getFreeAudiences(state_data["day"], state_data["time"], numerator))
