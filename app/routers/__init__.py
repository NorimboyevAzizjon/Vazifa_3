from app.routers.auth import router as auth_router
from app.routers.settings import router as settings_router
from app.routers.debts import router as debts_router
from app.routers.monitoring import router as monitoring_router

__all__ = ["auth_router", "settings_router", "debts_router", "monitoring_router"]
