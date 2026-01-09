"""Login user use case."""

from datetime import datetime

from src.application.services.password_service import IPasswordService
from src.application.services.token_service import ITokenService
from src.domain.entities import Session
from src.domain.events import UserLoggedIn
from src.domain.exceptions import (
    InvalidCredentialsException,
    UserNotFoundException,
)
from src.domain.repositories import ISessionRepository, IUserRepository
from src.domain.value_objects import Email, Password
from src.infrastructure.events.event_bus import EventBus


class LoginUserUseCase:
    """Use case for user authentication."""

    def __init__(
        self,
        user_repository: IUserRepository,
        session_repository: ISessionRepository,
        password_service: IPasswordService,
        token_service: ITokenService,
        event_bus: EventBus,
    ):
        self._user_repository = user_repository
        self._session_repository = session_repository
        self._password_service = password_service
        self._token_service = token_service
        self._event_bus = event_bus

    async def execute(
        self, email: str, password: str
    ) -> tuple[str, str, Session]:
        """
        Authenticate user and create session.

        Args:
            email: User's email address
            password: User's plaintext password

        Returns:
            Tuple of (access_token, refresh_token, session)

        Raises:
            InvalidCredentialsException: If credentials are invalid
            UserNotFoundException: If user doesn't exist
        """
        # Create value objects
        email_vo = Email(value=email)
        password_vo = Password(value=password)

        # Find user by email
        user = await self._user_repository.find_by_email(email_vo)
        if not user:
            raise InvalidCredentialsException()

        # Verify password
        if not self._password_service.verify_password(
            password_vo, user.password_hash
        ):
            raise InvalidCredentialsException()

        # Check if user is active
        if not user.is_active:
            raise InvalidCredentialsException()

        # Create new session
        session = Session.create(user_id=user.id)
        session = await self._session_repository.save(session)

        # Generate tokens
        access_token = self._token_service.create_access_token(
            user.id, session.id
        )
        refresh_token = self._token_service.create_refresh_token(
            user.id, session.id
        )

        # Publish domain event
        event = UserLoggedIn(
            occurred_at=datetime.utcnow(),
            user_id=user.id,
            session_id=session.id,
        )
        await self._event_bus.publish(event)

        return (access_token, refresh_token, session)
