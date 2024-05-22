from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from database.services.user import delete_user, is_registered
from filters.dispatcherFilters import IsPrivate
from handlers.admin_panel import start
from loguru import logger

router = Router(name="user_handler")
router.message.filter(IsPrivate)


@router.callback_query(F.data == "delete_user")
async def deleteUser(callback: CallbackQuery, username: str, state: FSMContext, db) -> None:
    logger.opt(colors=True).debug(f"[<y>{username}</y>]: Called <b>delete_user</b> callback")
    user_id = callback.from_user.id
    async with db.session() as session:
        async with session.begin():
            existUser: bool = await is_registered(session, user_id)
            if not existUser:
                await callback.answer("Вы не зарегистрированы!")
            else:
                await delete_user(session, user_id)
                await callback.answer("Вы успешно удалили свой аккаунт")

    await callback.message.delete()

    return await start(msg=callback.message, state=state, username=username, db=db, existUser=False)
