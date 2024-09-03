from loguru import logger
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Role

# TODO: Аннотации


async def create_role(session: AsyncSession, name: str) -> Role | None:
    """
    Creates `Role` object

    :param session: An `AsyncSession` object
    :param name: Name of the role
    :return: Created `Role`
    """
    try:
        role = await session.execute(select(Role).where(Role.name == name))
        if role.scalars().first() is not None:
            return None

        role = Role(name=name)

        session.add(role)
        await session.flush()
        await session.refresh(role)
        await session.commit()

        return role
    except SQLAlchemyError as e:
        await session.rollback()
        logger.error(f"An error occurred: {e}")
        return None


async def get_role_by_name(session: AsyncSession, name) -> Role:
    try:
        stmt = select(Role).where(Role.name == name)

        result = await session.execute(stmt)

        return result.scalars().first()
    except SQLAlchemyError as e:
        await session.rollback()
        logger.error(f"An error occurred: {e}")
        return None
