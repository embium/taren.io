"""Resend verification email use case."""

from datetime import datetime, timezone

from domain.entities import EmailVerification, VerificationType
from domain.events import EmailVerificationRequested
from domain.exceptions import UserNotFoundException
from domain.repositories import (
    IEmailVerificationRepository,
    IUserRepository,
)
from domain.value_objects import Email
from infrastructure.events.event_bus import EventBus
from config.settings import settings


class ResendVerificationUseCase:
    """Use case for resending verification email."""

    def __init__(
        self,
        user_repository: IUserRepository,
        verification_repository: IEmailVerificationRepository,
        event_bus: EventBus,
    ):
        self._user_repository = user_repository
        self._verification_repository = verification_repository
        self._event_bus = event_bus

    async def execute(self, email: str) -> None:
        """
        Resend verification email to user.

        Args:
            email: User's email address

        Raises:
            UserNotFoundException: If user not found
        """
        # Parse email
        email_vo = Email(value=email)

        # Find user
        user = await self._user_repository.find_by_email(email_vo)
        if not user:
            raise UserNotFoundException(email)

        # If already verified, do nothing
        if user.is_email_verified:
            return

        # Create new verification token
        verification = EmailVerification.create(
            user_id=user.id,
            email=email_vo,
            verification_type=VerificationType.REGISTRATION,
            expiry_hours=settings.email_verification_token_expire_hours,
        )

        # Save verification
        await self._verification_repository.save(verification)

        # Publish event to trigger email sending
        event = EmailVerificationRequested(
            occurred_at=datetime.now(timezone.utc),
            user_id=user.id,
            email=email_vo,
            verification_token=str(verification.token),
            verification_type=verification.verification_type.value,
        )
        await self._event_bus.publish(event)
