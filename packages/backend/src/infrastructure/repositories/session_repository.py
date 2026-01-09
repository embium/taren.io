"""Session repository implementation using SQLAlchemy."""

from datetime import datetime
from typing import Optional

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities import Session
from src.domain.repositories import ISessionRepository
from src.domain.value_objects import SessionId, UserId
from src.infrastructure.database.models import SessionModel


class SessionRepository(ISessionRepository):
    """SQLAlchemy implementation of session repository."""

    def __init__(self, session: AsyncSession):
        """Initialize repository with database session."""
        self._session = session

    async def save(self, session: Session) -> Session:
        """Save or update a session in the database."""
        # Check if session exists
        result = await self._session.execute(
            select(SessionModel).where(SessionModel.id == str(session.id))
        )
        existing = result.scalar_one_or_none()

        if existing:
            # Update existing session
            existing.expires_at = session.expires_at
            existing.is_revoked = session.is_revoked
        else:
            # Create new session
            session_model = SessionModel(
                id=str(session.id),
                user_id=str(session.user_id),
                created_at=session.created_at,
                expires_at=session.expires_at,
                is_revoked=session.is_revoked,
            )
            self._session.add(session_model)

        await self._session.flush()
        return session

    async def find_by_id(self, session_id: SessionId) -> Optional[Session]:
        """Find a session by its ID."""
        result = await self._session.execute(
            select(SessionModel).where(SessionModel.id == str(session_id))
        )
        session_model = result.scalar_one_or_none()

        if not session_model:
            return None

        return self._model_to_entity(session_model)

    async def find_by_user_id(self, user_id: UserId) -> list[Session]:
        """Find all sessions for a user."""
        result = await self._session.execute(
            select(SessionModel).where(SessionModel.user_id == str(user_id))
        )
        session_models = result.scalars().all()

        return [self._model_to_entity(model) for model in session_models]

    async def delete(self, session_id: SessionId) -> None:
        """Delete a session by its ID."""
        await self._session.execute(
            delete(SessionModel).where(SessionModel.id == str(session_id))
        )
        await self._session.flush()

    async def delete_expired(self) -> int:
        """Delete all expired sessions and return count."""
        result = await self._session.execute(
            delete(SessionModel).where(
                SessionModel.expires_at < datetime.utcnow()
            )
        )
        await self._session.flush()
        return result.rowcount or 0  # type: ignore[attr-defined]

    async def revoke_all_for_user(self, user_id: UserId) -> None:
        """Revoke all sessions for a specific user."""
        result = await self._session.execute(
            select(SessionModel).where(SessionModel.user_id == str(user_id))
        )
        sessions = result.scalars().all()

        for session in sessions:
            session.is_revoked = True

        await self._session.flush()

    @staticmethod
    def _model_to_entity(model: SessionModel) -> Session:
        """Convert SQLAlchemy model to domain entity."""
        return Session(
            id=SessionId.from_string(model.id),
            user_id=UserId.from_string(model.user_id),
            created_at=model.created_at,
            expires_at=model.expires_at,
            is_revoked=model.is_revoked,
        )
