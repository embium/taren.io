"""Security utilities for password hashing and token management."""

import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Dict

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from jose import JWTError, jwt

from core.config import settings


class PasswordHasherService:
    """Password hashing using Argon2id."""

    def __init__(self):
        """Initialize Argon2 password hasher with secure defaults."""
        self._hasher = PasswordHasher(
            time_cost=2,  # Number of iterations
            memory_cost=65536,  # Memory usage in KiB (64 MB)
            parallelism=4,  # Number of parallel threads
            hash_len=32,  # Length of the hash in bytes
            salt_len=16,  # Length of the salt in bytes
        )

    def hash_password(self, password: str) -> str:
        """Hash a plaintext password using Argon2id."""
        return self._hasher.hash(password)

    def verify_password(
        self, password: str, hashed_password: str
    ) -> tuple[bool, bool]:
        """
        Verify a plaintext password against a hashed password.

        Returns:
            Tuple of (is_valid, needs_rehash)
        """
        try:
            self._hasher.verify(hashed_password, password)

            # Check if rehashing is needed (parameters changed)
            if self._hasher.check_needs_rehash(hashed_password):
                return True, True

            return True, False
        except VerifyMismatchError:
            return False, False


class TokenService:
    """JWT token service for authentication."""

    def __init__(self):
        """Initialize JWT handler with settings from config."""
        self._secret_key = settings.jwt_secret_key
        self._algorithm = settings.jwt_algorithm
        self._access_token_expire_minutes = settings.access_token_expire_minutes
        self._refresh_token_expire_days = settings.refresh_token_expire_days

    def create_access_token(self, user_id: str, session_id: str) -> str:
        """Create a JWT access token."""
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=self._access_token_expire_minutes
        )

        payload = {
            "user_id": user_id,
            "session_id": session_id,
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "type": "access",
        }

        return jwt.encode(payload, self._secret_key, algorithm=self._algorithm)

    def create_refresh_token(self, user_id: str, session_id: str) -> str:
        """Create a JWT refresh token."""
        expire = datetime.now(timezone.utc) + timedelta(
            days=self._refresh_token_expire_days
        )

        payload = {
            "user_id": user_id,
            "session_id": session_id,
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "type": "refresh",
        }

        return jwt.encode(payload, self._secret_key, algorithm=self._algorithm)

    def decode_access_token(self, token: str) -> Dict[str, Any]:
        """
        Decode and validate an access token.

        Raises:
            JWTError: If token is invalid or expired
        """
        payload = jwt.decode(
            token, self._secret_key, algorithms=[self._algorithm]
        )

        # Verify token type
        if payload.get("type") != "access":
            raise JWTError("Invalid token type")

        return payload

    def decode_refresh_token(self, token: str) -> Dict[str, Any]:
        """
        Decode and validate a refresh token.

        Raises:
            JWTError: If token is invalid or expired
        """
        payload = jwt.decode(
            token, self._secret_key, algorithms=[self._algorithm]
        )

        # Verify token type
        if payload.get("type") != "refresh":
            raise JWTError("Invalid token type")

        return payload

    def get_access_token_expiry_seconds(self) -> int:
        """Get access token expiry time in seconds."""
        return self._access_token_expire_minutes * 60


def generate_verification_token() -> str:
    """Generate a secure random token for email verification."""
    return secrets.token_urlsafe(32)


# Global service instances
password_service = PasswordHasherService()
token_service = TokenService()
