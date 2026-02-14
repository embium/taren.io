"""FastAPI dependencies."""

from fastapi import Cookie, Depends, HTTPException, status
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.security import token_service
from models.user import User
from services.auth_service import auth_service


async def get_current_user(
    access_token: str = Cookie(None),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Get current authenticated user from access token cookie."""
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    try:
        user = await auth_service.get_current_user_from_token(db, access_token)
        return user
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
