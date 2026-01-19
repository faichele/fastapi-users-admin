"""
FastAPI Router für Benutzerverwaltung.

Dieser Router stellt alle Endpunkte für die Benutzerverwaltung bereit,
einschließlich CRUD-Operationen und Admin-Interface.
"""

import logging

import uuid
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from ..models.admin_models import (
    UserAdminCreate,
    UserAdminUpdate,
    UserAdminPublic,
    UserAdminList,
    PasswordChange,
    Message
)
from ..services.user_admin_service import UserAdminService
from ..config.admin_config import AdminConfig
from fastapi_users_auth.dependencies.auth_deps import (
    AuthDependencies,
    get_current_user as get_current_user_provider,
    get_current_active_superuser as get_current_superuser_provider,
)
from packages.fastapi_users_auth.models.user_models import User

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class UserAdminRouter:
    """
    Router-Klasse für Benutzerverwaltung.

    Diese Klasse kapselt alle Routen für die Benutzerverwaltung und
    kann einfach in eine FastAPI-Anwendung integriert werden.
    """

    def __init__(
        self,
        database_session,
        auth_deps: AuthDependencies,  # Geändert: auth_deps direkt übergeben
        config: Optional[AdminConfig] = None,
        user_model=None,
        security_utils=None,
        superuser_or_redirect=None
    ):
        """
        Initialisiert den Router.

        Args:
            database_session: Dependency für Datenbank-Session
            auth_deps: AuthDependencies Instanz
            config: AdminConfig Instanz
            user_model: SQLAlchemy User Model
            security_utils: SecurityUtils Instanz
            superuser_or_redirect: Dependency für HTML-Seiten
        """
        self.database_session = database_session
        self.config = config or AdminConfig()
        self.user_model = user_model
        self.security_utils = security_utils
        self.superuser_or_redirect = superuser_or_redirect

        # Dependencies korrekt initialisieren
        self.get_current_user_dep = get_current_user_provider(auth_deps)
        self.get_current_superuser_dep = get_current_superuser_provider(auth_deps)

        # Router erstellen
        self.router = APIRouter(
            prefix=self.config.api_prefix,
            tags=self.config.router_tags
        )

        # Templates
        self.templates = Jinja2Templates(directory=self.config.templates_dir)

        # Routen registrieren
        self._register_routes()

    def _register_routes(self):
        """Registriert alle Routen."""

        # HTML Admin Page
        @self.router.get("/admin", response_class=HTMLResponse)
        async def users_admin_page(
            request: Request,
            current_user = Depends(self.superuser_or_redirect)
        ):
            """Rendert die Admin-Seite für Benutzerverwaltung."""
            if isinstance(current_user, RedirectResponse):
                return current_user

            return self.templates.TemplateResponse(
                "admin_users.html",
                {
                    "request": request,
                    "title": "Benutzerverwaltung",
                    "user": current_user
                }
            )

        # List Users
        @self.router.get("/users", response_model=UserAdminList)
        def read_users(
            skip: int = 0,
            limit: int = 100,
            session: Session = Depends(self.database_session),
            current_user: User = Depends(self.get_current_superuser_dep)
        ) -> Any:
            """Ruft eine Liste aller Benutzer ab (nur für Admins)."""
            service = UserAdminService(session, self.user_model, self.security_utils)
            users, count = service.get_users(skip=skip, limit=limit)

            return UserAdminList(
                data=[UserAdminPublic.model_validate(user) for user in users],
                count=count
            )

        # Create User
        @self.router.post("/users", response_model=UserAdminPublic)
        def create_user(
            user_in: UserAdminCreate,
            session: Session = Depends(self.database_session),
            current_user: User = Depends(self.get_current_superuser_dep)
        ) -> Any:
            """Erstellt einen neuen Benutzer (nur für Admins)."""
            service = UserAdminService(session, self.user_model, self.security_utils)

            # Check if user exists
            existing_user = service.get_user_by_email(user_in.email)
            if existing_user:
                raise HTTPException(
                    status_code=400,
                    detail="The user with this email already exists in the system."
                )

            user = service.create_user(user_in)
            return UserAdminPublic.model_validate(user)

        # Get Current User
        @self.router.get("/users/me", response_model=UserAdminPublic)
        def read_users_me(
            current_user: User = Depends(self.get_current_user_dep)
        ) -> Any:
            """Ruft Informationen über den aktuellen Benutzer ab."""
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            logger.info(f"Current user: {current_user}")
            return UserAdminPublic.model_validate(current_user)

        # Update Current User
        @self.router.patch("/users/me", response_model=UserAdminPublic)
        def update_user_me(
            user_in: UserAdminUpdate,
            session: Session = Depends(self.database_session),
            current_user: User = Depends(self.get_current_user_dep)
        ) -> Any:
            """Aktualisiert die Daten des aktuellen Benutzers."""
            service = UserAdminService(session, self.user_model, self.security_utils)

            # Check email uniqueness
            if user_in.email and user_in.email != current_user.email:
                existing_user = service.get_user_by_email(user_in.email)
                if existing_user and existing_user.uuid != current_user.uuid:
                    raise HTTPException(
                        status_code=409,
                        detail="User with this email already exists"
                    )

            # Prevent privilege escalation
            if user_in.is_superuser is not None:
                user_in.is_superuser = current_user.is_superuser

            updated_user = service.update_user(current_user.uuid, user_in)
            return UserAdminPublic.model_validate(updated_user)

        # Change Password
        @self.router.patch("/users/me/password", response_model=Message)
        def update_password_me(
            password_data: PasswordChange,
            session: Session = Depends(self.database_session),
            current_user: User = Depends(self.get_current_user_dep)
        ) -> Any:
            """Ändert das Passwort des aktuellen Benutzers."""
            service = UserAdminService(session, self.user_model, self.security_utils)

            # Hole echten DB-Benutzer, da current_user (UserPublic) kein Passwort enthält
            db_user = service.get_user_by_email(current_user.email)
            if not db_user:
                raise HTTPException(status_code=404, detail="User not found")

            # Verify current password
            if not self.security_utils.verify_password(
                password_data.current_password,
                db_user.password
            ):
                raise HTTPException(
                    status_code=400,
                    detail="Incorrect password"
                )

            # Check new password is different
            if password_data.current_password == password_data.new_password:
                raise HTTPException(
                    status_code=400,
                    detail="New password cannot be the same as the current one"
                )

            success = service.update_password(db_user.uuid, password_data.new_password)
            if not success:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to update password"
                )

            return Message(message="Password updated successfully")

        # Delete Current User
        @self.router.delete("/users/me", response_model=Message)
        def delete_user_me(
            session: Session = Depends(self.database_session),
            current_user: User = Depends(self.get_current_user_dep)
        ) -> Any:
            """Löscht den aktuellen Benutzer."""
            if current_user.is_superuser:
                raise HTTPException(
                    status_code=403,
                    detail="Super users are not allowed to delete themselves"
                )

            service = UserAdminService(session, self.user_model, self.security_utils)
            success = service.delete_user(current_user.uuid)

            if not success:
                raise HTTPException(
                    status_code=404,
                    detail="User not found"
                )

            return Message(message="User deleted successfully")

        # Get User by ID
        @self.router.get("/users/{user_id}", response_model=UserAdminPublic)
        def read_user_by_id(
            user_id: uuid.UUID,
            session: Session = Depends(self.database_session),
            current_user: User = Depends(self.get_current_user_dep)
        ) -> Any:
            """Ruft einen bestimmten Benutzer nach ID ab."""
            service = UserAdminService(session, self.user_model, self.security_utils)
            user = service.get_user_by_id(user_id)

            if not user:
                raise HTTPException(
                    status_code=404,
                    detail="The user with this id does not exist in the system"
                )

            # Allow users to see their own data or require superuser
            if user.uuid != current_user.uuid and not current_user.is_superuser:
                raise HTTPException(
                    status_code=403,
                    detail="The user doesn't have enough privileges"
                )

            return UserAdminPublic.model_validate(user)

        # Update User by ID
        @self.router.patch("/users/{user_id}", response_model=UserAdminPublic)
        def update_user(
            user_id: uuid.UUID,
            user_in: UserAdminUpdate,
            session: Session = Depends(self.database_session),
            current_user: User = Depends(self.get_current_superuser_dep)
        ) -> Any:
            """Aktualisiert einen Benutzer (nur für Admins)."""
            service = UserAdminService(session, self.user_model, self.security_utils)

            # Check if user exists
            db_user = service.get_user_by_id(user_id)
            if not db_user:
                raise HTTPException(
                    status_code=404,
                    detail="The user with this id does not exist in the system"
                )

            # Check email uniqueness
            if user_in.email:
                existing_user = service.get_user_by_email(user_in.email)
                if existing_user and existing_user.uuid != user_id:
                    raise HTTPException(
                        status_code=409,
                        detail="User with this email already exists"
                    )

            updated_user = service.update_user(user_id, user_in)
            return UserAdminPublic.model_validate(updated_user)

        # Delete User by ID
        @self.router.delete("/users/{user_id}", response_model=Message)
        def delete_user(
            user_id: uuid.UUID,
            session: Session = Depends(self.database_session),
            current_user: User = Depends(self.get_current_superuser_dep)
        ) -> Any:
            """Löscht einen Benutzer (nur für Admins)."""
            if user_id == current_user.uuid:
                raise HTTPException(
                    status_code=403,
                    detail="Super users are not allowed to delete themselves"
                )

            service = UserAdminService(session, self.user_model, self.security_utils)

            # Check if user exists
            db_user = service.get_user_by_id(user_id)
            if not db_user:
                raise HTTPException(status_code=404, detail="User not found")

            success = service.delete_user(user_id)
            if not success:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to delete user"
                )

            return Message(message="User deleted successfully")

        # User Signup (public endpoint)
        @self.router.post("/users/signup", response_model=UserAdminPublic)
        def register_user(
            user_in: UserAdminCreate,
            session: Session = Depends(self.database_session)
        ) -> Any:
            """Registriert einen neuen Benutzer (öffentlicher Endpunkt)."""
            service = UserAdminService(session, self.user_model, self.security_utils)

            # Check if user exists
            existing_user = service.get_user_by_email(user_in.email)
            if existing_user:
                raise HTTPException(
                    status_code=400,
                    detail="The user with this email already exists in the system"
                )

            # Force inactive and non-superuser for public registration
            user_in.is_active = False
            user_in.is_superuser = False

            user = service.create_user(user_in)
            return UserAdminPublic.model_validate(user)

