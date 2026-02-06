"""User repository implementation using SQLAlchemy."""

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities import User
from domain.repositories import IUserRepository
from domain.value_objects import Email, HashedPassword, UserId, Username
from infrastructure.database.models import UserModel


class UserRepository(IUserRepository):
    """SQLAlchemy implementation of user repository."""

    def __init__(self, session: AsyncSession):
        """Initialize repository with database session."""
        self._session = session

    async def save(self, user: User) -> User:
        """Save or update a user in the database."""
        # Check if user exists
        result = await self._session.execute(
            select(UserModel).where(UserModel.id == str(user.id))
        )
        existing = result.scalar_one_or_none()

        if existing:
            # Update existing user
            existing.email = str(user.email)
            existing.username = str(user.username)
            existing.name = user.name
            existing.avatar = user.avatar
            existing.password_hash = str(user.password_hash.value)
            existing.updated_at = user.updated_at
            existing.is_active = user.is_active
            existing.is_email_verified = user.is_email_verified
            existing.username_last_changed_at = user.username_last_changed_at
        else:
            # Create new user
            user_model = UserModel(
                id=str(user.id),
                email=str(user.email),
                username=str(user.username),
                name=user.name,
                avatar=user.avatar,
                password_hash=user.password_hash.value,
                created_at=user.created_at,
                updated_at=user.updated_at,
                is_active=user.is_active,
                is_email_verified=user.is_email_verified,
                username_last_changed_at=user.username_last_changed_at,
            )
            self._session.add(user_model)

        await self._session.flush()
        return user

    async def find_by_id(self, user_id: UserId) -> Optional[User]:
        """Find a user by their ID."""
        result = await self._session.execute(
            select(UserModel).where(UserModel.id == str(user_id))
        )
        user_model = result.scalar_one_or_none()

        if not user_model:
            return None

        return self._model_to_entity(user_model)

    async def find_by_email(self, email: Email) -> Optional[User]:
        """Find a user by their email address."""
        result = await self._session.execute(
            select(UserModel).where(UserModel.email == str(email))
        )
        user_model = result.scalar_one_or_none()

        if not user_model:
            return None

        return self._model_to_entity(user_model)

    async def find_by_username(self, username: Username) -> Optional[User]:
        """Find a user by their username."""
        result = await self._session.execute(
            select(UserModel).where(UserModel.username == str(username))
        )
        user_model = result.scalar_one_or_none()

        if not user_model:
            return None

        return self._model_to_entity(user_model)

    async def exists_by_email(self, email: Email) -> bool:
        """Check if a user with the given email exists."""
        result = await self._session.execute(
            select(UserModel.id).where(UserModel.email == str(email))
        )
        return result.scalar_one_or_none() is not None

    async def exists_by_username(self, username: Username) -> bool:
        """Check if a user with the given username exists."""
        result = await self._session.execute(
            select(UserModel.id).where(UserModel.username == str(username))
        )
        return result.scalar_one_or_none() is not None

    async def delete(self, user_id: UserId) -> None:
        """Delete a user by their ID."""
        result = await self._session.execute(
            select(UserModel).where(UserModel.id == str(user_id))
        )
        user_model = result.scalar_one_or_none()

        if user_model:
            await self._session.delete(user_model)
            await self._session.flush()

    @staticmethod
    def _ensure_utc(dt: datetime) -> datetime:
        """Ensure the datetime is timezone-aware (UTC)."""
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt

    @staticmethod
    def _model_to_entity(model: UserModel) -> User:
        """Convert SQLAlchemy model to domain entity."""
        return User(
            id=UserId.from_string(model.id),
            email=Email(value=model.email),
            username=Username(value=model.username),
            password_hash=HashedPassword(value=model.password_hash),
            name=model.name,
            avatar=model.avatar,
            created_at=UserRepository._ensure_utc(model.created_at),
            updated_at=UserRepository._ensure_utc(model.updated_at),
            is_active=model.is_active,
            is_email_verified=model.is_email_verified,
            username_last_changed_at=(
                UserRepository._ensure_utc(model.username_last_changed_at)
                if model.username_last_changed_at
                else None
            ),
        )
