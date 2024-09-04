from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from ..models import Group, Role, Settings, User
from .settings import create_settings

# TODO: Аннотации


async def is_registered(session: AsyncSession, id: int) -> bool:
    return (await get_user_by_telegram_id(session, id)) is not None


async def get_user_by_telegram_id(session: AsyncSession, telegram_id: int) -> User | None:
    """
    Returns user by telegram_id

    :param session: An `AsyncSession` object
    :param id: A telegram_id
    :return: `User` or `None`
    """

    stmt = select(User).options(joinedload(User.settings)).filter(User.telegram_id == telegram_id)

    result = await session.execute(stmt)

    result = result.scalars().first()

    if result is not None or result.settings is None:
        result.settings = await create_settings(session, result)

    return result


async def create_user(
    session: AsyncSession,
    telegram_id: str,
    vk_id: str,
    first_name: str,
    middle_name: str,
    last_name: str,
    role: Role,
    group: Group | None = None,
) -> bool:
    """
    Creates `User` object

    :param session: An `AsyncSession` object
    :param telegram_id: Telegram ID
    :param vk_id: VK ID
    :param first_name: First name of user
    :param middle_name: Middle name of user
    :param last_name: Last name of user
    :param role: `Role`
    :param group: `Group` (optional)
    :return: `bool` indicating whether the user was successfully created
    """

    existed_user = await is_registered(session, telegram_id)

    if existed_user:
        return False

    obj = User(
        telegram_id=telegram_id,
        vk_id=vk_id,
        first_name=first_name,
        middle_name=middle_name,
        last_name=last_name,
        role=role,
        group=group,
    )

    session.add(obj)
    settings = Settings(user=obj)
    session.add(settings)
    obj.settings = settings

    await session.flush()
    await session.refresh(obj)
    await session.commit()

    return True


async def delete_user_by_telegram_id(session: AsyncSession, telegram_id: int) -> bool:
    """
    Deletes `User` object

    :param telegram_id: telegram_id
    :param session: An `AsyncSession` object
    :return: `bool` indicating whether the user was successfully deleted
    """

    if not (await is_registered(session, telegram_id)):
        return False

    stmt = delete(User).where(User.telegram_id == telegram_id)

    await session.execute(stmt)
    await session.commit()
    return True


async def get_users_for_notify(session: AsyncSession) -> list[User]:
    """
    Get `User` objects for notification

    :param session: An `AsyncSession` object
    :return: `List[User]`
    """

    stmt = select(User).where(User.settings.notifications)

    result = await session.execute(stmt)
    return result.scalars().all()


async def switch_notify_for_user(session: AsyncSession, user_id: int) -> bool:
    """
    Function to toggle the boolean notify parameter for `User`.

    :param session: An `AsyncSession` object
    :param user_id: User ID
    :return: `bool` the notify parameter
    """

    user = await get_user_by_telegram_id(session, user_id)
    if user is None:
        return False

    stmt = update(Settings).where(Settings.user == user).values(notifications=not user.settings.notifications)

    await session.execute(stmt)

    await session.refresh(user)
    await session.commit()

    return user.settings.notifications
