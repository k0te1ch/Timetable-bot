import asyncio
import os
import re

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from loguru import logger
from redis.asyncio import Redis
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_scoped_session, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base, scoped_session, sessionmaker

from handlers import adminPanel, feedbackHandler, mainHandler, registerHandler
from handlers.middlewares import GeneralMiddleware

# IMPORT SETTINGS
MAIN_MODULE_NAME = os.path.basename(__file__)[:-3]

try:
    from config import API_TOKEN, DATABASE, DATABASE_URL, PARSE_MODE, REDIS_URL

    logger.debug("Loading settings from config")
except ModuleNotFoundError:
    logger.critical("Config file not found! Please create config.py file")
    exit()
except ImportError as err:
    var = re.match(r"cannot import name '(\w+)' from", err.msg).groups()[0]
    logger.critical(f"{var} is not defined in the config file")
    exit()

# TODO сделать универсальность между async/sync sqlalchemy


# OBJECTS FOR BOT
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase


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


# GET TG BOT OBJECT
def _get_bot_obj() -> Bot:
    from config import LOCAL, TG_SERVER

    # TODO CHECK THIS
    if TG_SERVER is None and LOCAL:
        from aiogram.client.session.aiohttp import AiohttpSession
        from aiogram.client.telegram import TelegramAPIServer

        TG_SERVER = AiohttpSession(api=TelegramAPIServer.from_base("http://localhost:8081"))
        logger.opt(colors=True).info(
            f"Telegram bot configured for work with custom server <light-blue>({TG_SERVER.api.base[:TG_SERVER.api.base.find('/bot')]})</light-blue>"
        )
    elif TG_SERVER is not None:
        from aiogram.client.session.aiohttp import AiohttpSession
        from aiogram.client.telegram import TelegramAPIServer

        TG_SERVER = AiohttpSession(api=TelegramAPIServer.from_base(TG_SERVER))
        logger.opt(colors=True).info(
            f"Telegram bot configured for work with custom server <light-blue>({TG_SERVER.api.base[:TG_SERVER.api.base.find('/bot')]})</light-blue>"
        )
    else:
        logger.opt(colors=True).debug("The standard api tg server is used")
    # TODO logging
    # TODO proxy
    # TODO server
    bot = Bot(token=API_TOKEN, parse_mode=PARSE_MODE, session=TG_SERVER)
    logger.debug("Bot is configured")
    return bot


# GET REDIS OBJECT
def _get_redis_obj():
    if REDIS_URL is not None:
        redis = Redis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)
        logger.debug("Redis is configured")
    else:
        redis = _NoneModule("redis", "REDIS_URL")
        logger.debug("Redis isn't configured")

    return redis


# GET DISPATCHER OBJECT
def _get_dp_obj(bot, redis):
    logger.debug("Dispatcher configurate:")
    if not isinstance(redis, _NoneModule):
        storage = RedisStorage(redis)
        logger.debug("Used by Redis")
    else:
        storage = MemoryStorage()
        logger.debug("Used by MemoryStorage")
    dp = Dispatcher(storage=storage)
    # TODO отказ от структуры загрузки всех handlerов (?)
    dp.message.middleware(GeneralMiddleware())
    dp.callback_query.middleware(GeneralMiddleware())
    dp.include_routers(registerHandler.router, adminPanel.router, mainHandler.router, feedbackHandler.router)

    logger.debug("Dispatcher is configured")
    return dp


# GET DATABASE OBJECT
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


# GET SCHEDULER OBJECT
def _get_scheduler_obj(redis):
    job_defaults = {"misfire_grace_time": 3600}

    if not isinstance(redis, _NoneModule):
        cfg = redis.connection_pool.connection_kwargs
        jobstores = {
            "default": RedisJobStore(
                host=cfg.get("host", "localhost"),
                port=cfg.get("port", 6379),
                db=cfg.get("db", 0),
                password=cfg.get("password"),
            )
        }
    else:
        jobstores = {"default": MemoryJobStore()}

    scheduler = AsyncIOScheduler(jobstores=jobstores, job_defaults=job_defaults)

    logger.debug("Scheduler configured")
    return scheduler


if __name__ == MAIN_MODULE_NAME:
    bot = _get_bot_obj()
    redis = _get_redis_obj()
    db = _get_db_obj() if DATABASE else None
    dp = _get_dp_obj(bot, redis)
    scheduler = _get_scheduler_obj(redis)

if __name__ == "__main__":
    asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())
    from cli import cli

    logger.debug("Calling the cli module")

    cli()
