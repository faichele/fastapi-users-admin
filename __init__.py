"""
Wiederverwendbares Benutzerverwaltungsmodul für FastAPI-Anwendungen.

Dieses Modul bietet eine vollständige Lösung für:
- Benutzerverwaltung (CRUD-Operationen)
- Passwort-Reset und -Änderung
- Benutzerprofilverwaltung
- Admin-Interface für Benutzerverwaltung
- HTML-Templates für Admin-Bereich

Usage:
    from fastapi_users_admin import UserAdminModule

    # In FastAPI-App einbinden
    admin_module = UserAdminModule(app, database_session, settings)
"""

from .models.admin_models import (
    UserAdminCreate,
    UserAdminUpdate,
    UserAdminPublic,
    UserAdminList,
    PasswordResetRequest,
    PasswordResetConfirm
)

from .services.user_admin_service import UserAdminService
from .routers.user_admin_router import UserAdminRouter
from .config.admin_config import AdminConfig

__version__ = "0.0.2"

__all__ = [
    # Models
    "UserAdminCreate",
    "UserAdminUpdate",
    "UserAdminPublic",
    "UserAdminList",
    "PasswordResetRequest",
    "PasswordResetConfirm",

    # Services
    "UserAdminService",

    # Routers
    "UserAdminRouter",

    # Config
    "AdminConfig",
]


class UserAdminModule:
    """
    Hauptklasse zum Einbinden des Benutzerverwaltungsmoduls in eine FastAPI-Anwendung.

    Diese Klasse bietet eine einfache Schnittstelle zur Integration des kompletten
    Benutzerverwaltungssystems in bestehende FastAPI-Anwendungen.
    """

    def __init__(self, app=None, database_session=None, config=None):
        self.app = app
        self.database_session = database_session
        self.config = config or AdminConfig()

        if app:
            self.init_app(app)

    def init_app(self, app):
        """Initialisiert das Modul mit einer FastAPI-App."""
        from fastapi import FastAPI

        if not isinstance(app, FastAPI):
            raise TypeError("app must be a FastAPI instance")

        # Router hinzufügen
        admin_router = UserAdminRouter(
            database_session=self.database_session,
            config=self.config
        )

        app.include_router(admin_router.router)

