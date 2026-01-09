"""Users router for protected user endpoints."""

from fastapi import APIRouter, Depends

from src.api.dependencies import get_current_user
from src.application.schemas import UserResponse
from src.domain.entities import User

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user",
    description="Get the profile of the currently authenticated user",
)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get the current user's profile."""
    return UserResponse(
        id=str(current_user.id),
        email=str(current_user.email),
        created_at=current_user.created_at,
        is_active=current_user.is_active,
    )
