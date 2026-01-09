"""Register user use case."""

from datetime import datetime

from src.application.services.password_service import IPasswordService
from src.domain.entities import User
from src.domain.events import UserRegistered
from src.domain.exceptions import UserAlreadyExistsException
from src.domain.repositories import IUserRepository
from src.domain.value_objects import Email, Password
from src.infrastructure.events.event_bus import EventBus


class RegisterUserUseCase:
    """Use case for registering a new user."""

    def __init__(
        self,
        user_repository: IUserRepository,
        password_service: IPasswordService,
        event_bus: EventBus,
    ):
        self._user_repository = user_repository
        self._password_service = password_service
        self._event_bus = event_bus

    async def execute(self, email: str, password: str) -> User:
        """
        Register a new user.

        Args:
            email: User's email address
            password: User's plaintext password

        Returns:
            Created User entity

        Raises:
            UserAlreadyExistsException: If email is already registered
            InvalidEmailException: If email format is invalid
            InvalidPasswordException: If password doesn't meet requirements
        """
        # Create value objects (will validate automatically)
        email_vo = Email(value=email)
        password_vo = Password(value=password)

        # Check if user already exists
        if await self._user_repository.exists_by_email(email_vo):
            raise UserAlreadyExistsException(email)

        # Hash the password
        hashed_password = self._password_service.hash_password(password_vo)

        # Create user entity
        user = User.create(email=email_vo, password_hash=hashed_password)

        # Persist user
        user = await self._user_repository.save(user)

        # Publish domain event
        event = UserRegistered(
            occurred_at=datetime.utcnow(), user_id=user.id, email=user.email
        )
        await self._event_bus.publish(event)

        return user
