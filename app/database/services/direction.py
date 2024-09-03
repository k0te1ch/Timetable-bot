from loguru import logger
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Direction


async def get_directions(session: AsyncSession) -> list[Direction] | None:
    try:
        stmt = select(Direction)

        return (await session.execute(stmt)).scalars().all()
    except SQLAlchemyError as e:
        await session.rollback()
        logger.error(f"An error occurred: {e}")
        return None


async def get_directions_by_course_id(session: AsyncSession, course_id: int) -> list[Direction] | None:
    try:
        stmt = select(Direction).where(Direction.course_id == course_id)

        return (await session.execute(stmt)).scalars().all()
    except SQLAlchemyError as e:
        await session.rollback()
        logger.error(f"An error occurred: {e}")
        return None
