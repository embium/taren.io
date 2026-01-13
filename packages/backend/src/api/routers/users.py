"""Users router for protected user endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status

from src.api.dependencies import (
    get_current_user,
    get_user_repository,
    get_session_repository,
    get_password_service,
)
from src.application.schemas import (
    UserResponse,
    UpdateUserRequest,
    DeleteAccountRequest,
    DeleteAccountResponse,
)
from src.application.services.password_service import IPasswordService
from src.domain.entities import User
from src.domain.repositories import IUserRepository, ISessionRepository
from src.domain.value_objects import Email, Password

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
        name=current_user.name,
        avatar=current_user.avatar,
        created_at=current_user.created_at,
        is_active=current_user.is_active,
    )


@router.patch(
    "/me",
    response_model=UserResponse,
    summary="Update current user profile",
    description="Update the profile of the currently authenticated user",
)
async def update_profile(
    update_data: UpdateUserRequest,
    current_user: User = Depends(get_current_user),
    user_repository: IUserRepository = Depends(get_user_repository),
):
    """Update the current user's profile (name, email, avatar)."""
    # Check if email is being updated and if it's already taken
    if update_data.email and str(update_data.email) != str(current_user.email):
        if await user_repository.exists_by_email(
            Email(value=str(update_data.email))
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use",
            )
        email_to_update = Email(value=str(update_data.email))
    else:
        email_to_update = None

    # Update user profile
    current_user.update_profile(
        name=update_data.name,
        email=email_to_update,
        avatar=update_data.avatar,
    )

    # Save to database
    await user_repository.save(current_user)

    return UserResponse(
        id=str(current_user.id),
        email=str(current_user.email),
        name=current_user.name,
        avatar=current_user.avatar,
        created_at=current_user.created_at,
        is_active=current_user.is_active,
    )


@router.delete(
    "/me",
    response_model=DeleteAccountResponse,
    summary="Delete current user account",
    description="Soft-delete the current user account (marks as inactive)",
)
async def delete_account(
    delete_data: DeleteAccountRequest,
    current_user: User = Depends(get_current_user),
    user_repository: IUserRepository = Depends(get_user_repository),
    session_repository: ISessionRepository = Depends(get_session_repository),
    password_service: IPasswordService = Depends(get_password_service),
):
    """Soft-delete the current user account after password verification."""
    # Verify password
    if not password_service.verify_password(
        Password(value=delete_data.password),
        current_user.password_hash,
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid password",
        )

    # Deactivate user account (soft delete)
    current_user.deactivate()
    await user_repository.save(current_user)

    # Revoke all active sessions
    await session_repository.revoke_all_for_user(current_user.id)

    return DeleteAccountResponse(message="Account successfully deactivated")
