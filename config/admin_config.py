"""
Konfiguration für das Benutzerverwaltungsmodul.
"""

from pathlib import Path
from typing import Optional
from pydantic import BaseModel

# Absoluter Pfad zum templates/-Verzeichnis dieses Pakets
_DEFAULT_TEMPLATES_DIR = str(Path(__file__).resolve().parent.parent / "templates")


class AdminConfig(BaseModel):
    """Konfigurationsklasse für Benutzerverwaltung."""

    # Template-Verzeichnis – standardmäßig das templates/-Verzeichnis des Moduls
    templates_dir: str = _DEFAULT_TEMPLATES_DIR

    # API-Präfix
    api_prefix: str = "/api"

    # Router-Tags
    router_tags: list = ["users", "admin"]

    # E-Mail-Einstellungen
    emails_enabled: bool = False
    smtp_host: Optional[str] = None
    smtp_port: Optional[int] = None
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None
    emails_from_email: Optional[str] = None
    emails_from_name: Optional[str] = None

    # Passwort-Reset-Token Gültigkeitsdauer (in Minuten)
    password_reset_token_expire_minutes: int = 60

    # Logging
    enable_logging: bool = True
    log_file: str = "logs/fastapi_users_admin.log"

    class Config:
        arbitrary_types_allowed = True

