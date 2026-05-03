"""
Sicherheits-Utilities für Passwort-Hashing und -Verifikation.
"""

from passlib.context import CryptContext


class SecurityUtils:
    """
    Utility-Klasse für Sicherheitsfunktionen.

    Stellt Methoden für Passwort-Hashing und -Verifikation bereit.
    """

    def __init__(self):
        self.pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

    def get_password_hash(self, password: str) -> str:
        """
        Hasht ein Passwort mit Argon2.

        Args:
            password: Das zu hashende Passwort

        Returns:
            Der gehashte Passwort-String
        """
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verifiziert ein Passwort gegen einen Hash.

        Args:
            plain_password: Das Klartext-Passwort
            hashed_password: Der gehashte Passwort-String

        Returns:
            True wenn das Passwort korrekt ist, sonst False
        """
        return self.pwd_context.verify(plain_password, hashed_password)
