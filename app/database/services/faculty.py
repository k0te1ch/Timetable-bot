import re

from database.models.models import Course
from loguru import logger
from sqlalchemy import and_, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Direction, Faculty, Group, Profile

# TODO: Аннотации


async def create_faculty(
    session: AsyncSession, name: str, timetable_url: str, has_rating_system_access: bool = False
) -> Faculty | None:
    """
    Creates `Faculty` object

    :param session: An `AsyncSession` object
    :param name: Name of the faculty
    :param timetable_url: URL of the faculty timetable
    :param has_rating_system_access: Indicates if the faculty has access to the rating system (default is False)
    :return: Created `Faculty`
    """

    existing_faculty = await session.execute(select(Faculty).where(Faculty.name == name))
    if existing_faculty.scalars().first() is not None:
        return None

    faculty = Faculty(name=name, has_rating_system_access=has_rating_system_access, timetable_url=timetable_url)

    session.add(faculty)
    await session.flush()
    await session.refresh(faculty)
    await session.commit()

    return faculty


async def get_faculty_by_id(session: AsyncSession, id: int) -> Faculty:

    stmt = select(Faculty).where(Faculty.id == id)

    result = await session.execute(stmt)
    return result.scalars().first()


async def create_group_direction_profile_course(
    session: AsyncSession,
    group_name: str,
    year_of_study: int,
    profile_name: str,
    direction_name: str,
    faculty_id: int,
    course_name: str,
):
    try:
        created = False
        faculty = (await session.execute(select(Faculty).filter_by(id=faculty_id))).scalars().one_or_none()
        if not faculty:
            return None

        course = (
            (await session.execute(select(Course).filter_by(name=course_name, faculty_id=faculty_id)))
            .scalars()
            .one_or_none()
        )
        if not course:
            created = True
            course = Course(name=course_name, faculty=faculty)
            session.add(course)

        direction = (
            (await session.execute(select(Direction).filter_by(name=direction_name, course_id=course.id)))
            .scalars()
            .one_or_none()
        )
        if not direction:
            created = True
            direction = Direction(name=direction_name, course=course)
            session.add(direction)

        profile = (
            (await session.execute(select(Profile).filter_by(name=profile_name, direction_id=direction.id)))
            .scalars()
            .one_or_none()
        )
        if not profile:
            created = True
            profile = Profile(name=profile_name, direction=direction)
            session.add(profile)

        # Создаем группу (Group)
        group = (
            (await session.execute(select(Group).filter_by(name=group_name, profile_id=profile.id)))
            .scalars()
            .one_or_none()
        )
        if not group:

            new_group_name = re.sub(r"(\d+)", lambda x: f"{x.group()}.2", group_name)
            updated_group_name = re.sub(r"(\d+)", lambda x: f"{x.group()}.1", group_name)

            stmt1 = select(Group).where(and_(Group.profile_id == profile.id, Group.name == new_group_name))
            stmt2 = select(Group).where(and_(Group.profile_id == profile.id, Group.name == updated_group_name))

            res1 = (await session.execute(stmt1)).scalars().first()
            res2 = (await session.execute(stmt2)).scalars().first()

            if res1 is None or res2 is None:
                created = True
                group = Group(name=group_name, year_of_study=year_of_study, profile=profile)
                session.add(group)

        # Фиксируем изменения
        if created:
            await session.commit()

        return group

    except SQLAlchemyError as e:
        await session.rollback()
        logger.error(f"An error occurred: {e}")
        return None


async def get_faculties(session: AsyncSession) -> list[Faculty] | None:
    try:
        stmt = select(Faculty)

        return (await session.execute(stmt)).scalars().all()
    except SQLAlchemyError as e:
        await session.rollback()
        logger.error(f"An error occurred: {e}")
        return None
