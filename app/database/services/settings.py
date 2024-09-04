from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Settings, User


async def create_settings(session: AsyncSession, user: User) -> Settings:
    """
    Creates `Settings` object

    :param session: An `AsyncSession` object
    :param user: `User`
    :return: `Settings` or `None`
    """

    settings = Settings(user=user)

    session.add(settings)
    await session.flush()
    await session.refresh(settings)

    return settings
