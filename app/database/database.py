import asyncio

from config import DATABASE_URL
from loguru import logger
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    AsyncSession,
    async_scoped_session,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, declarative_base, scoped_session, sessionmaker

# TODO сделать универсальность между async/sync sqlalchemy


class Base(AsyncAttrs, DeclarativeBase):
    pass


class _SQLAlchemy:
    def __init__(self, db_url):
        self.engine = create_engine(db_url)
        self.Model = declarative_base()

        self.sessionmaker = sessionmaker(bind=self.engine)
        self.session = scoped_session(self.sessionmaker)

        self.Model.query = self.session.query_property()

    @property
    def metadata(self):
        return self.Model.metadata


class _AsyncSQLAlchemy:
    def __init__(self, db_url):
        self.engine = create_async_engine(db_url)
        self.Model = Base

        self.AsyncSession = async_sessionmaker(bind=self.engine, class_=AsyncSession, expire_on_commit=False)
        self.session: async_scoped_session[AsyncSession] = async_scoped_session(
            self.AsyncSession, scopefunc=self._scopefunc
        )

    @property
    def metadata(self):
        return self.Model.metadata

    def _scopefunc(self):
        return asyncio.current_task()


class _NotDefinedModule(Exception):
    pass


class _NoneModule:
    def __init__(self, module_name, attr_name):
        self.module_name = module_name
        self.attr_name = attr_name

    def __getattr__(self, attr):
        msg = f"You are using {self.module_name} while the {self.attr_name} is not set in config"
        logger.critical(msg)
        raise _NotDefinedModule(msg)


def _get_db_obj():
    if "async" in DATABASE_URL:
        db = _AsyncSQLAlchemy(DATABASE_URL)
        logger.debug("Datebase loaded (Async)")
    elif DATABASE_URL is not None:
        db = _SQLAlchemy(DATABASE_URL)
        logger.debug("Datebase loaded (Sync)")
    else:
        db = _NoneModule("db", "DATABASE_URL")
        logger.debug("Datebase not loaded")

    return db


db: _AsyncSQLAlchemy | _SQLAlchemy | _NoneModule = _get_db_obj()
