from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from config import ADMIN_CHAT_ID
from forms.feedback import Feedback
from aiogram.filters import StateFilter
from aiogram.types import CallbackQuery, ReplyKeyboardRemove, Message
from loguru import logger
from utils.context import context

router = Router(name="feedbackHandler")

@router.callback_query(F.data == "feedback")
async def feedback(callback: CallbackQuery, state: FSMContext):
    await callback.answer("Введите сообщение для обратной связи")
    await callback.message.answer("Введите сообщение для обратной связи")
    
    await state.set_state(Feedback.message)


@router.message(StateFilter(Feedback.message))
async def feedback_message(message: Message, state: FSMContext, username, bot):
    logger.opt(colors=True).debug(f"[<y>{username}</y>]: Send Feedback")
    await bot.send_message(ADMIN_CHAT_ID, message.text)
    await message.answer("Спасибо за обратную связь!")
    await state.clear()


@router.callback_query(F.data == "cancel", StateFilter(Feedback))
async def cancel(callback: CallbackQuery, state: FSMContext, language: str, username: str) -> None:
    logger.opt(colors=True).debug(f"[<y>{username}</y>]: Cancel feedback")
    await callback.message.edit_text(
        "Сообщение " + context[language].feedback,
        reply_markup=ReplyKeyboardRemove(remove_keyboard=True),
    )
    await state.clear()