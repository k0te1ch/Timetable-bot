# TODO ПЕРЕДЕЛАТЬ ВСЁ ТУТ
import asyncio
import importlib
import os
from datetime import datetime

import click
from alembic import command as alembic
from alembic.command import revision as alembic_revision
from alembic.config import Config
from alembic.util.exc import CommandError
from loguru import logger

import bot
from config import DATABASE_URL, ENABLE_APSCHEDULER, MODELS_DIR, SKIP_UPDATES


@logger.catch
def get_alembic_conf(sync: bool = False):
    alembic_cfg = Config()
    alembic_cfg.set_main_option("script_location", "migrations")
    alembic_cfg.set_main_option("sqlalchemy.url", DATABASE_URL)
    alembic_cfg.config_file_name = os.path.join("migrations", "alembic.ini")
    if os.path.isdir("migrations") is False:
        logger.opt(colors=True).info("<light-blue>Initiating alembic...</light-blue>")
        alembic.init(alembic_cfg, "migrations", "generic" if sync else "async")
        with open("migrations/env.py", "r+") as f:
            content = f.read()
            content = content.replace(
                "target_metadata = None", f"from {bot.MAIN_MODULE_NAME} import db\ntarget_metadata = db.metadata"
            )
            f.seek(0)
            f.write(content)
            f.truncate()

    logger.debug("Alembic is configured")
    return alembic_cfg


@logger.catch
def set_bot_properties():
    loop = bot.executor.asyncio.get_event_loop()
    _ = loop.run_until_complete(bot.bot.get_me())
    for prop, val in _:
        setattr(bot.bot, prop, val)


# CLI COMMANDS
class CliGroup(click.Group):
    def list_commands(self, ctx):
        return ["showmigrations", "makemigrations", "migrate", "run"]


@click.group(cls=CliGroup)
@click.pass_context
def cli(ctx):
    pass


@logger.catch
async def _run():
    logger.info("Connecting to Telegram...")

    me = await bot.bot.get_me()
    logger.opt(colors=True).info(f"Bot running as <light-blue>@{me.username}</light-blue>")

    if ENABLE_APSCHEDULER is True:
        bot.scheduler.start()
        # TODO добавить в scheduler задачу проверку на обновления расписания
        logger.success("Scheduler started!")

    # Добавляем команды в бота
    from aiogram.types import BotCommand, BotCommandScopeAllPrivateChats

    # TODO BotCommand или в env, или формировать при помощи handlers
    await bot.bot.set_my_commands(
        commands=[  # TODO в отдельный файл
            BotCommand(command="start", description="Команда для регистрация в боте"),
            BotCommand(command="menu", description="Команда для вызова меню"),
        ],
        scope=BotCommandScopeAllPrivateChats(),
    )

    logger.success("Bot polling started!")
    await bot.dp.start_polling(bot.bot, skip_updates=SKIP_UPDATES)


@cli.command()
@logger.catch
def run():
    asyncio.run(_run())


@logger.catch
@cli.command()
@click.option("--verbose", default=False, is_flag=True)
def showmigrations(verbose):
    cfg = get_alembic_conf()
    history = alembic.history(cfg, verbose=verbose)
    logger.info(history)


def load_models():
    models = [m[:-3] for m in os.listdir(MODELS_DIR) if m.endswith(".py")]
    logger.opt(colors=True).info(f"Loading <y>{len(models)}</y> models")
    for model in models:
        try:
            importlib.import_module(f"{MODELS_DIR}.{model}")
            logger.opt(colors=True).info(f"Loading <y>{model}</y>...   <light-green>loaded</light-green>")
        except ImportError:
            logger.opt(colors=True).exception(f"Loading <y>{model}</y>...   <light-red>error</light-red>")


@cli.command()
@click.option("-m", "--message", default=None)
@click.option("-s", "--sync", default=True)
def makemigrations(message, sync):
    if message is None:
        message = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")

    load_models()

    try:
        cfg = get_alembic_conf(sync)
        alembic_revision(
            config=cfg,
            message=message,
            autogenerate=True,
            sql=False,
            head="head",
            splice=False,
            branch_label=None,
            version_path=None,
            rev_id=None,
        )
        print("Alembic revision")
    except CommandError as err:
        print("Alembic Command Error")
        if str(err) == "Target database is not up to date.":
            print('Run "python bot.py migrate"')


@logger.catch
@cli.command()
@click.option("-r", "--revision", default="head")
@click.option("--upgrade/--downgrade", default=True, help="Default is upgrade")
@click.option("-s", "--sync", default=True)
def migrate(revision, upgrade, sync):
    cfg = get_alembic_conf(sync)
    if upgrade is True:
        alembic.upgrade(cfg, revision)
        logger.debug("Alembic upgrade")
    else:
        alembic.downgrade(cfg, "-1" if revision == "head" else revision)
        logger.debug("Alembic downgrade")
