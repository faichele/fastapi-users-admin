"""
FastAPI Dependencies für Benutzerverwaltung.
"""

from typing import Annotated
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session


class AdminDependencies:
    """
    Dependency-Provider für Benutzerverwaltung.

    Diese Klasse stellt FastAPI Dependencies bereit, die in Routern
    verwendet werden können.
    """

    def __init__(self, get_db, get_current_user, user_model, security_utils):
        """
        Initialisiert die Dependencies.

        Args:
            get_db: Funktion zum Abrufen einer Datenbank-Session
            get_current_user: Funktion zum Abrufen des aktuellen Benutzers
            user_model: SQLAlchemy User Model
            security_utils: SecurityUtils Instanz
        """
        self.get_db = get_db
        self.get_current_user = get_current_user
        self.user_model = user_model
        self.security_utils = security_utils

    def get_current_active_user(self, session: Session = Depends(lambda: None),
                                 current_user = Depends(lambda: None)):
        """
        Dependency zum Abrufen des aktuellen aktiven Benutzers.

        Raises:
            HTTPException: Wenn der Benutzer nicht aktiv ist
        """
        if not current_user:
            # Use the injected get_current_user function
            current_user = self.get_current_user(session)

        if not current_user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Inactive user"
            )
        return current_user

    def get_current_superuser(self, current_user = Depends(lambda: None)):
        """
        Dependency zum Abrufen des aktuellen Superusers.

        Raises:
            HTTPException: Wenn der Benutzer kein Superuser ist
        """
        if not current_user:
            current_user = self.get_current_active_user()

        if not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="The user doesn't have enough privileges"
            )
        return current_user

    def superuser_or_redirect(self, request, session: Session = Depends(lambda: None)):
        """
        Dependency für HTML-Seiten: Prüft Superuser-Status oder leitet um.

        Diese Dependency ist für HTML-Seiten gedacht und gibt entweder
        den Benutzer zurück oder eine RedirectResponse.
        """
        from fastapi.responses import RedirectResponse
        from starlette.status import HTTP_302_FOUND

        try:
            # Try to get token from cookies or headers
            token = request.cookies.get("access_token") or request.headers.get("Authorization")
            if not token:
                return RedirectResponse(
                    url=f"/api/login?next={request.url.path}",
                    status_code=HTTP_302_FOUND
                )

            # Clean token
            token = token.replace("Bearer ", "") if token.startswith("Bearer ") else token

            # Get current user
            current_user = self.get_current_user(session=session, token=token)
            if not current_user:
                return RedirectResponse(
                    url=f"/api/login?next={request.url.path}",
                    status_code=HTTP_302_FOUND
                )

            # Check if superuser
            if not current_user.is_superuser:
                return RedirectResponse(
                    url="/api//login?message=Access%20denied",
                    status_code=HTTP_302_FOUND
                )

            return current_user
        except Exception:
            return RedirectResponse(
                url=f"/api/login?next={request.url.path}",
                status_code=HTTP_302_FOUND
            )

