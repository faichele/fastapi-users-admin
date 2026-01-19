"""
CRUD-Service für Benutzerverwaltung.

Diese Klasse stellt vereinfachte CRUD-Operationen bereit, die von verschiedenen
Service-Implementierungen genutzt werden können.
"""

import uuid
from typing import Optional, Any
from sqlalchemy.orm import Session


class UserCRUDService:
    """
    Service für grundlegende CRUD-Operationen auf Benutzern.

    Diese Klasse kann von verschiedenen Implementierungen als Hilfsklasse
    genutzt werden.
    """

    @staticmethod
    def create_user(session: Session, user_model, user_create: Any, security_utils) -> Any:
        """Erstellt einen neuen Benutzer in der Datenbank."""
        hashed_password = security_utils.get_password_hash(user_create.password)

        user = user_model(
            uuid=uuid.uuid4(),
            email=user_create.email,
            full_name=user_create.full_name,
            is_active=getattr(user_create, 'is_active', True),
            is_superuser=getattr(user_create, 'is_superuser', False),
            password=hashed_password
        )

        session.add(user)
        session.commit()
        session.refresh(user)

        return user

    @staticmethod
    def update_user(session: Session, db_user: Any, user_in: Any, security_utils) -> Any:
        """Aktualisiert einen bestehenden Benutzer."""
        update_data = user_in.model_dump(exclude_unset=True)

        # Handle password separately
        if "password" in update_data and update_data["password"]:
            hashed_password = security_utils.get_password_hash(update_data["password"])
            del update_data["password"]
            db_user.password = hashed_password

        # Update other fields
        for field, value in update_data.items():
            if hasattr(db_user, field):
                setattr(db_user, field, value)

        session.add(db_user)
        session.commit()
        session.refresh(db_user)

        return db_user

    @staticmethod
    def get_user_by_email(session: Session, user_model, email: str) -> Optional[Any]:
        """Ruft einen Benutzer anhand seiner E-Mail-Adresse ab."""
        return session.query(user_model).filter(user_model.email == email).first()

    @staticmethod
    def get_user_by_id(session: Session, user_model, user_id: uuid.UUID) -> Optional[Any]:
        """Ruft einen Benutzer anhand seiner UUID ab."""
        return session.query(user_model).filter(user_model.uuid == user_id).first()

