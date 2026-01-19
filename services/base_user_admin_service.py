"""
Basis-Service-Klasse für Benutzerverwaltung.

Diese abstrakte Basisklasse definiert die Schnittstelle für alle
Benutzerverwaltungs-Services und ermöglicht verschiedene Implementierungen
(z.B. SQLAlchemy, MongoDB, externe APIs).
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Any
import uuid


class BaseUserAdminService(ABC):
    """
    Abstrakte Basisklasse für Benutzerverwaltungs-Services.

    Implementierungen können verschiedene Datenquellen nutzen:
    - Datenbank (SQLAlchemy)
    - NoSQL (MongoDB, Redis)
    - Externe APIs (LDAP, Active Directory)
    - Identity Provider (Keycloak, Auth0)
    """

    @abstractmethod
    def get_user_by_id(self, user_id: uuid.UUID) -> Optional[Any]:
        """Ruft einen Benutzer anhand seiner ID ab."""
        pass

    @abstractmethod
    def get_user_by_email(self, email: str) -> Optional[Any]:
        """Ruft einen Benutzer anhand seiner E-Mail-Adresse ab."""
        pass

    @abstractmethod
    def get_users(self, skip: int = 0, limit: int = 100) -> tuple[List[Any], int]:
        """
        Ruft eine Liste von Benutzern ab.

        Returns:
            Tuple mit (Liste der Benutzer, Gesamtanzahl)
        """
        pass

    @abstractmethod
    def create_user(self, user_data: Any) -> Any:
        """Erstellt einen neuen Benutzer."""
        pass

    @abstractmethod
    def update_user(self, user_id: uuid.UUID, user_data: Any) -> Optional[Any]:
        """Aktualisiert einen bestehenden Benutzer."""
        pass

    @abstractmethod
    def delete_user(self, user_id: uuid.UUID) -> bool:
        """Löscht einen Benutzer."""
        pass

    @abstractmethod
    def update_password(self, user_id: uuid.UUID, new_password: str) -> bool:
        """Aktualisiert das Passwort eines Benutzers."""
        pass

    @abstractmethod
    def activate_user(self, user_id: uuid.UUID) -> Optional[Any]:
        """Aktiviert einen Benutzer."""
        pass

    @abstractmethod
    def deactivate_user(self, user_id: uuid.UUID) -> Optional[Any]:
        """Deaktiviert einen Benutzer."""
        pass

