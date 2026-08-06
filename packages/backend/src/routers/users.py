"""User management router."""

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.dependencies import get_current_user
from models.user import User
from schemas.auth import (
    ChangePasswordRequest,
    DeleteAccountRequest,
    MessageResponse,
    UpdateUserRequest,
    UserResponse,
)
from services.user_service import user_service

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me")
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    """Get current user profile."""
    return UserResponse.model_validate(current_user)


@router.patch("/me")
async def update_user_profile(
    request: UpdateUserRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """Update user profile."""
    return await user_service.update_user(db, str(current_user.id), request)


@router.post("/me/password")
async def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    """Change user password."""
    await user_service.change_password(db, str(current_user.id), request)
    return MessageResponse(message="Password changed successfully")


@router.delete("/me")
async def delete_account(
    response: Response,
    request: DeleteAccountRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    """Delete (deactivate) user account."""
    await user_service.delete_user(db, str(current_user.id), request.password)

    # Clear cookies
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")

    return MessageResponse(message="Account successfully deactivated")
