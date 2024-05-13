import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from loguru import logger
from pytz import timezone

# TODO: Добавить загрузку .env из аргументов запуска


def loadEnv():
    env_file = os.getenv("ENVFILE", ".env")
    if env_file.endswith(".env"):
        env_path = Path.cwd() / env_file
        load_dotenv(dotenv_path=env_path, override=True)


def get_env_bool(env_name: str, default: bool = False) -> bool:
    env_val = os.getenv(env_name)
    if env_val is None or not isinstance(env_val, str) or not env_val.lower() in ["true", "false", "1", "0"]:
        return default

    env_val_lower = env_val.lower()
    if env_val_lower in ["1", "0"]:
        return bool(int(env_val_lower))

    return env_val_lower.lower() == "true"


def get_env_str(env_key: str, default: str = None, required: bool = False) -> str | None:
    env_val = os.getenv(env_key, default)
    if env_val is None or isinstance(env_val, str) and env_val.lower() == "none":
        if required:
            raise NameError(f'name "{env_key}" is not defined in your env file')
        return None
    return env_val


def set_up_logger(log_level: str, logs_path: Path):
    logger.remove()
    logger.add(
        sys.stdout,
        colorize=True,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level>::<blue>{module}</blue>::<cyan>{function}</cyan>::<cyan>{line}</cyan> | <level>{message}</level>",
        level=log_level,
        backtrace=True,
        diagnose=True,
    )

    logger.add(
        logs_path / "file_{time:YYYY-MM-DD_HH-mm-ss}.log",
        rotation="5 MB",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level}::{module}::{function}::{line} | {message}",
        level="TRACE",
        backtrace=True,
        diagnose=True,
    )


loadEnv()

# SOURCES OF PROJECT
PROJECT_PATH = Path.cwd()
SRC_PATH = Path(__file__).parent
# TODO: make method for paths
TIMETABLE_FILENAME: Path = get_env_str("TIMETABLE_FILENAME", default="timetable.xlsx", required=True)
CONTEXT_FILE: Path = get_env_str("CONTEXT_FILE", default="context")

KEYBOARDS_DIR: Path = get_env_str("KEYBOARDS_DIR", default="keyboards")
HANDLERS_DIR: Path = get_env_str("HANDLERS_DIR", default="handlers")
MODELS_DIR: Path = get_env_str("MODELS_DIR", default="models")
FILES_PATH: Path = PROJECT_PATH / get_env_str("FILES_PATH", default="files")
TIMETABLE_PATH: Path = FILES_PATH / TIMETABLE_FILENAME

# LOGGER SETTINGS
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOGS_PATH = PROJECT_PATH / "logs"
set_up_logger(LOG_LEVEL, LOGS_PATH)


# BOT SETTINGS
CS_URL = get_env_str("CS_URL", required=True)
TIMEZONE = timezone(get_env_str("TIMEZONE", default="GMT"))

# TELEGRAM BOT SETTINGS
API_TOKEN = get_env_str("TELEGRAM_API_TOKEN", required=True)
SKIP_UPDATES = get_env_bool("SKIP_UPDATES", default=True)
ADMIN_CHAT_ID = get_env_str("ADMIN_CHAT_ID", required=True)


# default tg_server is official api server
TG_SERVER = get_env_str("TG_SERVER")  # TODO: отрефакторить поддержку TG_SERVER
LOCAL = get_env_bool("LOCAL", default=False)

PARSE_MODE = get_env_str("PARSE_MODE", default="html")

DATABASE = get_env_bool("DATABASE", default=True)

DATABASE_URL = get_env_str("DATABASE_URL", required=True)

REDIS_URL = get_env_str("REDIS_URL", default="redis://redis:6379/0", required=True)

ENABLE_APSCHEDULER = get_env_bool("ENABLE_APSCHEDULER", default=True)

# TODO: Создать функцию, которая будет импортировать списки
ADMINS = json.loads(get_env_str("ADMINS"))

HANDLERS = json.loads(get_env_str("HANDLERS"))

KEYBOARDS = json.loads(get_env_str("KEYBOARDS"))

LANGUAGES = json.loads(get_env_str("LANGUAGES"))


# make dirs
for path in [FILES_PATH, LOGS_PATH]:
    if not isinstance(path, Path):
        path = Path(path)
    if not path.exists():
        try:
            path.mkdir(parents=True)
            logger.debug(f"Директория {path} успешно создана")
        except OSError as e:
            logger.error(f"Ошибка создания директории {path}: {e}")
