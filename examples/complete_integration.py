"""
Vollständiges Integrations-Beispiel für das fastapi_users_admin Modul.

Dieses Beispiel zeigt die Integration in eine FastAPI-Anwendung mit
allen notwendigen Abhängigkeiten und Konfigurationen.
"""

from fastapi import FastAPI, Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import asynccontextmanager

# Import des fastapi_users_admin Moduls
from users_admin import UserAdminRouter
from users_admin.config import AdminConfig
from users_admin.utils import SecurityUtils

# Annahme: Diese Imports existieren in Ihrer Anwendung
# from backend.database.models import User
# from backend.api.deps import get_current_user, get_current_active_superuser
# from backend.utils.auth import superuser_or_redirect


# ============================================================================
# DATABASE SETUP
# ============================================================================

# Datenbank-Verbindung
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_users.db"
# Für PostgreSQL:
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@localhost/dbname"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}  # Nur für SQLite
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Dependency für Datenbank-Session
def get_db():
    """Stellt eine Datenbank-Session bereit."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============================================================================
# USER MODEL (Beispiel)
# ============================================================================

from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid as uuid_pkg

Base = declarative_base()


class User(Base):
    """Beispiel User-Model."""
    __tablename__ = "users"

    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid_pkg.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String)
    password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)


# ============================================================================
# AUTHENTICATION DEPENDENCIES (vereinfacht)
# ============================================================================

from fastapi import HTTPException, status, Request
from fastapi.responses import RedirectResponse
from starlette.status import HTTP_302_FOUND


def get_current_user(session: Session = Depends(get_db), token: str = None):
    """
    Simplified dependency to get current user from token.
    In production, use proper JWT token validation.
    """
    # Dies ist eine vereinfachte Version
    # In der Realität würden Sie hier das JWT-Token validieren
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )

    # Beispiel: Token ist die E-Mail-Adresse (NICHT für Produktion!)
    user = session.query(User).filter(User.email == token).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user


def get_current_active_superuser(
    current_user: User = Depends(get_current_user)
):
    """Prüft ob der aktuelle Benutzer ein Superuser ist."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges"
        )
    return current_user


def superuser_or_redirect(
    request: Request,
    session: Session = Depends(get_db)
):
    """
    Für HTML-Seiten: Prüft Superuser-Status oder leitet um.
    """
    try:
        # Token aus Cookie oder Header holen
        token = request.cookies.get("access_token") or request.headers.get("Authorization")

        if not token:
            return RedirectResponse(
                url=f"/api/login?next={request.url.path}",
                status_code=HTTP_302_FOUND
            )

        # Token bereinigen
        token = token.replace("Bearer ", "") if token.startswith("Bearer ") else token

        # Benutzer abrufen
        current_user = get_current_user(session=session, token=token)

        if not current_user or not current_user.is_superuser:
            return RedirectResponse(
                url="/login?message=Access%20denied",
                status_code=HTTP_302_FOUND
            )

        return current_user
    except Exception:
        return RedirectResponse(
            url=f"/api/login?next={request.url.path}",
            status_code=HTTP_302_FOUND
        )


