"""Repository interfaces for the domain layer."""

from abc import ABC, abstractmethod
from typing import Optional

from src.domain.entities import Session, User
from src.domain.value_objects import Email, SessionId, UserId


class IUserRepository(ABC):
    """Abstract interface for user persistence operations."""

    @abstractmethod
    async def save(self, user: User) -> User:
        """Save or update a user."""
        pass

    @abstractmethod
    async def find_by_id(self, user_id: UserId) -> Optional[User]:
        """Find a user by their ID."""
        pass

    @abstractmethod
    async def find_by_email(self, email: Email) -> Optional[User]:
        """Find a user by their email address."""
        pass

    @abstractmethod
    async def exists_by_email(self, email: Email) -> bool:
        """Check if a user with the given email exists."""
        pass

    @abstractmethod
    async def delete(self, user_id: UserId) -> None:
        """Delete a user by their ID."""
        pass


class ISessionRepository(ABC):
    """Abstract interface for session persistence operations."""

    @abstractmethod
    async def save(self, session: Session) -> Session:
        """Save or update a session."""
        pass

    @abstractmethod
    async def find_by_id(self, session_id: SessionId) -> Optional[Session]:
        """Find a session by its ID."""
        pass

    @abstractmethod
    async def find_by_user_id(self, user_id: UserId) -> list[Session]:
        """Find all sessions for a user."""
        pass

    @abstractmethod
    async def delete(self, session_id: SessionId) -> None:
        """Delete a session by its ID."""
        pass

    @abstractmethod
    async def delete_expired(self) -> int:
        """Delete all expired sessions and return count of deleted sessions."""
        pass

    @abstractmethod
    async def revoke_all_for_user(self, user_id: UserId) -> None:
        """Revoke all sessions for a specific user."""
        pass
