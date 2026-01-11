"""Domain entities for the authentication system."""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional

from src.domain.value_objects import Email, HashedPassword, SessionId, UserId


@dataclass
class User:
    """User aggregate root entity."""

    id: UserId
    email: Email
    password_hash: HashedPassword
    name: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True

    @classmethod
    def create(
        cls,
        email: Email,
        password_hash: HashedPassword,
        user_id: Optional[UserId] = None,
        name: Optional[str] = None,
    ) -> "User":
        """Factory method to create a new user."""
        return cls(
            id=user_id or UserId.generate(),
            email=email,
            name=name,
            password_hash=password_hash,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            is_active=True,
        )

    def deactivate(self) -> None:
        """Deactivate the user account."""
        self.is_active = False
        self.updated_at = datetime.utcnow()

    def activate(self) -> None:
        """Activate the user account."""
        self.is_active = True
        self.updated_at = datetime.utcnow()

    def update_password(self, new_password_hash: HashedPassword) -> None:
        """Update user password."""
        self.password_hash = new_password_hash
        self.updated_at = datetime.utcnow()

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
        now = datetime.utcnow()
        return cls(
            id=session_id or SessionId.generate(),
            user_id=user_id,
            created_at=now,
            expires_at=now + timedelta(days=expiry_days),
            is_revoked=False,
        )

    def is_valid(self) -> bool:
        """Check if session is valid (not expired and not revoked)."""
        return not self.is_revoked and datetime.utcnow() < self.expires_at

    def is_expired(self) -> bool:
        """Check if session has expired."""
        return datetime.utcnow() >= self.expires_at

    def revoke(self) -> None:
        """Revoke the session (logout)."""
        self.is_revoked = True

    def refresh(self, expiry_days: int = 7) -> None:
        """Extend session expiration time."""
        if self.is_valid():
            self.expires_at = datetime.utcnow() + timedelta(days=expiry_days)

    def __eq__(self, other: object) -> bool:
        """Sessions are equal if they have the same ID."""
        if not isinstance(other, Session):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
