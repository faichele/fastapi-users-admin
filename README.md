# Users Admin Module

Ein wiederverwendbares Python-Modul für Benutzerverwaltung in FastAPI-Anwendungen.

## Überblick

Das `users_admin` Modul bietet eine vollständige, produktionsreife Lösung für:

- **Benutzerverwaltung**: CRUD-Operationen für Benutzerkonten
- **Passwort-Management**: Passwortänderung und -reset
- **Benutzerprofilverwaltung**: Benutzer können ihre eigenen Daten verwalten
- **Admin-Interface**: HTML-basierte Administrationsoberfläche
- **Flexible Architektur**: Basis-Klassen ermöglichen verschiedene Backend-Implementierungen

## Architektur

Das Modul folgt einer sauberen, schichtweisen Architektur mit abstrakten Basisklassen:

```
users_admin/
├── models/              # Pydantic-Modelle
│   └── admin_models.py  # Admin-Datenmodelle
├── services/            # Business Logic Layer
│   ├── base_user_admin_service.py    # Abstrakte Basis-Klasse
│   ├── user_admin_service.py         # SQLAlchemy-Implementierung
│   └── user_crud_service.py          # CRUD-Hilfsfunktionen
├── utils/               # Utility-Funktionen
│   ├── security_utils.py  # Passwort-Hashing
│   └── email_utils.py     # E-Mail-Versand
├── dependencies/        # FastAPI Dependencies
│   └── admin_deps.py    # Auth-Dependencies für Admin
├── routers/             # FastAPI Router
│   └── user_admin_router.py  # Admin-Endpunkte
├── templates/           # HTML-Templates
│   └── admin_users.html # Admin-Interface
├── config/              # Konfiguration
│   └── admin_config.py  # Modul-Konfiguration
└── examples/            # Integrations-Beispiele
```

## Features

### Flexible Service-Architektur

Das Modul verwendet abstrakte Basisklassen (`BaseUserAdminService`), die es ermöglichen, verschiedene Backend-Implementierungen zu nutzen:

- **SQLAlchemy** (Standard-Implementierung)
- **MongoDB** oder andere NoSQL-Datenbanken
- **LDAP** oder Active Directory
- **Externe APIs** oder Identity Provider (Keycloak, Auth0)

### Benutzermodell

- UUID-basierte Benutzer-IDs
- E-Mail als Benutzername
- Sichere Passwort-Speicherung (bcrypt)
- Benutzer-Status (aktiv/inaktiv)
- Rollen-System (normale Benutzer/Superuser)
- Zeitstempel für Erstellung, Updates und letzten Login

### Admin-Interface

- Moderne HTML-Oberfläche mit Bootstrap 5
- Benutzer auflisten, erstellen, bearbeiten und löschen
- Modal-Dialoge für Benutzeroperationen
- Responsive Design für mobile Geräte

### API-Endpunkte

#### Admin-Interface
- `GET /api/admin` - Admin-Seite (HTML)

#### Benutzerverwaltung (`/api/users`)
- `GET /api/users` - Benutzer auflisten (Admin)
- `POST /api/users` - Benutzer erstellen (Admin)
- `POST /api/users/signup` - Öffentliche Registrierung
- `GET /api/users/me` - Eigene Informationen
- `PATCH /api/users/me` - Eigene Daten aktualisieren
- `PATCH /api/users/me/password` - Eigenes Passwort ändern
- `DELETE /api/users/me` - Eigenes Konto löschen
- `GET /api/users/{id}` - Benutzer nach ID
- `PATCH /api/users/{id}` - Benutzer aktualisieren (Admin)
- `DELETE /api/users/{id}` - Benutzer löschen (Admin)

## Installation & Integration

### 1. Installation

```bash
cd backend/fastapi_users_admin
pip install -e .
```

### 2. Einfache Integration

```python
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
    get_current_active_superuser
)
from backend.utils.auth import superuser_or_redirect

app = FastAPI()

# Konfiguration erstellen
config = AdminConfig(
    templates_dir="backend/fastapi_users_admin/templates",
    api_prefix="/api",
    router_tags=["users", "admin"],
    emails_enabled=False,
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
```

### 3. Eigene Service-Implementierung

Sie können eigene Service-Implementierungen erstellen, z.B. für LDAP:

```python
from users_admin.services import BaseUserAdminService

class LDAPUserAdminService(BaseUserAdminService):
    """LDAP-basierte Benutzerverwaltung."""
    
    def __init__(self, ldap_connection):
        self.ldap = ldap_connection
    
    def get_user_by_email(self, email: str):
        # LDAP-Implementierung
        return self.ldap.search(f"mail={email}")
    
    def create_user(self, user_data):
        # LDAP-Implementierung
        return self.ldap.add_user(user_data)
    
    # ... weitere Methoden
```

