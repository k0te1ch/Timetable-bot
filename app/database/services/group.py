import re

from loguru import logger
from sqlalchemy import and_, select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from ..models import Course, Direction, Faculty, Group, Profile


async def get_groups(session: AsyncSession) -> list[Group] | None:
    try:
        stmt = select(Group)

        result = await session.execute(stmt)

        return result.scalars().all()
    except SQLAlchemyError as e:
        await session.rollback()
        logger.error(f"An error occurred: {e}")
        return None


async def get_specific_group(
    session: AsyncSession, faculty: str, direction: str, profile: str, group: str, course: str
) -> Group:
    try:
        stmt = (
            select(Group)
            .join(Group.profile)
            .join(Profile.direction)
            .join(Direction.course)
            .join(Course.faculty)
            .filter(
                Faculty.name == faculty,
                Course.name == course,
                Direction.name == direction,
                Profile.name == profile,
                Group.name == group,
            )
        )

        result = await session.execute(stmt)

        return result.scalars().first()
    except SQLAlchemyError as e:
        await session.rollback()
        logger.error(f"An error occurred: {e}")
        return None


async def bifurcation_group(
    session: AsyncSession, group_id: int, group_name: str, profile_id: str, year_of_study
) -> None:
    try:
        new_group_name = re.sub(r"(\d+)", lambda x: f"{x.group()}.2", group_name)
        updated_group_name = re.sub(r"(\d+)", lambda x: f"{x.group()}.1", group_name)

        profile = (await session.execute(select(Profile).where(Profile.id == profile_id))).scalars().first()

        stmt1 = select(Group).where(and_(Group.profile_id == profile.id, Group.name == new_group_name))
        stmt2 = select(Group).where(and_(Group.profile_id == profile.id, Group.name == updated_group_name))

        res1 = (await session.execute(stmt1)).scalars().first()
        res2 = (await session.execute(stmt2)).scalars().first()

        if res1 is not None and res2 is not None:
            return

        new_group = Group(name=new_group_name, profile=profile, year_of_study=year_of_study)

        session.add(new_group)

        stmt = update(Group).where(Group.id == group_id).values(name=updated_group_name)
        await session.execute(stmt)

        await session.commit()

    except SQLAlchemyError as e:
        await session.rollback()
        logger.error(f"An error occurred: {e}")


async def get_groups_by_profile_id(session: AsyncSession, profile_id: int) -> list[Group] | None:
    try:
        stmt = select(Group).where(Group.profile_id == profile_id)

        return (await session.execute(stmt)).scalars().all()
    except SQLAlchemyError as e:
        await session.rollback()
        logger.error(f"An error occurred: {e}")
        return None


async def get_group_by_id(session: AsyncSession, id: int) -> Group | None:
    try:

        stmt = (
            select(Group)
            .options(joinedload(Group.profile).joinedload(Profile.direction).joinedload(Direction.course))
            .where(Group.id == id)
        )

        return (await session.execute(stmt)).scalars().first()
    except SQLAlchemyError as e:
        await session.rollback()
        logger.error(f"An error occurred: {e}")
        return None
