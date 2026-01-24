"""Verify email use case."""

from datetime import datetime, timezone

from application.services.email_service import IEmailService
from domain.entities import EmailVerification, VerificationType
from domain.events import EmailVerified
from domain.exceptions import (
    ExpiredVerificationTokenException,
    InvalidVerificationTokenException,
)
from domain.repositories import (
    IEmailVerificationRepository,
    IUserRepository,
)
from domain.value_objects import VerificationToken
from infrastructure.events.event_bus import EventBus


class VerifyEmailUseCase:
    """Use case for verifying email address."""

    def __init__(
        self,
        user_repository: IUserRepository,
        verification_repository: IEmailVerificationRepository,
        event_bus: EventBus,
    ):
        self._user_repository = user_repository
        self._verification_repository = verification_repository
        self._event_bus = event_bus

    async def execute(self, token: str) -> tuple[str, str]:
        """
        Verify email using verification token.

        Args:
            token: Verification token string

        Returns:
            Tuple of (message, email)

        Raises:
            InvalidVerificationTokenException: If token is invalid
            ExpiredVerificationTokenException: If token has expired
        """
        # Find verification by token
        token_vo = VerificationToken.from_string(token)
        verification = await self._verification_repository.find_by_token(
            token_vo
        )

        if not verification:
            raise InvalidVerificationTokenException()

        if verification.is_expired():
            raise ExpiredVerificationTokenException()

        if verification.is_used:
            raise InvalidVerificationTokenException()

        # Mark verification as used
        verification.mark_as_used()
        await self._verification_repository.save(verification)

        # Get user and verify email
        user = await self._user_repository.find_by_id(verification.user_id)
        if not user:
            raise InvalidVerificationTokenException()

        # For registration verification, mark email as verified
        if verification.verification_type == VerificationType.REGISTRATION:
            user.verify_email()
            await self._user_repository.save(user)

            # Publish event
            event = EmailVerified(
                occurred_at=datetime.now(timezone.utc),
                user_id=user.id,
                email=user.email,
                verification_type=verification.verification_type.value,
            )
            await self._event_bus.publish(event)

            return (
                "Email verified successfully! You can now log in.",
                str(user.email),
            )

        # For additional email verification, update user email
        elif (
            verification.verification_type == VerificationType.ADDITIONAL_EMAIL
        ):
            user.update_profile(email=verification.email)
            await self._user_repository.save(user)

            # Publish event
            event = EmailVerified(
                occurred_at=datetime.now(timezone.utc),
                user_id=user.id,
                email=verification.email,
                verification_type=verification.verification_type.value,
            )
            await self._event_bus.publish(event)

            return ("Email updated successfully!", str(verification.email))

        raise InvalidVerificationTokenException()
