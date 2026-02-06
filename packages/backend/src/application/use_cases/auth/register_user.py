"""Register user use case."""

from datetime import datetime, timezone

from application.services.password_service import IPasswordService
from domain.entities import User
from domain.events import UserRegistered
from domain.exceptions import (
    UserEmailAlreadyExistsException,
    UsernameAlreadyExistsException,
)
from domain.repositories import (
    IUserRepository,
    IEmailVerificationRepository,
)
from domain.value_objects import Email, Password, Username
from infrastructure.events.event_bus import EventBus


class RegisterUserUseCase:
    """Use case for registering a new user."""

    def __init__(
        self,
        user_repository: IUserRepository,
        password_service: IPasswordService,
        event_bus: EventBus,
        verification_repository: IEmailVerificationRepository,
    ):
        self._user_repository = user_repository
        self._password_service = password_service
        self._event_bus = event_bus
        self._verification_repository = verification_repository

    async def execute(
        self, email: str, username: str, password: str, name: str | None = None
    ) -> User:
        """
        Register a new user.

        Args:
            email: User's email address
            username: User's username
            password: User's plaintext password
            name: User's full name (optional)

        Returns:
            Created User entity

        Raises:
            UserEmailAlreadyExistsException: If email is already in use
            UsernameAlreadyExistsException: If username is already in use
            InvalidEmailException: If email format is invalid
            InvalidPasswordException: If password doesn't meet requirements
            InvalidUsernameException: If username format is invalid
        """
        # Create value objects (will validate automatically)
        email_vo = Email(value=email)
        username_vo = Username(value=username)
        password_vo = Password(value=password)

        # Check if user already exists
        if await self._user_repository.exists_by_email(email_vo):
            raise UserEmailAlreadyExistsException(email)

        if await self._user_repository.exists_by_username(username_vo):
            raise UsernameAlreadyExistsException(username)

        # Hash the password
        hashed_password = self._password_service.hash_password(password_vo)

        # Create user entity
        user = User.create(
            email=email_vo,
            username=username_vo,
            password_hash=hashed_password,
            name=name,
        )

        # Persist user
        user = await self._user_repository.save(user)

        # Create email verification token
        from domain.entities import EmailVerification, VerificationType
        from config.settings import settings as app_settings
        from domain.events import EmailVerificationRequested

        verification = EmailVerification.create(
            user_id=user.id,
            email=email_vo,
            verification_type=VerificationType.REGISTRATION,
            expiry_hours=app_settings.email_verification_token_expire_hours,
        )

        # Save verification token
        await self._verification_repository.save(verification)

        # Publish verification event to trigger email sending
        verification_event = EmailVerificationRequested(
            occurred_at=datetime.now(timezone.utc),
            user_id=user.id,
            email=user.email,
            verification_token=str(verification.token),
            verification_type=verification.verification_type.value,
        )

        # Publish domain events
        event = UserRegistered(
            occurred_at=datetime.now(timezone.utc),
            user_id=user.id,
            email=user.email,
        )
        await self._event_bus.publish(event)
        await self._event_bus.publish(verification_event)

        return user
