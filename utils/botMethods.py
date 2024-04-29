import zipfile
from pathlib import Path

from loguru import logger

from config import LOGS_PATH

# TODO: Необходимо реализовать выключение бота в докере и если просто запущен просто так
# TODO: Необходимо реализовать перезагрузку скрипта (вывод ошибки если запущен не в докере)
# TODO: Удаление логов, старше N времени


def shutdown_bot() -> None:
    logger.info("Shutdown bot")
    exit()


def delete_logs() -> None:
    logger.info("Delete log")
    logger.debug("Logs not deleted")


def get_logs() -> Path:
    logger.info("Get logs")
    zip_path = LOGS_PATH / "logs.zip"
    with zipfile.ZipFile(zip_path, mode="w") as archive:
        for file_name in sorted(LOGS_PATH.glob("*.log")):
            archive.write(file_name, f"logs/{file_name.name}")
    logger.info("Logs returns")
    return zip_path
