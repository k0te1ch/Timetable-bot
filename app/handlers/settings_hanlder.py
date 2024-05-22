from aiogram import F, Router
from aiogram.types import CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from filters.dispatcherFilters import IsPrivate
from loguru import logger

router = Router(name="settings_handler")
router.message.filter(IsPrivate)


@router.callback_query(F.data == "settings")
async def settings(callback: CallbackQuery, username: str, existUser: bool) -> None:
    logger.opt(colors=True).debug(f"[<y>{username}</y>]: Called <b>settings</b> callback")

    if not existUser:
        return await callback.answer("Вы не зарегистрированы!")

    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(text="Обратная связь", callback_data="feedback"))
    keyboard.row(InlineKeyboardButton(text="Удалить аккаунт", callback_data="delete_user"))
    keyboard.row(InlineKeyboardButton(text="Назад", callback_data="menu"))
    await callback.message.edit_text("Настройки", reply_markup=keyboard.as_markup())
    return await callback.answer()
