# TODO ПЕРЕДЕЛАТЬ ВСЁ ТУТ
import json
from pytz import timezone
import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

env_path = Path('.')/'.env'
load_dotenv(dotenv_path=env_path)

def getEnvBool(env_name: str) -> Optional[bool]:
    env_val = os.getenv(env_name)
    if type(env_val) != str or not env_val.lower() in ["true", "false", "1", "0"]:
        return None
    
    if env_val in ["1", "0"]:
        return bool(int(env_val))

    return env_val.lower() == "true"

# BOT SETTINGS
CS_URL = os.getenv("CS_URL")
TIMEZONE = timezone(os.getenv("TIMEZONE"))

# TELEGRAM BOT SETTINGS
API_TOKEN = os.getenv("TELEGRAM_API_TOKEN")
SKIP_UPDATES = getEnvBool(os.getenv("SKIP_UPDATES"))

# FTP SETTINGS
FTP_SERVER = os.getenv("FTP_SERVER")
FTP_LOGIN = os.getenv("FTP_LOGIN")
FTP_PASSWORD = os.getenv("FTP_PASSWORD")

# LOGGER SETTINGS
LOG_LEVEL = os.getenv("LOG_LEVEL")

# default tg_server is official api server
TG_SERVER = os.getenv("TG_SERVER")
LOCAL = getEnvBool("LOCAL")

# default parse_mode is None
PARSE_MODE = os.getenv("PARSE_MODE")

PROXY = os.getenv("PROXY")

PROXY_AUTH = os.getenv("PROXY_AUTH")

DATABASE = getEnvBool("DATABASE")

DATABASE_URL = os.getenv("DATABASE_URL")

REDIS_URL = os.getenv("REDIS_URL")

KEYBOARDS_DIR = os.getenv("KEYBOARDS_DIR")
HANDLERS_DIR = os.getenv("HANDLERS_DIR")
MODELS_DIR = os.getenv("MODELS_DIR")
CONTEXT_FILE = os.getenv("CONTEXT_FILE")

ENABLE_APSCHEDULER = os.getenv("ENABLE_APSCHEDULER")

ADMINS = json.loads(os.getenv('ADMINS'))

HANDLERS = json.loads(os.getenv("HANDLERS"))

KEYBOARDS = json.loads(os.getenv("KEYBOARDS"))

LANGUAGES = json.loads(os.getenv("LANGUAGES"))


# SOURCES
SRC_PATH = Path(__file__).parent
TIMETABLE_FILENAME = os.getenv("TIMETABLE_FILENAME")

FILES_PATH = SRC_PATH / os.getenv("FILES_PATH")
TIMETABLE_PATH = FILES_PATH / TIMETABLE_FILENAME
