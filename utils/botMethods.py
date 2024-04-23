import zipfile
from pathlib import Path

from config import LOGS_PATH

# TODO: Необходимо реализовать выключение бота в докере и если просто запущен просто так
# TODO: Необходимо реализовать перезагрузку скрипта (вывод ошибки если запущен не в докере)
# TODO: Удаление логов, старше N времени


def shutdown_bot() -> None:
    exit()


def delete_logs() -> None:
    pass


def get_logs() -> Path:
    zip_path = LOGS_PATH / "logs.zip"
    with zipfile.ZipFile(zip_path, mode="w") as archive:
        for file_name in sorted(LOGS_PATH.glob("*.log")):
            archive.write(file_name, f"logs/{file_name.name}")
    return zip_path
