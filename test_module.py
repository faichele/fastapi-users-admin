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

