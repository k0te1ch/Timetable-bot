from .admin_panel import router as adminPanel_router
from .feedback_handler import router as feedbackHandler_router
from .free_audiences_handler import router as free_audiences_handler_router
from .main_handler import router as mainHandler_router
from .register_handler import router as registerHandler_router
from .schedule_handler import router as schedule_handler_router
from .settings_hanlder import router as settings_handler_router
from .user_handler import router as user_handler_router

ROUTERS = [
    adminPanel_router,
    feedbackHandler_router,
    free_audiences_handler_router,
    mainHandler_router,
    registerHandler_router,
    schedule_handler_router,
    settings_handler_router,
    user_handler_router,
]
