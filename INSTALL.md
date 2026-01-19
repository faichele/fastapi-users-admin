# Installation und Setup

## Installation des Moduls

### Entwicklungs-Installation (empfohlen)

```bash
cd backend/fastapi_users_admin
pip install -e .
```

### Standard-Installation

```bash
cd backend/fastapi_users_admin
pip install .
```

### Abhängigkeiten installieren

```bash
cd backend/fastapi_users_admin
pip install -r requirements.txt
```

## Schnellstart

### 1. Modul testen

```bash
cd backend/fastapi_users_admin
python test_module.py
```

### 2. Demo-Anwendung starten

```bash
cd backend/fastapi_users_admin/examples
python complete_integration.py
```

Die Demo-Anwendung startet auf `http://localhost:8000`

- API-Dokumentation: `http://localhost:8000/docs`
- Admin-Interface: `http://localhost:8000/api/admin`

Standard-Admin-Zugangsdaten:
- E-Mail: `admin@example.com`
- Passwort: `admin123`

### 3. In eigene FastAPI-App integrieren

```python
from users_admin import UserAdminRouter
from users_admin.config import AdminConfig
from users_admin.utils import SecurityUtils

# Konfiguration
config = AdminConfig(
    templates_dir="backend/fastapi_users_admin/templates",
    api_prefix="/api"
)

# Router erstellen
admin_router = UserAdminRouter(
    database_session=get_db,
    config=config,
    user_model=User,
    security_utils=SecurityUtils(),
    get_current_user=get_current_user,
    get_current_superuser=get_current_active_superuser,
    superuser_or_redirect=superuser_or_redirect
)

# In App einbinden
app.include_router(admin_router.router)
```

## Struktur

```
users_admin/
├── __init__.py              # Modul-Einstiegspunkt
├── pyproject.toml           # Paket-Konfiguration
├── requirements.txt         # Abhängigkeiten
├── README.md                # Dokumentation
├── LICENSE                  # Lizenz
├── test_module.py           # Tests
├── models/                  # Datenmodelle
├── services/                # Business Logic
├── routers/                 # API-Endpunkte
├── templates/               # HTML-Templates
├── utils/                   # Hilfsfunktionen
├── config/                  # Konfiguration
└── examples/                # Beispiele
```

## Konfiguration

Die Konfiguration erfolgt über die `AdminConfig`-Klasse:

```python
from users_admin.config import AdminConfig

config = AdminConfig(
    templates_dir="backend/fastapi_users_admin/templates",
    api_prefix="/api",
    router_tags=["users", "admin"],
    emails_enabled=True,
    smtp_host="smtp.example.com",
    smtp_port=587,
    smtp_user="user@example.com",
    smtp_password="password",
    emails_from_email="noreply@example.com",
    emails_from_name="My App",
    password_reset_token_expire_minutes=60,
    enable_logging=True,
    log_file="logs/fastapi_users_admin.log"
)
```

## Entwicklung

### Tests ausführen

```bash
python test_module.py
```

### Mit pytest

```bash
pytest test_module.py -v
```

### Code-Qualität prüfen

```bash
# Linting
ruff check .

# Type-Checking
mypy .
```

## Lizenz

MIT License - siehe LICENSE Datei
# Core dependencies
fastapi>=0.100.0
pydantic>=2.7,<3
sqlalchemy>=2.0
python-multipart>=0.0.5

# Security
passlib>=1.7.4
bcrypt>=4.0.0

# Templates
jinja2>=3.1.0

# Email (optional)
# aiosmtplib>=2.0.0

# Development dependencies
pytest>=7.4.0
pytest-cov>=4.1.0
mypy>=1.5.0
ruff>=0.0.290

