# TODO ПЕРЕДЕЛАТЬ ВСЁ ТУТ
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from loguru import logger
from pytz import timezone


# TODO добавить загрузку .env из аргументов запуска
def loadEnv():
    env_file = os.getenv("ENVFILE", ".env")
    if env_file.endswith(".env"):
        env_path = Path(".") / env_file
        load_dotenv(dotenv_path=env_path, override=True)


def getEnvBool(env_name: str) -> bool | None:
    env_val = os.getenv(env_name)
    if env_val is None or not isinstance(env_val, str) or not env_val.lower() in ["true", "false", "1", "0"]:
        return None

    env_val_lower = env_val.lower()
    if env_val_lower in ["1", "0"]:
        return bool(int(env_val_lower))

    return env_val_lower.lower() == "true"


def getStrOrNone(env_name: str) -> str | None:
    env_val = os.getenv(env_name)
    if env_val is None or isinstance(env_val, str) and env_val.lower() == "none":
        return None
    return env_val


loadEnv()

# BOT SETTINGS
CS_URL = getStrOrNone("CS_URL")
TIMEZONE = timezone(getStrOrNone("TIMEZONE"))

# TELEGRAM BOT SETTINGS
API_TOKEN = os.getenv("TELEGRAM_API_TOKEN")
SKIP_UPDATES = getEnvBool(os.getenv("SKIP_UPDATES"))
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")

# FTP SETTINGS
FTP_SERVER = getStrOrNone("FTP_SERVER")
FTP_LOGIN = getStrOrNone("FTP_LOGIN")
FTP_PASSWORD = getStrOrNone("FTP_PASSWORD")

# LOGGER SETTINGS
LOG_LEVEL = getStrOrNone("LOG_LEVEL")

# default tg_server is official api server
TG_SERVER = getStrOrNone("TG_SERVER")
LOCAL = getEnvBool("LOCAL")

# default parse_mode is None
PARSE_MODE = getStrOrNone("PARSE_MODE")

PROXY = getStrOrNone("PROXY")

PROXY_AUTH = getStrOrNone("PROXY_AUTH")

DATABASE = getEnvBool("DATABASE")

DATABASE_URL = getStrOrNone("DATABASE_URL")

REDIS_URL = getStrOrNone("REDIS_URL")

KEYBOARDS_DIR = getStrOrNone("KEYBOARDS_DIR")
HANDLERS_DIR = getStrOrNone("HANDLERS_DIR")
MODELS_DIR = getStrOrNone("MODELS_DIR")
CONTEXT_FILE = getStrOrNone("CONTEXT_FILE")

ENABLE_APSCHEDULER = getStrOrNone("ENABLE_APSCHEDULER")

ADMINS = json.loads(getStrOrNone("ADMINS"))

HANDLERS = json.loads(getStrOrNone("HANDLERS"))

KEYBOARDS = json.loads(getStrOrNone("KEYBOARDS"))

LANGUAGES = json.loads(getStrOrNone("LANGUAGES"))


# SOURCES
SRC_PATH = Path(__file__).parent
TIMETABLE_FILENAME = getStrOrNone("TIMETABLE_FILENAME")

FILES_PATH = SRC_PATH / getStrOrNone("FILES_PATH")
TIMETABLE_PATH = FILES_PATH / TIMETABLE_FILENAME


# LOGGER
logger.remove()
logger.add(
    sys.stdout,
    colorize=True,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level>::<blue>{module}</blue>::<cyan>{function}</cyan>::<cyan>{line}</cyan> | <level>{message}</level>",
    level=LOG_LEVEL,
    backtrace=True,
    diagnose=True,
)

MODULE_PATH = os.path.dirname(os.path.realpath(__file__))
if not os.path.exists(f"{MODULE_PATH}/logs"):
    os.mkdir(f"{MODULE_PATH}/logs")
logger.add(
    MODULE_PATH + "/logs/file_{time:YYYY-MM-DD_HH-mm-ss}.log",
    rotation="5 MB",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level}::{module}::{function}::{line} | {message}",
    level="TRACE",
    backtrace=True,
    diagnose=True,
)
