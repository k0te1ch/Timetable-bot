from aiogram.types import BotCommand

from .admin_handler import router as admin_handler_router
from .feedback_handler import router as feedbackHandler_router
from .free_audiences_handler import router as free_audiences_handler_router
from .main_handler import router as mainHandler_router
from .register_handler import router as registerHandler_router
from .schedule_handler import router as schedule_handler_router
from .settings_hanlder import router as settings_handler_router
from .user_handler import router as user_handler_router

ROUTERS = [
    admin_handler_router,
    feedbackHandler_router,
    free_audiences_handler_router,
    mainHandler_router,
    registerHandler_router,
    schedule_handler_router,
    settings_handler_router,
    user_handler_router,
]

COMMANDS = [
    BotCommand(command="start", description="Команда для регистрация в боте"),
    BotCommand(command="menu", description="Команда для вызова меню"),
    BotCommand(command="feedback", description="Команда для обратной связи"),
]
