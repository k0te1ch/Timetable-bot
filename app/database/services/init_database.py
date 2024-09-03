from config import CS_URL

from ..database import db
from .faculty import create_faculty
from .role import create_role


async def init_database():
    async with db.session() as session:
        async with session.begin():
            await create_faculty(
                session=session,
                name="Компьютерных наук",
                timetable_url=CS_URL,
                has_rating_system_access=True,
            )
        async with session.begin():
            await create_role(session=session, name="Бакалавр")
            # TODO: Автоматизировать
            # names = ["Географии, геоэкологии и туризма", "Геологический", "Журналистики",
            #        "Исторический", "Математический", "Медико-биологический",
            #        "Международных отношений", "Прикладной математики, информатики и механики",
            #        "Романо-германской филологии", "Фармацевтический", "Физический",
            #        "Филологический", "Философии и психологии", "Химический",
            #        "Экономический", "Юридический"]
            # for name in names:
            #    await create_faculty(session=session, name=name)
