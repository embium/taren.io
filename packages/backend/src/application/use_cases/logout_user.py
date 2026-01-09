"""Logout user use case."""

from datetime import datetime

from src.domain.entities import Session
from src.domain.events import UserLoggedOut
from src.domain.exceptions import SessionNotFoundException
from src.domain.repositories import ISessionRepository
from src.domain.value_objects import SessionId
from src.infrastructure.events.event_bus import EventBus


class LogoutUserUseCase:
    """Use case for user logout."""

    def __init__(
        self,
        session_repository: ISessionRepository,
        event_bus: EventBus,
    ):
        self._session_repository = session_repository
        self._event_bus = event_bus

    async def execute(self, session_id: str) -> None:
        """
        Logout user by revoking their session.

        Args:
            session_id: Session ID to revoke

        Raises:
            SessionNotFoundException: If session doesn't exist
        """
        # Find session
        session_id_vo = SessionId.from_string(session_id)
        session = await self._session_repository.find_by_id(session_id_vo)

        if not session:
            raise SessionNotFoundException()

        # Revoke session
        session.revoke()
        await self._session_repository.save(session)

        # Publish domain event
        event = UserLoggedOut(
            occurred_at=datetime.utcnow(),
            user_id=session.user_id,
            session_id=session.id,
        )
        await self._event_bus.publish(event)
