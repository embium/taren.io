"""Users router for protected user endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status

from api.dependencies import (
    get_current_user,
    get_user_repository,
    get_session_repository,
    get_password_service,
)
from application.schemas import (
    UserResponse,
    UpdateUserRequest,
    DeleteAccountRequest,
    DeleteAccountResponse,
)
from application.services.password_service import IPasswordService
from domain.entities import User
from domain.repositories import IUserRepository, ISessionRepository

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
        username=str(current_user.username),
        name=current_user.name,
        avatar=current_user.avatar,
        created_at=current_user.created_at,
        is_active=current_user.is_active,
        is_email_verified=current_user.is_email_verified,
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
    from application.use_cases.users.update_profile import UpdateProfileUseCase

    use_case = UpdateProfileUseCase(user_repository)
    await use_case.execute(update_data, current_user)

    return UserResponse(
        id=str(current_user.id),
        email=str(current_user.email),
        username=str(current_user.username),
        name=current_user.name,
        avatar=current_user.avatar,
        created_at=current_user.created_at,
        is_active=current_user.is_active,
        is_email_verified=current_user.is_email_verified,
        username_last_changed_at=current_user.username_last_changed_at,
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
    from application.use_cases.users.delete_account import DeleteAccountUseCase

    use_case = DeleteAccountUseCase(
        user_repository, session_repository, password_service
    )
    await use_case.execute(delete_data, current_user)

    return DeleteAccountResponse(message="Account successfully deactivated")
