"""Domain events for the authentication system."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict

from src.domain.value_objects import Email, UserId, SessionId


@dataclass(frozen=True)
class DomainEvent:
    """Base class for all domain events."""

    occurred_at: datetime

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization."""
        return {
            "event_type": self.__class__.__name__,
            "occurred_at": self.occurred_at.isoformat(),
        }


@dataclass(frozen=True)
class UserRegistered(DomainEvent):
    """Event raised when a new user registers."""

    user_id: UserId
    email: Email

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary."""
        base = super().to_dict()
        base.update({"user_id": str(self.user_id), "email": str(self.email)})
        return base


@dataclass(frozen=True)
class UserLoggedIn(DomainEvent):
    """Event raised when a user successfully logs in."""

    user_id: UserId
    session_id: SessionId

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary."""
        base = super().to_dict()
        base.update(
            {"user_id": str(self.user_id), "session_id": str(self.session_id)}
        )
        return base


@dataclass(frozen=True)
class UserLoggedOut(DomainEvent):
    """Event raised when a user logs out."""

    user_id: UserId
    session_id: SessionId

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary."""
        base = super().to_dict()
        base.update(
            {"user_id": str(self.user_id), "session_id": str(self.session_id)}
        )
        return base


@dataclass(frozen=True)
class PasswordChanged(DomainEvent):
    """Event raised when a user changes their password."""

    user_id: UserId

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary."""
        base = super().to_dict()
        base.update({"user_id": str(self.user_id)})
        return base


@dataclass(frozen=True)
class SessionExpired(DomainEvent):
    """Event raised when a session expires."""

    session_id: SessionId
    user_id: UserId

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary."""
        base = super().to_dict()
        base.update(
            {"session_id": str(self.session_id), "user_id": str(self.user_id)}
        )
        return base