# ============================================================================
# FASTAPI APPLICATION
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events für die App."""
    # Startup: Datenbank-Tabellen erstellen
    Base.metadata.create_all(bind=engine)
    print("Database tables created")

    # Beispiel-Admin-Benutzer erstellen (nur für Entwicklung!)
    db = SessionLocal()
    try:
        security = SecurityUtils()
        existing_admin = db.query(User).filter(User.email == "admin@example.com").first()

        if not existing_admin:
            admin = User(
                uuid=uuid_pkg.uuid4(),
                email="admin@example.com",
                full_name="Admin User",
                password=security.get_password_hash("admin123"),
                is_active=True,
                is_superuser=True
            )
            db.add(admin)
            db.commit()
            print("Admin user created: admin@example.com / admin123")
    finally:
        db.close()

    yield

    # Shutdown
    print("Application shutdown")


# FastAPI App erstellen
app = FastAPI(
    title="Users Admin Demo",
    description="Demo-Anwendung für das fastapi_users_admin Modul",
    version="1.0.0",
    lifespan=lifespan
)


# ============================================================================
# USERS ADMIN MODULE INTEGRATION
# ============================================================================

# Konfiguration
admin_config = AdminConfig(
    templates_dir="backend/fastapi_users_admin/templates",
    api_prefix="/api",
    router_tags=["users", "admin"],
    emails_enabled=False,  # E-Mail deaktiviert für Demo
    enable_logging=True,
    log_file="logs/fastapi_users_admin.log"
)

# Security Utils
security_utils = SecurityUtils()

# Router erstellen und einbinden
admin_router = UserAdminRouter(
    database_session=get_db,
    config=admin_config,
    user_model=User,
    security_utils=security_utils,
    get_current_user=get_current_user,
    get_current_superuser=get_current_active_superuser,
    superuser_or_redirect=superuser_or_redirect
)

# Router in App einbinden
app.include_router(admin_router.router)


# ============================================================================
# ADDITIONAL ROUTES (optional)
# ============================================================================

@app.get("/")
async def root():
    """Root-Endpunkt."""
    return {
        "message": "Users Admin Demo API",
        "admin_interface": "/api/admin",
        "api_docs": "/docs",
        "users_endpoint": "/api/users"
    }


@app.get("/health")
async def health_check():
    """Health-Check-Endpunkt."""
    return {"status": "healthy"}


# ============================================================================
# RUN APPLICATION
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    print("\n" + "="*60)
    print("Starting Users Admin Demo Application")
    print("="*60)
    print("\nAccess the application at:")
    print("  - API Documentation: http://localhost:8000/docs")
    print("  - Admin Interface:   http://localhost:8000/api/admin")
    print("  - Root Endpoint:     http://localhost:8000/")
    print("\nDefault Admin Credentials:")
    print("  Email:    admin@example.com")
    print("  Password: admin123")
    print("\n" + "="*60 + "\n")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
"""
Test-Skript für das fastapi_users_admin Modul.

