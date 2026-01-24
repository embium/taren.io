"""Refresh token use case."""

from application.services.token_service import ITokenService
from domain.exceptions import (
    InvalidTokenException,
    SessionExpiredException,
    SessionNotFoundException,
)
from domain.repositories import ISessionRepository
from domain.value_objects import SessionId, UserId


class RefreshTokenUseCase:
    """Use case for refreshing access tokens."""

    def __init__(
        self,
        session_repository: ISessionRepository,
        token_service: ITokenService,
    ):
        self._session_repository = session_repository
        self._token_service = token_service

    async def execute(self, refresh_token: str) -> str:
        """
        Refresh an access token using a valid refresh token.

        Args:
            refresh_token: JWT refresh token

        Returns:
            New access token

        Raises:
            InvalidTokenException: If refresh token is invalid
            SessionNotFoundException: If session doesn't exist
            SessionExpiredException: If session has expired
        """
        # Decode and validate refresh token
        try:
            payload = self._token_service.decode_refresh_token(refresh_token)
        except Exception:
            raise InvalidTokenException()

        # Extract session and user IDs from token
        session_id_str = payload.get("session_id")
        user_id_str = payload.get("user_id")

        if not session_id_str or not user_id_str:
            raise InvalidTokenException()

        # Verify session is valid
        session = await self._session_repository.find_by_id(
            SessionId.from_string(session_id_str)
        )

        if not session:
            raise SessionNotFoundException()

        if not session.is_valid():
            if session.is_expired():
                raise SessionExpiredException()
            raise InvalidTokenException()

        # Generate new access token
        access_token = self._token_service.create_access_token(
            UserId.from_string(user_id_str),
            SessionId.from_string(session_id_str),
        )

        return access_token
