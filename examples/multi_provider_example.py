"""
Beispiel für ein Multi-Provider-Setup mit Fallback-Mechanismus.

Dieses Beispiel zeigt, wie man mehrere Authentifizierungs-Backends
kombinieren kann, z.B. primär LDAP mit Fallback auf lokale Datenbank.
"""

import uuid
from typing import Optional, List, Any
from users_admin.services import BaseUserAdminService


class MultiProviderUserAdminService(BaseUserAdminService):
    """
    Service der mehrere Provider kombiniert mit Fallback-Mechanismus.
    """

    def __init__(self, primary_service: BaseUserAdminService,
                 fallback_service: BaseUserAdminService):
        """
        Initialisiert den Multi-Provider-Service.

        Args:
            primary_service: Primärer Service (z.B. LDAP)
            fallback_service: Fallback-Service (z.B. lokale DB)
        """
        self.primary = primary_service
        self.fallback = fallback_service

    def get_user_by_id(self, user_id: uuid.UUID) -> Optional[Any]:
        """Versucht zuerst primären Service, dann Fallback."""
        user = self.primary.get_user_by_id(user_id)
        if not user:
            user = self.fallback.get_user_by_id(user_id)
        return user

    def get_user_by_email(self, email: str) -> Optional[Any]:
        """Versucht zuerst primären Service, dann Fallback."""
        user = self.primary.get_user_by_email(email)
        if not user:
            user = self.fallback.get_user_by_email(email)
        return user

    def get_users(self, skip: int = 0, limit: int = 100) -> tuple[List[Any], int]:
        """
        Kombiniert Benutzer von beiden Services.
        """
        primary_users, primary_count = self.primary.get_users(skip, limit)

        # Falls primärer Service keine Benutzer zurückgibt, Fallback nutzen
        if not primary_users:
            return self.fallback.get_users(skip, limit)

        return primary_users, primary_count

    def create_user(self, user_data: Any) -> Any:
        """
        Erstellt Benutzer nur im Fallback-Service.
        (Primärer Service könnte read-only sein, z.B. LDAP)
        """
        try:
            return self.primary.create_user(user_data)
        except NotImplementedError:
            # Falls primärer Service keine Erstellung unterstützt
            return self.fallback.create_user(user_data)

    def update_user(self, user_id: uuid.UUID, user_data: Any) -> Optional[Any]:
        """Aktualisiert im Service wo der Benutzer existiert."""
        user = self.primary.get_user_by_id(user_id)
        if user:
            try:
                return self.primary.update_user(user_id, user_data)
            except NotImplementedError:
                # Falls primärer Service read-only ist
                pass

        return self.fallback.update_user(user_id, user_data)

    def delete_user(self, user_id: uuid.UUID) -> bool:
        """Löscht aus beiden Services."""
        primary_deleted = False
        fallback_deleted = False

        try:
            primary_deleted = self.primary.delete_user(user_id)
        except NotImplementedError:
            pass

        try:
            fallback_deleted = self.fallback.delete_user(user_id)
        except NotImplementedError:
            pass

        return primary_deleted or fallback_deleted

    def update_password(self, user_id: uuid.UUID, new_password: str) -> bool:
        """Aktualisiert Passwort im entsprechenden Service."""
        user = self.primary.get_user_by_id(user_id)
        if user:
            try:
                return self.primary.update_password(user_id, new_password)
            except NotImplementedError:
                pass

        return self.fallback.update_password(user_id, new_password)

    def activate_user(self, user_id: uuid.UUID) -> Optional[Any]:
        """Aktiviert Benutzer im entsprechenden Service."""
        user = self.primary.get_user_by_id(user_id)
        if user:
            try:
                return self.primary.activate_user(user_id)
            except NotImplementedError:
                pass

        return self.fallback.activate_user(user_id)

    def deactivate_user(self, user_id: uuid.UUID) -> Optional[Any]:
        """Deaktiviert Benutzer im entsprechenden Service."""
        user = self.primary.get_user_by_id(user_id)
        if user:
            try:
                return self.primary.deactivate_user(user_id)
            except NotImplementedError:
                pass

        return self.fallback.deactivate_user(user_id)


# Verwendungsbeispiel
"""
from fastapi_users_admin.services import UserAdminService
from fastapi_users_admin.utils import SecurityUtils
from your_ldap_service import LDAPUserAdminService

# Services erstellen
ldap_service = LDAPUserAdminService(ldap_connection)
db_service = UserAdminService(db_session, User, SecurityUtils())

# Multi-Provider-Service mit Fallback
multi_service = MultiProviderUserAdminService(
    primary_service=ldap_service,    # Primär: LDAP
    fallback_service=db_service      # Fallback: lokale DB
)

# Im Router verwenden
# Der Router würde dann multi_service anstelle von UserAdminService nutzen
"""


class ReadOnlyLDAPService(BaseUserAdminService):
    """
    Beispiel für einen read-only LDAP-Service.
    """

    def __init__(self, ldap_config):
        self.ldap_config = ldap_config
        # LDAP-Connection-Setup hier

    def get_user_by_id(self, user_id: uuid.UUID) -> Optional[Any]:
        # LDAP-Implementierung
        pass

    def get_user_by_email(self, email: str) -> Optional[Any]:
        # LDAP-Implementierung
        pass

    def get_users(self, skip: int = 0, limit: int = 100) -> tuple[List[Any], int]:
        # LDAP-Implementierung
        pass

    def create_user(self, user_data: Any) -> Any:
        raise NotImplementedError("LDAP service is read-only")

    def update_user(self, user_id: uuid.UUID, user_data: Any) -> Optional[Any]:
        raise NotImplementedError("LDAP service is read-only")

    def delete_user(self, user_id: uuid.UUID) -> bool:
        raise NotImplementedError("LDAP service is read-only")

    def update_password(self, user_id: uuid.UUID, new_password: str) -> bool:
        raise NotImplementedError("LDAP service is read-only")

    def activate_user(self, user_id: uuid.UUID) -> Optional[Any]:
        raise NotImplementedError("LDAP service is read-only")

    def deactivate_user(self, user_id: uuid.UUID) -> Optional[Any]:
        raise NotImplementedError("LDAP service is read-only")

