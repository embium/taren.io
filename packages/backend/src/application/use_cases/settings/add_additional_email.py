"""Add additional email use case."""

from datetime import datetime, timezone

from domain.entities import EmailVerification, VerificationType
from domain.events import EmailVerificationRequested
from domain.exceptions import UserEmailAlreadyExistsException
from domain.repositories import (
    IEmailVerificationRepository,
    IUserRepository,
)
from domain.value_objects import Email, UserId
from infrastructure.events.event_bus import EventBus
from config.settings import settings


class AddAdditionalEmailUseCase:
    """Use case for adding additional email to user account."""

    def __init__(
        self,
        user_repository: IUserRepository,
        verification_repository: IEmailVerificationRepository,
        event_bus: EventBus,
    ):
        self._user_repository = user_repository
        self._verification_repository = verification_repository
        self._event_bus = event_bus

    async def execute(self, user_id: str, email: str) -> None:
        """
        Request to add additional email to user account.

        Args:
            user_id: ID of the current user
            email: New email address to add

        Raises:
            UserEmailAlreadyExistsException: If email is already in use
        """
        # Parse values
        user_id_vo = UserId.from_string(user_id)
        email_vo = Email(value=email)

        # Check if email already exists
        if await self._user_repository.exists_by_email(email_vo):
            raise UserEmailAlreadyExistsException(email)

        # Get current user
        user = await self._user_repository.find_by_id(user_id_vo)
        if not user:
            raise ValueError("User not found")

        # Create verification token for additional email
        verification = EmailVerification.create(
            user_id=user.id,
            email=email_vo,
            verification_type=VerificationType.ADDITIONAL_EMAIL,
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