### 4. Multi-Provider-Setup mit Fallback

Sie können mehrere Service-Provider kombinieren:

```python
from users_admin.examples.multi_provider_example import MultiProviderUserAdminService

# Services erstellen
ldap_service = LDAPUserAdminService(ldap_connection)
db_service = UserAdminService(db_session, User, SecurityUtils())

# Multi-Provider-Service mit Fallback
multi_service = MultiProviderUserAdminService(
    primary_service=ldap_service,    # Primär: LDAP
    fallback_service=db_service      # Fallback: lokale DB
)
```

## Konfiguration

### AdminConfig

```python
from users_admin.config import AdminConfig

config = AdminConfig(
    # Template-Verzeichnis
    templates_dir="backend/fastapi_users_admin/templates",
    
    # API-Präfix
    api_prefix="/api",
    
    # Router-Tags
    router_tags=["users", "admin"],
    
    # E-Mail-Einstellungen
    emails_enabled=True,
    smtp_host="smtp.example.com",
    smtp_port=587,
    smtp_user="user@example.com",
    smtp_password="password",
    emails_from_email="noreply@example.com",
    emails_from_name="My App",
    
    # Passwort-Reset-Token Gültigkeit
    password_reset_token_expire_minutes=60,
    
    # Logging
    enable_logging=True,
    log_file="logs/fastapi_users_admin.log"
)
```

## Anpassung

### Eigene Templates

Sie können die HTML-Templates anpassen, indem Sie das Template-Verzeichnis in der Konfiguration angeben:

```python
config = AdminConfig(
    templates_dir="my_custom_templates"
)
```

### Eigene Dependencies

Sie können eigene Dependencies für Authentifizierung und Autorisierung bereitstellen:

```python
from fastapi import Depends, HTTPException

def my_custom_auth(token: str = Depends(oauth2_scheme)):
    # Ihre eigene Auth-Logik
    return verify_token(token)

admin_router = UserAdminRouter(
    database_session=get_db,
    config=config,
    get_current_user=my_custom_auth,
    # ...
)
```

## Testen

### Unit-Tests ausführen

```bash
cd backend/fastapi_users_admin
python test_module.py
```

### Demo-Anwendung starten

```bash
cd backend/fastapi_users_admin/examples
python complete_integration.py
```

Die Demo-Anwendung läuft auf `http://localhost:8000`:
- API-Dokumentation: `http://localhost:8000/docs`
- Admin-Interface: `http://localhost:8000/api/admin`

Standard-Admin-Zugangsdaten:
- E-Mail: `admin@example.com`
- Passwort: `admin123`

## Sicherheit

- **Passwort-Hashing**: Verwendet bcrypt für sicheres Passwort-Hashing
- **Token-basierte Authentifizierung**: Kompatibel mit JWT und OAuth2
- **Rollentrennung**: Unterscheidung zwischen normalen Benutzern und Admins
- **Input-Validierung**: Pydantic-Modelle validieren alle Eingaben
- **CSRF-Schutz**: Empfohlen für Produktionsumgebungen

## Abhängigkeiten

- FastAPI >= 0.100.0
- SQLAlchemy >= 2.0 (für Standard-Implementierung)
- Pydantic >= 2.7
- passlib (für Passwort-Hashing)
- bcrypt >= 4.0.0
- python-multipart >= 0.0.5
- jinja2 >= 3.1.0

## Beispiele

### Einfache Integration
Siehe `examples/integration_example.py`

### Multi-Provider mit Fallback
Siehe `examples/multi_provider_example.py`

### Vollständige Demo-Anwendung
Siehe `examples/complete_integration.py`

## Lizenz

MIT License - siehe LICENSE Datei

## Autor

Fabian Aichele <aichele@zykl.io>

## Changelog

### Version 1.0.0 (2025-10-10)

- Initiales Release
- Basis-Service-Architektur mit abstrakten Klassen
- SQLAlchemy-Implementierung
- HTML-Admin-Interface
- CRUD-Operationen für Benutzer
- Passwort-Management
- E-Mail-Utilities
- Konfigurierbare Dependencies

## Support

Bei Fragen oder Problemen:
- Siehe [INSTALL.md](INSTALL.md) für Installationsanleitungen
- Siehe [examples/](examples/) für Integrations-Beispiele
- Siehe [../README_authentication.md](../../docs/backend/dependencies/README_authentication_multi.md) für Gesamtübersicht
- E-Mail: aichele@zykl.io

