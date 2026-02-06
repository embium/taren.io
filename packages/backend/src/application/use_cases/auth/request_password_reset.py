"""Request password reset use case."""

from datetime import datetime, timezone

from domain.entities import EmailVerification, VerificationType
from domain.events import PasswordResetRequested
from domain.repositories import (
    IEmailVerificationRepository,
    IUserRepository,
)
from domain.value_objects import Email
from infrastructure.events.event_bus import EventBus
from config.settings import settings


class RequestPasswordResetUseCase:
    """Use case for requesting password reset."""

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
        Request password reset for a user.

        Args:
            email: User's email address

        Note:
            For security, this method doesn't reveal whether the email exists.
            It always returns success but only sends email if user exists.
        """
        # Parse email
        email_vo = Email(value=email)

        # Find user by email
        user = await self._user_repository.find_by_email(email_vo)

        # If user doesn't exist, return silently (security best practice)
        if not user:
            return

        # Create verification token for password reset
        verification = EmailVerification.create(
            user_id=user.id,
            email=email_vo,
            verification_type=VerificationType.PASSWORD_RESET,
            expiry_hours=settings.password_reset_token_expire_hours,
        )

        # Save verification
        await self._verification_repository.save(verification)

        # Publish event to trigger email sending
        event = PasswordResetRequested(
            occurred_at=datetime.now(timezone.utc),
            user_id=user.id,
            email=email_vo,
            reset_token=str(verification.token),
        )
        await self._event_bus.publish(event)
