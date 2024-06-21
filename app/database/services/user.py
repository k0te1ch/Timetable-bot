from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.user import User

# from .exceptions import UserNotFound, UserAlreadyExists


async def is_registered(session: AsyncSession, id: int) -> bool:
    return (await get_user_by_id(session, id)) is not None


async def get_user_by_id(
    session: AsyncSession,
    id: int,
) -> User | None:
    """
    Returns user by tg-id

    :param session: An `AsyncSession` object
    :param telegram_id: A telegram ID
    :return: `User` or `None`
    """

    stmt = select(User).where(User.id == id)

    result = await session.execute(stmt)

    return result.scalars().first()


async def create_user(session: AsyncSession, user_id: int, course: str, direction: str, profile: str, group: str):
    """
    Creates `User` object
    :param session: An `AsyncSession` object
    :param telegram_id: A telegram-id
    :param full_name: Fullname of user
    :param token: A token of user
    :return: Created `User`
    """

    existed_user = await is_registered(session, user_id)

    if existed_user:
        return False

    obj = User(
        id=user_id,
        course=course,
        direction=direction,
        profile=profile,
        group=group,
        send_notifications=True,
    )
    session.add(obj)
    await session.flush()
    await session.refresh(obj)

    return True


async def delete_user(session: AsyncSession, user_id: int) -> bool:
    """
    Deletes `User` object

    :param user_id: User ID
    :param session: An `AsyncSession` object
    :return:
    """

    if not (await is_registered(session, user_id)):
        return False

    stmt = delete(User).where(User.id == user_id)

    await session.execute(stmt)
    return True


async def get_users_for_notify(session: AsyncSession) -> list[User]:
    """
    Get `User` objects for notification
    :param session: An `AsyncSession` object
    :return: `List[User]`
    """

    stmt = select(User).where(User.send_notifications)

    result = await session.execute(stmt)
    return result.scalars().all()


async def switch_notify_for_user(session: AsyncSession, user_id: int) -> bool:
    """
    Function to toggle the boolean notify parameter for `User`.

    :param session: An `AsyncSession` object
    :param user_id: User ID
    :return: `bool` indicating whether the user was found and the notify parameter was successfully toggled
    """

    stmt = (
        update(User)
        .where(User.id == user_id)
        .values(send_notifications=(~User.send_notifications))
        .execution_options(synchronize_session="fetch")
    )
    result = await session.execute(stmt)

    if result.rowcount == 0:
        return False

    await session.commit()

    return True
