from loguru import logger
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Course


async def get_courses(session: AsyncSession) -> list[Course] | None:
    try:
        stmt = select(Course)

        return (await session.execute(stmt)).scalars().all()
    except SQLAlchemyError as e:
        await session.rollback()
        logger.error(f"An error occurred: {e}")
        return None


async def get_courses_by_faculty_id(session: AsyncSession, faculty_id: int) -> list[Course] | None:
    try:
        stmt = select(Course).where(Course.faculty_id == faculty_id)

        return (await session.execute(stmt)).scalars().all()
    except SQLAlchemyError as e:
        await session.rollback()
        logger.error(f"An error occurred: {e}")
        return None
