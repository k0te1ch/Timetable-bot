from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from config import ADMIN_CHAT_ID
from filters.dispatcherFilters import IsPrivate
from forms.feedback import Feedback
from loguru import logger

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
    await message.answer("Спасибо за обратную связь!")
    await state.clear()


@router.callback_query(F.data == "cancel", StateFilter(Feedback))
async def cancel(callback: CallbackQuery, state: FSMContext, username: str) -> None:
    logger.opt(colors=True).debug(f"[<y>{username}</y>]: Cancel feedback")
    await callback.message.edit_text(
        "Отправка сообщения отменена",
        reply_markup=ReplyKeyboardRemove(remove_keyboard=True),
    )
    await state.clear()
