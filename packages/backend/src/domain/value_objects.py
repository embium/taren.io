"""Value objects for the authentication domain."""

import re
import uuid
from dataclasses import dataclass
from typing import Union

from domain.exceptions import (
    InvalidEmailException,
    InvalidPasswordException,
    InvalidUsernameException,
)


@dataclass(frozen=True)
class Username:
    """Username value object with validation."""

    value: str

    def __post_init__(self):
        """Validate username format on initialization."""
        self._validate_username(self.value)

    @staticmethod
    def _validate_username(username: str) -> None:
        """
        Validate username format:
        - Length between 3 and 30 characters
        - Alphanumeric, underscores, and hyphens only
        """
        if not (3 <= len(username) <= 30):
            raise InvalidUsernameException(
                "Username must be between 3 and 30 characters"
            )

        if not re.match(r"^[a-zA-Z0-9_-]+$", username):
            raise InvalidUsernameException(
                "Username can only contain letters, numbers, underscores, and hyphens"
            )

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class Email:
    """Email value object with validation."""

    value: str

    def __post_init__(self):
        """Validate email format on initialization."""
        if not self._is_valid_email(self.value):
            raise InvalidEmailException(self.value)

    @staticmethod
    def _is_valid_email(email: str) -> bool:
        """Validate email format using regex."""
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, email))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class Password:
    """Password value object with complexity requirements."""

    value: str

    def __post_init__(self):
        """Validate password complexity on initialization."""
        self._validate_password(self.value)

    @staticmethod
    def _validate_password(password: str) -> None:
        """
        Validate password meets complexity requirements:
        - Minimum 8 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one digit
        - At least one special character
        """
        if len(password) < 8:
            raise InvalidPasswordException(
                "Password must be at least 8 characters long"
            )

        if not re.search(r"[A-Z]", password):
            raise InvalidPasswordException(
                "Password must contain at least one uppercase letter"
            )

        if not re.search(r"[a-z]", password):
            raise InvalidPasswordException(
                "Password must contain at least one lowercase letter"
            )

        if not re.search(r"\d", password):
            raise InvalidPasswordException(
                "Password must contain at least one digit"
            )

        if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]", password):
            raise InvalidPasswordException(
                "Password must contain at least one special character"
            )

    def __str__(self) -> str:
        return "********"  # Never expose password in string representation


@dataclass(frozen=True)
class HashedPassword:
    """Hashed password value object - immutable and secure."""

    value: str

    def __str__(self) -> str:
        return "********"  # Never expose hash in logs


@dataclass(frozen=True)
class UserId:
    """User identifier value object."""

    value: str

    @classmethod
    def generate(cls) -> "UserId":
        """Generate a new unique user ID."""
        return cls(value=str(uuid.uuid4()))

    @classmethod
    def from_string(cls, user_id: str) -> "UserId":
        """Create UserId from string."""
        return cls(value=user_id)

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class SessionId:
    """Session identifier value object."""

    value: str

    @classmethod
    def generate(cls) -> "SessionId":
        """Generate a new unique session ID."""
        return cls(value=str(uuid.uuid4()))

    @classmethod
    def from_string(cls, session_id: str) -> "SessionId":
        """Create SessionId from string."""
        return cls(value=session_id)

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class VerificationTokenId:
    """Verification token identifier value object."""

    value: str

    @classmethod
    def generate(cls) -> "VerificationTokenId":
        """Generate a new unique verification token ID."""
        return cls(value=str(uuid.uuid4()))

    @classmethod
    def from_string(cls, token_id: str) -> "VerificationTokenId":
        """Create VerificationTokenId from string."""
        return cls(value=token_id)

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class VerificationToken:
    """Verification token value object - cryptographically secure random token."""

    value: str

    @classmethod
    def generate(cls) -> "VerificationToken":
        """Generate a new cryptographically secure verification token."""
        import secrets

        # Generate 32 bytes (256 bits) of random data, URL-safe base64 encoded
        token = secrets.token_urlsafe(32)
        return cls(value=token)

    @classmethod
    def from_string(cls, token: str) -> "VerificationToken":
        """Create VerificationToken from string."""
        return cls(value=token)

    def __str__(self) -> str:
        return self.value