Dieses Skript kann verwendet werden, um die Funktionalität des Moduls zu testen.
"""

import sys
import uuid
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from users_admin.models.admin_models import (
    UserAdminCreate,
    UserAdminUpdate,
    UserAdminPublic
)
from users_admin.services.base_user_admin_service import BaseUserAdminService
from users_admin.utils.security_utils import SecurityUtils


class MockUserAdminService(BaseUserAdminService):
    """Mock-Service für Tests ohne Datenbank."""

    def __init__(self):
        self.users = {}
        self.security = SecurityUtils()

    def get_user_by_id(self, user_id: uuid.UUID):
        return self.users.get(str(user_id))

    def get_user_by_email(self, email: str):
        for user in self.users.values():
            if user.get('email') == email:
                return user
        return None

    def get_users(self, skip: int = 0, limit: int = 100):
        users_list = list(self.users.values())[skip:skip+limit]
        return users_list, len(self.users)

    def create_user(self, user_data):
        user_id = uuid.uuid4()
        user = {
            'uuid': user_id,
            'email': user_data.email,
            'full_name': user_data.full_name,
            'is_active': user_data.is_active,
            'is_superuser': user_data.is_superuser,
            'password': self.security.get_password_hash(user_data.password)
        }
        self.users[str(user_id)] = user
        return user

    def update_user(self, user_id: uuid.UUID, user_data):
        user = self.users.get(str(user_id))
        if not user:
            return None

        if user_data.email:
            user['email'] = user_data.email
        if user_data.full_name:
            user['full_name'] = user_data.full_name
        if user_data.password:
            user['password'] = self.security.get_password_hash(user_data.password)
        if user_data.is_active is not None:
            user['is_active'] = user_data.is_active
        if user_data.is_superuser is not None:
            user['is_superuser'] = user_data.is_superuser

        return user

    def delete_user(self, user_id: uuid.UUID):
        if str(user_id) in self.users:
            del self.users[str(user_id)]
            return True
        return False

    def update_password(self, user_id: uuid.UUID, new_password: str):
        user = self.users.get(str(user_id))
        if not user:
            return False
        user['password'] = self.security.get_password_hash(new_password)
        return True

    def activate_user(self, user_id: uuid.UUID):
        user = self.users.get(str(user_id))
        if not user:
            return None
        user['is_active'] = True
        return user

    def deactivate_user(self, user_id: uuid.UUID):
        user = self.users.get(str(user_id))
        if not user:
            return None
        user['is_active'] = False
        return user


def test_user_admin_service():
    """Testet die Basis-Funktionalität des UserAdminService."""

    print("=== Testing fastapi_users_admin Module ===\n")

    service = MockUserAdminService()

    # Test 1: Create User
    print("Test 1: Create User")
    user_create = UserAdminCreate(
        email="test@example.com",
        full_name="Test User",
        password="TestPassword123",
        is_active=True,
        is_superuser=False
    )
    user = service.create_user(user_create)
    print(f"✓ Created user: {user['email']} (ID: {user['uuid']})\n")

    # Test 2: Get User by Email
    print("Test 2: Get User by Email")
    found_user = service.get_user_by_email("test@example.com")
    assert found_user is not None
    print(f"✓ Found user: {found_user['email']}\n")

    # Test 3: Get User by ID
    print("Test 3: Get User by ID")
    user_id = user['uuid']
    found_user = service.get_user_by_id(user_id)
    assert found_user is not None
    print(f"✓ Found user by ID: {found_user['uuid']}\n")

    # Test 4: Update User
    print("Test 4: Update User")
    user_update = UserAdminUpdate(
        full_name="Updated Test User",
        is_active=False
    )
    updated_user = service.update_user(user_id, user_update)
    assert updated_user['full_name'] == "Updated Test User"
    assert updated_user['is_active'] == False
    print(f"✓ Updated user: {updated_user['full_name']}, Active: {updated_user['is_active']}\n")

    # Test 5: Update Password
    print("Test 5: Update Password")
    success = service.update_password(user_id, "NewPassword123")
    assert success == True
    print("✓ Password updated successfully\n")

    # Test 6: Activate User
    print("Test 6: Activate User")
    activated_user = service.activate_user(user_id)
    assert activated_user['is_active'] == True
    print("✓ User activated\n")

    # Test 7: Deactivate User
    print("Test 7: Deactivate User")
    deactivated_user = service.deactivate_user(user_id)
    assert deactivated_user['is_active'] == False
    print("✓ User deactivated\n")

    # Test 8: Get Users List
    print("Test 8: Get Users List")
    users, count = service.get_users()
    assert count == 1
    print(f"✓ Found {count} user(s)\n")

    # Test 9: Delete User
    print("Test 9: Delete User")
    success = service.delete_user(user_id)
    assert success == True
    users, count = service.get_users()
    assert count == 0
    print("✓ User deleted successfully\n")

    print("=== All tests passed! ===")


def test_security_utils():
    """Testet die Security-Utils."""

    print("\n=== Testing Security Utils ===\n")

    security = SecurityUtils()

    # Test Password Hashing
    print("Test 1: Password Hashing")
    password = "MySecurePassword123"
    hashed = security.get_password_hash(password)
    print(f"✓ Password hashed: {hashed[:50]}...\n")

    # Test Password Verification
    print("Test 2: Password Verification")
    is_valid = security.verify_password(password, hashed)
    assert is_valid == True
    print("✓ Password verification successful\n")

    # Test Wrong Password
    print("Test 3: Wrong Password")
    is_valid = security.verify_password("WrongPassword", hashed)
    assert is_valid == False
    print("✓ Wrong password correctly rejected\n")

    print("=== Security tests passed! ===")


if __name__ == "__main__":
    try:
        test_security_utils()
        test_user_admin_service()
        print("\n✓ All tests completed successfully!")
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

