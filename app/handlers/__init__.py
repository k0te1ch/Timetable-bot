from aiogram.types import BotCommand

from .admin_handler import router as admin_handler_router
<<<<<<< HEAD
<<<<<<< HEAD
from .feedback_handler import router as feedbackHandler_router
=======
from .feedback_handler import router as feedback_handler_router
>>>>>>> 14c1f28 (Fixed all errors)
=======
from .feedback_handler import router as feedback_handler_router
>>>>>>> b84f6c69106e06e40db34ece7337719f8e2716cf
from .free_audiences_handler import router as free_audiences_handler_router
from .main_handler import router as mainHandler_router
from .register_handler import router as registerHandler_router
from .schedule_handler import router as schedule_handler_router
from .settings_hanlder import router as settings_handler_router
from .user_handler import router as user_handler_router

ROUTERS = [
    admin_handler_router,
<<<<<<< HEAD
<<<<<<< HEAD
    feedbackHandler_router,
=======
    feedback_handler_router,
>>>>>>> 14c1f28 (Fixed all errors)
=======
    feedback_handler_router,
>>>>>>> b84f6c69106e06e40db34ece7337719f8e2716cf
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
