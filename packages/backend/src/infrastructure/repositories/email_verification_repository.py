"""Email verification repository implementation."""

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities import EmailVerification, VerificationType
from domain.repositories import IEmailVerificationRepository
from domain.value_objects import (
    Email,
    UserId,
    VerificationToken,
    VerificationTokenId,
)
from infrastructure.database.models import EmailVerificationModel


class EmailVerificationRepository(IEmailVerificationRepository):
    """SQLAlchemy implementation of email verification repository."""

    def __init__(self, db_session: AsyncSession):
        self._db = db_session

    async def save(self, verification: EmailVerification) -> EmailVerification:
        """Save or update an email verification."""
        # Check if exists
        stmt = select(EmailVerificationModel).where(
            EmailVerificationModel.id == str(verification.id)
        )
        result = await self._db.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            # Update existing
            existing.email = str(verification.email)
            existing.token = str(verification.token)
            existing.verification_type = verification.verification_type.value
            existing.expires_at = verification.expires_at
            existing.is_used = verification.is_used
        else:
            # Create new
            model = EmailVerificationModel(
                id=str(verification.id),
                user_id=str(verification.user_id),
                email=str(verification.email),
                token=str(verification.token),
                verification_type=verification.verification_type.value,
                created_at=verification.created_at,
                expires_at=verification.expires_at,
                is_used=verification.is_used,
            )
            self._db.add(model)

        await self._db.commit()
        return verification

    async def find_by_token(
        self, token: VerificationToken
    ) -> Optional[EmailVerification]:
        """Find an email verification by its token."""
        stmt = select(EmailVerificationModel).where(
            EmailVerificationModel.token == str(token)
        )
        result = await self._db.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            return None

        return self._to_entity(model)

    async def find_by_user_and_type(
        self, user_id: UserId, verification_type: VerificationType
    ) -> list[EmailVerification]:
        """Find all verifications for a user of a specific type."""
        stmt = (
            select(EmailVerificationModel)
            .where(EmailVerificationModel.user_id == str(user_id))
            .where(
                EmailVerificationModel.verification_type
                == verification_type.value
            )
            .order_by(EmailVerificationModel.created_at.desc())
        )
        result = await self._db.execute(stmt)
        models = result.scalars().all()

        return [self._to_entity(model) for model in models]

    async def delete_expired(self) -> int:
        """Delete all expired verifications and return count."""
        stmt = delete(EmailVerificationModel).where(
            EmailVerificationModel.expires_at < datetime.now(timezone.utc)
        )
        result = await self._db.execute(stmt)
        await self._db.commit()
        # type: ignore - rowcount exists on CursorResult but typing may not reflect it
        return result.rowcount if result.rowcount is not None else 0  # type: ignore[attr-defined]

    async def delete(self, verification_id: VerificationTokenId) -> None:
        """Delete a verification by its ID."""
        stmt = delete(EmailVerificationModel).where(
            EmailVerificationModel.id == str(verification_id)
        )
        await self._db.execute(stmt)
        await self._db.commit()

    @staticmethod
    def _ensure_utc(dt: datetime) -> datetime:
        """Ensure the datetime is timezone-aware (UTC)."""
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt

    def _to_entity(self, model: EmailVerificationModel) -> EmailVerification:
        """Convert database model to domain entity."""
        return EmailVerification(
            id=VerificationTokenId.from_string(model.id),
            user_id=UserId.from_string(model.user_id),
            email=Email(value=model.email),
            token=VerificationToken.from_string(model.token),
            verification_type=VerificationType(model.verification_type),
            created_at=self._ensure_utc(model.created_at),
            expires_at=self._ensure_utc(model.expires_at),
            is_used=model.is_used,
        )
