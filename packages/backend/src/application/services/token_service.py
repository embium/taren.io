"""Token service interface for JWT token operations."""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any

from domain.value_objects import UserId, SessionId


class ITokenService(ABC):
    """Abstract interface for token generation and validation."""

    @abstractmethod
    def create_access_token(
        self, user_id: UserId, session_id: SessionId
    ) -> str:
        """Create a JWT access token."""
        pass

    @abstractmethod
    def create_refresh_token(
        self, user_id: UserId, session_id: SessionId
    ) -> str:
        """Create a JWT refresh token."""
        pass

    @abstractmethod
    def decode_access_token(self, token: str) -> Dict[str, Any]:
        """Decode and validate an access token. Returns payload."""
        pass

    @abstractmethod
    def decode_refresh_token(self, token: str) -> Dict[str, Any]:
        """Decode and validate a refresh token. Returns payload."""
        pass

    @abstractmethod
    def get_access_token_expiry_seconds(self) -> int:
        """Get access token expiry time in seconds."""
        pass
