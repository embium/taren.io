"""User management service."""

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.security import password_service
from exceptions import (
    EmailAlreadyExistsError,
    InvalidCredentialsError,
    UserNotFoundError,
    UsernameAlreadyExistsError,
    UsernameChangeRestrictedError,
    UsernameAlreadyCurrentError,
)
from models.user import Session, User
from schemas.auth import ChangePasswordRequest, UpdateUserRequest, UserResponse


class UserService:
    """Service for user management operations."""

    async def get_user_by_id(self, db: AsyncSession, user_id: str) -> User:
        """Get user by ID."""
        user = await db.get(User, user_id)
        if not user:
            raise UserNotFoundError()
        return user

    async def update_user(
        self, db: AsyncSession, user_id: str, data: UpdateUserRequest
    ) -> UserResponse:
        """Update user profile."""
        user = await self.get_user_by_id(db, user_id)

        # Check email uniqueness if changing
        if data.email and data.email != user.email:
            existing = await db.scalar(
                select(User).where(User.email == data.email)
            )
            if existing and existing.id != user.id:
                raise EmailAlreadyExistsError()

        # Update user
        user.update_profile(
            name=data.name,
            email=data.email,
            avatar=data.avatar,
        )

        await db.commit()
        await db.refresh(user)

        return UserResponse.model_validate(user)

    async def change_password(
        self, db: AsyncSession, user_id: str, data: ChangePasswordRequest
    ) -> None:
        """Change user password."""
        user = await self.get_user_by_id(db, user_id)

        # Verify current password
        is_valid, _ = password_service.verify_password(
            data.current_password, str(user.password_hash)
        )
        if not is_valid:
            raise InvalidCredentialsError()

        # Update password
        new_hash = password_service.hash_password(data.new_password)
        user.update_password(new_hash)

        await db.commit()

    async def delete_user(
        self, db: AsyncSession, user_id: str, password: str
    ) -> None:
        """Delete (deactivate) user account."""
        user = await self.get_user_by_id(db, user_id)

        # Verify password
        is_valid, _ = password_service.verify_password(
            password, str(user.password_hash)
        )
        if not is_valid:
            raise InvalidCredentialsError()

        # Deactivate account
        user.deactivate()

        # Revoke all sessions
        result = await db.execute(
            select(Session).where(Session.user_id == user.id)
        )
        sessions = result.scalars().all()
        for session in sessions:
            session.revoke()

        await db.commit()


# Global service instance
user_service = UserService()
