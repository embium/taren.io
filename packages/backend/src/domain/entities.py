"""Domain entities for the authentication system."""

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Optional

from domain.value_objects import (
    Email,
    HashedPassword,
    SessionId,
    UserId,
    Username,
    VerificationToken,
    VerificationTokenId,
)


@dataclass
class User:
    """User aggregate root entity."""

    id: UserId
    email: Email
    username: "Username"
    password_hash: HashedPassword
    name: Optional[str] = None
    avatar: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True
    is_email_verified: bool = False
    username_last_changed_at: Optional[datetime] = None

    @classmethod
    def create(
        cls,
        email: Email,
        username: "Username",
        password_hash: HashedPassword,
        user_id: Optional[UserId] = None,
        name: Optional[str] = None,
    ) -> "User":
        """Factory method to create a new user."""
        return cls(
            id=user_id or UserId.generate(),
            email=email,
            username=username,
            name=name,
            password_hash=password_hash,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            is_active=True,
        )

    def deactivate(self) -> None:
        """Deactivate the user account."""
        self.is_active = False
        self.updated_at = datetime.now(timezone.utc)

    def activate(self) -> None:
        """Activate the user account."""
        self.is_active = True
        self.updated_at = datetime.now(timezone.utc)

    def update_password(self, new_password_hash: HashedPassword) -> None:
        """Update user password."""
        self.password_hash = new_password_hash
        self.updated_at = datetime.now(timezone.utc)

    def update_profile(
        self,
        name: Optional[str] = None,
        email: Optional[Email] = None,
        avatar: Optional[str] = None,
        username: Optional[Username] = None,
    ) -> None:
        """Update user profile information."""
        if name is not None:
            self.name = name
        if email is not None:
            self.email = email
        if avatar is not None:
            self.avatar = avatar
        if username is not None:
            self.username = username
            self.username_last_changed_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)

    def verify_email(self) -> None:
        """Mark user email as verified."""
        self.is_email_verified = True
        self.updated_at = datetime.now(timezone.utc)

    def __eq__(self, other: object) -> bool:
        """Users are equal if they have the same ID."""
        if not isinstance(other, User):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)


@dataclass
class Session:
    """Session entity for managing authentication sessions."""

    id: SessionId
    user_id: UserId
    created_at: datetime
    expires_at: datetime
    is_revoked: bool = False

    @classmethod
    def create(
        cls,
        user_id: UserId,
        session_id: Optional[SessionId] = None,
        expiry_days: int = 7,
    ) -> "Session":
        """Factory method to create a new session."""
        now = datetime.now(timezone.utc)
        return cls(
            id=session_id or SessionId.generate(),
            user_id=user_id,
            created_at=now,
            expires_at=now + timedelta(days=expiry_days),
            is_revoked=False,
        )

    def is_valid(self) -> bool:
        """Check if session is valid (not expired and not revoked)."""
        return (
            not self.is_revoked and datetime.now(timezone.utc) < self.expires_at
        )

    def is_expired(self) -> bool:
        """Check if session has expired."""
        return datetime.now(timezone.utc) >= self.expires_at

    def revoke(self) -> None:
        """Revoke the session (logout)."""
        self.is_revoked = True

    def refresh(self, expiry_days: int = 7) -> None:
        """Extend session expiration time."""
        if self.is_valid():
            self.expires_at = datetime.now(timezone.utc) + timedelta(
                days=expiry_days
            )

    def __eq__(self, other: object) -> bool:
        """Sessions are equal if they have the same ID."""
        if not isinstance(other, Session):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)


class VerificationType(str, Enum):
    """Types of email verification."""

    REGISTRATION = "registration"
    PASSWORD_RESET = "password_reset"
    ADDITIONAL_EMAIL = "additional_email"


@dataclass
class EmailVerification:
    """Email verification entity for managing verification tokens."""

    id: VerificationTokenId
    user_id: UserId
    email: Email
    token: VerificationToken
    verification_type: VerificationType
    created_at: datetime
    expires_at: datetime
    is_used: bool = False

    @classmethod
    def create(
        cls,
        user_id: UserId,
        email: Email,
        verification_type: VerificationType,
        expiry_hours: int = 24,
        verification_id: Optional[VerificationTokenId] = None,
    ) -> "EmailVerification":
        """Factory method to create a new email verification."""
        now = datetime.now(timezone.utc)
        return cls(
            id=verification_id or VerificationTokenId.generate(),
            user_id=user_id,
            email=email,
            token=VerificationToken.generate(),
            verification_type=verification_type,
            created_at=now,
            expires_at=now + timedelta(hours=expiry_hours),
            is_used=False,
        )

    def is_valid(self) -> bool:
        """Check if verification token is valid (not expired and not used)."""
        return not self.is_used and datetime.now(timezone.utc) < self.expires_at

    def is_expired(self) -> bool:
        """Check if verification token has expired."""
        return datetime.now(timezone.utc) >= self.expires_at

    def mark_as_used(self) -> None:
        """Mark the verification token as used."""
        self.is_used = True

    def __eq__(self, other: object) -> bool:
        """Verifications are equal if they have the same ID."""
        if not isinstance(other, EmailVerification):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
