"""
SQLAlchemy-basierter Service für Benutzerverwaltung.

Diese Implementierung nutzt SQLAlchemy für Datenbankoperationen.
"""

import uuid
from typing import Optional, List, Any
from sqlalchemy.orm import Session

from ..services.base_user_admin_service import BaseUserAdminService


class UserAdminService(BaseUserAdminService):
    """
    SQLAlchemy-Implementierung des Benutzerverwaltungs-Service.
    """

    def __init__(self, session: Session, user_model, security_utils):
        """
        Initialisiert den Service.

        Args:
            session: SQLAlchemy Session
            user_model: SQLAlchemy User Model Klasse
            security_utils: Utility-Objekt für Passwort-Hashing
        """
        self.session = session
        self.user_model = user_model
        self.security_utils = security_utils

    def get_user_by_id(self, user_id: uuid.UUID) -> Optional[Any]:
        """Ruft einen Benutzer anhand seiner ID ab."""
        return self.session.query(self.user_model).filter(
            self.user_model.id == user_id
        ).first()

    def get_user_by_email(self, email: str) -> Optional[Any]:
        """Ruft einen Benutzer anhand seiner E-Mail-Adresse ab."""
        return self.session.query(self.user_model).filter(
            self.user_model.email == email
        ).first()

    def get_users(self, skip: int = 0, limit: int = 100) -> tuple[List[Any], int]:
        """
        Ruft eine Liste von Benutzern ab.

        Returns:
            Tuple mit (Liste der Benutzer, Gesamtanzahl)
        """
        count = self.session.query(self.user_model).count()
        users = self.session.query(self.user_model).offset(skip).limit(limit).all()
        return users, count

    def create_user(self, user_data: Any) -> Any:
        """Erstellt einen neuen Benutzer."""
        # Hash password
        hashed_password = self.security_utils.get_password_hash(user_data.password)

        # Create user instance
        user = self.user_model(
            id=uuid.uuid4(),
            email=user_data.email,
            full_name=user_data.full_name,
            is_active=user_data.is_active,
            is_superuser=user_data.is_superuser,
            hashed_password=hashed_password,
        )

        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)

        return user

    def update_user(self, user_id: uuid.UUID, user_data: Any) -> Optional[Any]:
        """Aktualisiert einen bestehenden Benutzer."""
        user = self.get_user_by_id(user_id)
        if not user:
            return None

        # Update fields
        if user_data.email is not None:
            user.email = user_data.email
        if user_data.full_name is not None:
            user.full_name = user_data.full_name
        if user_data.is_active is not None:
            user.is_active = user_data.is_active
        if user_data.is_superuser is not None:
            user.is_superuser = user_data.is_superuser
        if user_data.password is not None:
            user.hashed_password = self.security_utils.get_password_hash(user_data.password)

        self.session.commit()
        self.session.refresh(user)

        return user

    def delete_user(self, user_id: uuid.UUID) -> bool:
        """Löscht einen Benutzer."""
        user = self.get_user_by_id(user_id)
        if not user:
            return False

        self.session.delete(user)
        self.session.commit()
        return True

    def update_password(self, user_id: uuid.UUID, new_password: str) -> bool:
        """Aktualisiert das Passwort eines Benutzers."""
        user = self.get_user_by_id(user_id)
        if not user:
            return False

        user.hashed_password = self.security_utils.get_password_hash(new_password)
        self.session.commit()

        return True

    def activate_user(self, user_id: uuid.UUID) -> Optional[Any]:
        """Aktiviert einen Benutzer."""
        user = self.get_user_by_id(user_id)
        if not user:
            return None

        user.is_active = True
        self.session.commit()
        self.session.refresh(user)

        return user

    def deactivate_user(self, user_id: uuid.UUID) -> Optional[Any]:
        """Deaktiviert einen Benutzer."""
        user = self.get_user_by_id(user_id)
        if not user:
            return None

        user.is_active = False
        self.session.commit()
        self.session.refresh(user)

        return user
