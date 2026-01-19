"""
Beispiel für die Integration des fastapi_users_admin Moduls in eine FastAPI-Anwendung.
"""

from fastapi import FastAPI
from sqlalchemy.orm import Session

# Import des fastapi_users_admin Moduls
from users_admin import UserAdminRouter
from users_admin.config import AdminConfig
from users_admin.utils import SecurityUtils

# Ihre existierenden Imports
from backend.database.base import get_db
from backend.database.models import User
from backend.api.deps import (
    get_current_user,
    get_current_active_superuser,
    CurrentUser,
    SessionDep
)
from backend.utils.auth import superuser_or_redirect


def setup_user_admin(app: FastAPI):
    """
    Integriert das fastapi_users_admin Modul in die FastAPI-Anwendung.
    """

    # Konfiguration erstellen
    config = AdminConfig(
        templates_dir="backend/fastapi_users_admin/templates",
        api_prefix="/api",
        router_tags=["users", "admin"],
        emails_enabled=False,  # E-Mail-Versand deaktiviert für dieses Beispiel
        enable_logging=True,
        log_file="logs/fastapi_users_admin.log"
    )

    # Security Utils initialisieren
    security_utils = SecurityUtils()

    # Router erstellen
    admin_router = UserAdminRouter(
        database_session=get_db,
        config=config,
        user_model=User,
        security_utils=security_utils,
        get_current_user=get_current_user,
        get_current_superuser=get_current_active_superuser,
        superuser_or_redirect=superuser_or_redirect
    )

    # Router in die App einbinden
    app.include_router(admin_router.router)

    return admin_router


# Verwendung in main.py
if __name__ == "__main__":
    app = FastAPI(title="My Application")

    # Benutzerverwaltung einbinden
    admin_router = setup_user_admin(app)

    # Weitere Konfiguration...

    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

