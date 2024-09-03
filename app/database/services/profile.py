from loguru import logger
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Profile


async def get_profiles(session: AsyncSession) -> list[Profile] | None:
    try:
        stmt = select(Profile)

        return (await session.execute(stmt)).scalars().all()
    except SQLAlchemyError as e:
        await session.rollback()
        logger.error(f"An error occurred: {e}")
        return None


async def get_profiles_by_direction_id(session: AsyncSession, direction_id: int) -> list[Profile] | None:
    try:
        stmt = select(Profile).where(Profile.direction_id == direction_id)

        return (await session.execute(stmt)).scalars().all()
    except SQLAlchemyError as e:
        await session.rollback()
        logger.error(f"An error occurred: {e}")
        return None
