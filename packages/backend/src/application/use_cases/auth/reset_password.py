"""Reset password use case."""

from datetime import datetime, timezone

from application.services.password_service import IPasswordService
from domain.entities import VerificationType
from domain.events import PasswordResetCompleted
from domain.exceptions import (
    ExpiredVerificationTokenException,
    InvalidVerificationTokenException,
)
from domain.repositories import (
    IEmailVerificationRepository,
    ISessionRepository,
    IUserRepository,
)
from domain.value_objects import Password, VerificationToken
from infrastructure.events.event_bus import EventBus


class ResetPasswordUseCase:
    """Use case for resetting password with verification token."""

    def __init__(
        self,
        user_repository: IUserRepository,
        verification_repository: IEmailVerificationRepository,
        session_repository: ISessionRepository,
        password_service: IPasswordService,
        event_bus: EventBus,
    ):
        self._user_repository = user_repository
        self._verification_repository = verification_repository
        self._session_repository = session_repository
        self._password_service = password_service
        self._event_bus = event_bus

    async def execute(self, token: str, new_password: str) -> None:
        """
        Reset user password using verification token.

        Args:
            token: Password reset token
            new_password: New password (plaintext)

        Raises:
            InvalidVerificationTokenException: If token is invalid
            ExpiredVerificationTokenException: If token has expired
            InvalidPasswordException: If password doesn't meet requirements
        """
        # Find verification by token
        token_vo = VerificationToken.from_string(token)
        verification = await self._verification_repository.find_by_token(
            token_vo
        )

        if not verification:
            raise InvalidVerificationTokenException()

        if verification.verification_type != VerificationType.PASSWORD_RESET:
            raise InvalidVerificationTokenException()

        if verification.is_expired():
            raise ExpiredVerificationTokenException()

        if verification.is_used:
            raise InvalidVerificationTokenException()

        # Validate new password
        password_vo = Password(value=new_password)

        # Get user
        user = await self._user_repository.find_by_id(verification.user_id)
        if not user:
            raise InvalidVerificationTokenException()

        # Hash and update password
        hashed_password = self._password_service.hash_password(password_vo)
        user.update_password(hashed_password)
        await self._user_repository.save(user)

        # Mark verification as used
        verification.mark_as_used()
        await self._verification_repository.save(verification)

        # Revoke all existing sessions for security
        await self._session_repository.revoke_all_for_user(user.id)

        # Publish event
        event = PasswordResetCompleted(
            occurred_at=datetime.now(timezone.utc),
            user_id=user.id,
        )
        await self._event_bus.publish(event)
