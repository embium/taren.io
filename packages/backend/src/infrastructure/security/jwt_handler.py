"""JWT token handler for authentication."""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict

from jose import JWTError, jwt

from application.services.token_service import ITokenService
from config.settings import settings
from domain.exceptions import InvalidTokenException
from domain.value_objects import SessionId, UserId


class JWTHandler(ITokenService):
    """JWT token service implementation using python-jose."""

    def __init__(self):
        """Initialize JWT handler with settings from config."""
        self._secret_key = settings.jwt_secret_key
        self._algorithm = settings.jwt_algorithm
        self._access_token_expire_minutes = settings.access_token_expire_minutes
        self._refresh_token_expire_days = settings.refresh_token_expire_days

    def create_access_token(
        self, user_id: UserId, session_id: SessionId
    ) -> str:
        """
        Create a JWT access token.

        Args:
            user_id: User identifier
            session_id: Session identifier

        Returns:
            Encoded JWT access token
        """
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=self._access_token_expire_minutes
        )

        payload = {
            "user_id": str(user_id),
            "session_id": str(session_id),
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "type": "access",
        }

        return jwt.encode(payload, self._secret_key, algorithm=self._algorithm)

    def create_refresh_token(
        self, user_id: UserId, session_id: SessionId
    ) -> str:
        """
        Create a JWT refresh token.

        Args:
            user_id: User identifier
            session_id: Session identifier

        Returns:
            Encoded JWT refresh token
        """
        expire = datetime.now(timezone.utc) + timedelta(
            days=self._refresh_token_expire_days
        )

        payload = {
            "user_id": str(user_id),
            "session_id": str(session_id),
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "type": "refresh",
        }

        return jwt.encode(payload, self._secret_key, algorithm=self._algorithm)

    def decode_access_token(self, token: str) -> Dict[str, Any]:
        """
        Decode and validate an access token.

        Args:
            token: JWT access token

        Returns:
            Token payload dictionary

        Raises:
            InvalidTokenException: If token is invalid or expired
        """
        try:
            payload = jwt.decode(
                token, self._secret_key, algorithms=[self._algorithm]
            )

            # Verify token type
            if payload.get("type") != "access":
                raise InvalidTokenException()

            return payload
        except JWTError:
            raise InvalidTokenException()

    def decode_refresh_token(self, token: str) -> Dict[str, Any]:
        """
        Decode and validate a refresh token.

        Args:
            token: JWT refresh token

        Returns:
            Token payload dictionary

        Raises:
            InvalidTokenException: If token is invalid or expired
        """
        try:
            payload = jwt.decode(
                token, self._secret_key, algorithms=[self._algorithm]
            )

            # Verify token type
            if payload.get("type") != "refresh":
                raise InvalidTokenException()

            return payload
        except JWTError:
            raise InvalidTokenException()

    def get_access_token_expiry_seconds(self) -> int:
        """Get access token expiry time in seconds."""
        return self._access_token_expire_minutes * 60
