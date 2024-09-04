from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from database.services.user import delete_user_by_telegram_id, switch_notify_for_user
from filters.dispatcherFilters import IsPrivate
from handlers.register_handler import start
from loguru import logger

router = Router(name="user_handler")
router.message.filter(IsPrivate)


# TODO: писать включить или выключить уведомления


@router.callback_query(F.data == "delete_user")
async def deleteUser(callback: CallbackQuery, username: str, state: FSMContext, db) -> None:
    logger.opt(colors=True).debug(f"[<y>{username}</y>]: Called <b>delete_user</b> callback")
    user_id = callback.from_user.id
    async with db.session() as session:
        async with session.begin():
            if await delete_user_by_telegram_id(session, user_id):
                await callback.answer("Вы успешно удалили свой аккаунт")
            else:
                await callback.answer("Вы не зарегистрированы!")

    await callback.message.delete()

    return await start(msg=callback.message, state=state, username=username, db=db, existUser=False)


@router.callback_query(F.data == "notify_user")
async def notify_user(callback: CallbackQuery, username: str, db) -> None:
    logger.opt(colors=True).debug(f"[<y>{username}</y>]: Called <b>notify_user</b> callback")

    async with db.session() as session:
        async with session.begin():
            result = await switch_notify_for_user(session=session, user_id=callback.from_user.id)
            await callback.answer("Уведомления включены" if result else "Уведомления выключены")
