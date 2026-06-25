"""
Pydantic-Modelle für die Benutzerverwaltung.

Diese Modelle definieren die Datenstrukturen für Admin-Operationen.
"""

import uuid
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict

from fastapi_users_auth.models.user_models import UserRole


class UserAdminBase(BaseModel):
    """Basis-Modell für Benutzerdaten."""
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False


class UserAdminCreate(UserAdminBase):
    """Modell zum Erstellen eines neuen Benutzers."""
    password: str = Field(..., min_length=8)


class UserAdminUpdate(BaseModel):
    """Modell zum Aktualisieren von Benutzerdaten."""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8)
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None


class UserAdminPublic(UserAdminBase):
    """Öffentliches Benutzermodell (ohne Passwort)."""
    id: uuid.UUID = Field(..., serialization_alias="uuid")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    role: UserRole = UserRole.USER

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class UserAdminList(BaseModel):
    """Modell für die Liste von Benutzern."""
    data: List[UserAdminPublic]
    count: int


class PasswordResetRequest(BaseModel):
    """Modell für Passwort-Reset-Anfrage."""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Modell für Passwort-Reset-Bestätigung."""
    token: str
    new_password: str = Field(..., min_length=8)


class PasswordChange(BaseModel):
    """Modell für Passwortänderung durch den Benutzer selbst."""
    current_password: str
    new_password: str = Field(..., min_length=8)


class Message(BaseModel):
    """Generisches Nachrichtenmodell."""
    message: str

