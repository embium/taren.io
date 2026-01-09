"""Dependency injection for FastAPI."""

from typing import Annotated

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.services.password_service import IPasswordService
from src.application.services.token_service import ITokenService
from src.domain.entities import User
from src.domain.exceptions import InvalidTokenException
from src.domain.repositories import ISessionRepository, IUserRepository
from src.domain.value_objects import SessionId, UserId
from src.infrastructure.database.connection import get_db
from src.infrastructure.repositories.session_repository import SessionRepository
from src.infrastructure.repositories.user_repository import UserRepository
from src.infrastructure.security.jwt_handler import JWTHandler
from src.infrastructure.security.password_hasher import Argon2PasswordHasher
from src.infrastructure.events.event_bus import EventBus, get_event_bus


# Service providers
def get_password_service() -> IPasswordService:
    """Provide password hashing service."""
    return Argon2PasswordHasher()


def get_token_service() -> ITokenService:
    """Provide JWT token service."""
    return JWTHandler()


def get_event_bus_dependency() -> EventBus:
    """Provide event bus instance."""
    return get_event_bus()


# Repository providers


def get_user_repository(db: AsyncSession = Depends(get_db)) -> IUserRepository:
    """Provide user repository."""
    return UserRepository(db)


def get_session_repository(
    db: AsyncSession = Depends(get_db),
) -> ISessionRepository:
    """Provide session repository."""
    return SessionRepository(db)


# Authentication dependency
async def get_current_user(
    authorization: Annotated[str | None, Header()] = None,
    token_service: ITokenService = Depends(get_token_service),
    user_repository: IUserRepository = Depends(get_user_repository),
    session_repository: ISessionRepository = Depends(get_session_repository),
) -> User:
    """
    Get the current authenticated user from JWT token.

    Raises:
        HTTPException: If authentication fails
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Check if authorization header exists
    if not authorization:
        raise credentials_exception

    # Extract token from "Bearer <token>"
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise credentials_exception
    except ValueError:
        raise credentials_exception

    # Decode and validate token
    try:
        payload = token_service.decode_access_token(token)
    except InvalidTokenException:
        raise credentials_exception

    # Extract user and session IDs
    user_id_str = payload.get("user_id")
    session_id_str = payload.get("session_id")

    if not user_id_str or not session_id_str:
        raise credentials_exception

    # Verify session is valid
    session = await session_repository.find_by_id(
        SessionId.from_string(session_id_str)
    )
    if not session or not session.is_valid():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired or invalid",
        )

    # Get user
    user = await user_repository.find_by_id(UserId.from_string(user_id_str))
    if not user:
        raise credentials_exception

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    return user
