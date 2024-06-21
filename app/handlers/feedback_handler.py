from aiogram import F, Router
<<<<<<< HEAD
from aiogram.filters import Command, StateFilter
=======
from aiogram.filters import StateFilter
>>>>>>> Timetable-bot/main
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from config import ADMIN_CHAT_ID
from filters.dispatcherFilters import IsPrivate
from forms.feedback import Feedback
from loguru import logger
<<<<<<< HEAD

# TODO: Логирование

router = Router(name="feedback_handler")
router.message.filter(IsPrivate)


async def feedback(message: Message, state: FSMContext):
    await message.answer("Введите сообщение для обратной связи")
    await state.set_state(Feedback.message)


@router.message(F.text, Command("feedback"))
async def feedback_command(message: Message, state: FSMContext):
    await feedback(message, state)


@router.callback_query(F.data == "feedback")
async def feedback_callback(callback: CallbackQuery, state: FSMContext):
    await callback.answer("Введите сообщение для обратной связи")
    await feedback(callback.message, state)


@router.message(StateFilter(Feedback.message))
async def feedback_message(message: Message, state: FSMContext):
    await message.forward(ADMIN_CHAT_ID)
    logger.debug(f"Переслано сообщение от пользователя {message.chat.id} в чат {ADMIN_CHAT_ID}")
=======
from services.context import context

# TODO: Логирование
# TODO: Добавить кнопку отмены

router = Router(name="feedbackHandler")
router.message.filter(IsPrivate)


@router.callback_query(F.data == "feedback")
async def feedback(callback: CallbackQuery, state: FSMContext):
    await callback.answer("Введите сообщение для обратной связи")
    await callback.message.answer("Введите сообщение для обратной связи")
    await state.update_data(user_chat_id=callback.message.chat.id)

    await state.set_state(Feedback.message)


@router.message(StateFilter(Feedback.message))
async def feedback_message(message: Message, state: FSMContext, bot):
    user_chat_id = (await state.get_data()).get("user_chat_id")
    await message.forward(ADMIN_CHAT_ID)
    logger.debug(f"Переслано сообщение от пользователя {user_chat_id} в чат {ADMIN_CHAT_ID}")
>>>>>>> Timetable-bot/main
    await message.answer("Спасибо за обратную связь!")
    await state.clear()


@router.callback_query(F.data == "cancel", StateFilter(Feedback))
<<<<<<< HEAD
async def cancel(callback: CallbackQuery, state: FSMContext, username: str) -> None:
    logger.opt(colors=True).debug(f"[<y>{username}</y>]: Cancel feedback")
    await callback.message.edit_text(
        "Отправка сообщения отменена",
=======
async def cancel(callback: CallbackQuery, state: FSMContext, language: str, username: str) -> None:
    logger.opt(colors=True).debug(f"[<y>{username}</y>]: Cancel feedback")
    await callback.message.edit_text(
        "Сообщение " + context[language].feedback,
>>>>>>> Timetable-bot/main
        reply_markup=ReplyKeyboardRemove(remove_keyboard=True),
    )
    await state.clear()
