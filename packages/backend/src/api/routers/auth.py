"""Authentication router with registration, login, logout, and token refresh endpoints."""

from fastapi import APIRouter, Depends, status

from api.dependencies import (
    get_current_user,
    get_email_verification_repository,
    get_event_bus_dependency,
    get_password_service,
    get_session_repository,
    get_token_service,
    get_user_repository,
)
from application.schemas import (
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    LoginRequest,
    LoginResponse,
    LogoutResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
    RegisterUserRequest,
    RegisterUserResponse,
    ResendVerificationRequest,
    ResendVerificationResponse,
    ResetPasswordRequest,
    ResetPasswordResponse,
    UserResponse,
    VerifyEmailRequest,
    VerifyEmailResponse,
)
from application.services.password_service import IPasswordService
from application.services.token_service import ITokenService
from application.use_cases.login_user import LoginUserUseCase
from application.use_cases.logout_user import LogoutUserUseCase
from application.use_cases.refresh_token import RefreshTokenUseCase
from application.use_cases.register_user import RegisterUserUseCase
from domain.entities import User
from domain.repositories import ISessionRepository, IUserRepository
from infrastructure.events.event_bus import EventBus

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=RegisterUserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account with email and password",
)
async def register(
    request: RegisterUserRequest,
    user_repository: IUserRepository = Depends(get_user_repository),
    password_service: IPasswordService = Depends(get_password_service),
    event_bus: EventBus = Depends(get_event_bus_dependency),
    verification_repository=Depends(get_email_verification_repository),
):
    """Register a new user account."""
    use_case = RegisterUserUseCase(
        user_repository, password_service, event_bus, verification_repository
    )
    user = await use_case.execute(request.email, request.password, request.name)

    return RegisterUserResponse(
        user_id=str(user.id), email=str(user.email), created_at=user.created_at
    )


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="Login user",
    description="Authenticate user and receive JWT tokens",
)
async def login(
    request: LoginRequest,
    user_repository: IUserRepository = Depends(get_user_repository),
    session_repository: ISessionRepository = Depends(get_session_repository),
    password_service: IPasswordService = Depends(get_password_service),
    token_service: ITokenService = Depends(get_token_service),
    event_bus: EventBus = Depends(get_event_bus_dependency),
):
    """Authenticate user and create a session."""
    use_case = LoginUserUseCase(
        user_repository,
        session_repository,
        password_service,
        token_service,
        event_bus,
    )

    access_token, refresh_token, session = await use_case.execute(
        request.email, request.password
    )

    # Get user for response
    user = await user_repository.find_by_id(session.user_id)
    assert user is not None, "User should exist for valid session"

    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=token_service.get_access_token_expiry_seconds(),
        user=UserResponse(
            id=str(user.id),
            email=str(user.email),
            name=user.name,
            avatar=user.avatar,
            created_at=user.created_at,
            is_active=user.is_active,
            is_email_verified=user.is_email_verified,
        ),
    )


@router.post(
    "/logout",
    response_model=LogoutResponse,
    summary="Logout user",
    description="Revoke the current session",
)
async def logout(
    current_user: User = Depends(get_current_user),
    session_repository: ISessionRepository = Depends(get_session_repository),
    event_bus: EventBus = Depends(get_event_bus_dependency),
):
    """Logout the current user by revoking their session."""
    use_case = LogoutUserUseCase(session_repository, event_bus)

    # Note: We need to get the session ID from the token
    # For now, we'll revoke all sessions for the user
    # In production, you'd want to get the specific session ID from the request
    await session_repository.revoke_all_for_user(current_user.id)

    return LogoutResponse()


@router.post(
    "/refresh",
    response_model=RefreshTokenResponse,
    summary="Refresh access token",
    description="Get a new access token using a refresh token",
)
async def refresh_token(
    request: RefreshTokenRequest,
    session_repository: ISessionRepository = Depends(get_session_repository),
    token_service: ITokenService = Depends(get_token_service),
):
    """Refresh the access token using a valid refresh token."""
    use_case = RefreshTokenUseCase(session_repository, token_service)
    access_token = await use_case.execute(request.refresh_token)

    return RefreshTokenResponse(
        access_token=access_token,
        expires_in=token_service.get_access_token_expiry_seconds(),
    )


# Email Verification Endpoints


@router.post("/verify-email", response_model=VerifyEmailResponse)
async def verify_email(
    request: VerifyEmailRequest,
    user_repository: IUserRepository = Depends(get_user_repository),
    verification_repository=Depends(get_email_verification_repository),
    event_bus: EventBus = Depends(get_event_bus_dependency),
):
    """Verify user email with token."""
    from application.use_cases.verify_email import VerifyEmailUseCase

    use_case = VerifyEmailUseCase(
        user_repository, verification_repository, event_bus
    )
    message, email = await use_case.execute(request.token)

    return VerifyEmailResponse(message=message, email=email)


@router.post("/resend-verification", response_model=ResendVerificationResponse)
async def resend_verification(
    request: ResendVerificationRequest,
    user_repository: IUserRepository = Depends(get_user_repository),
    verification_repository=Depends(get_email_verification_repository),
    event_bus: EventBus = Depends(get_event_bus_dependency),
):
    """Resend verification email to user."""
    from application.use_cases.resend_verification import (
        ResendVerificationUseCase,
    )

    use_case = ResendVerificationUseCase(
        user_repository, verification_repository, event_bus
    )
    await use_case.execute(request.email)

    return ResendVerificationResponse()


@router.post("/forgot-password", response_model=ForgotPasswordResponse)
async def forgot_password(
    request: ForgotPasswordRequest,
    user_repository: IUserRepository = Depends(get_user_repository),
    verification_repository=Depends(get_email_verification_repository),
    event_bus: EventBus = Depends(get_event_bus_dependency),
):
    """Request password reset email."""
    from application.use_cases.request_password_reset import (
        RequestPasswordResetUseCase,
    )

    use_case = RequestPasswordResetUseCase(
        user_repository, verification_repository, event_bus
    )
    await use_case.execute(request.email)

    return ForgotPasswordResponse()


@router.post("/reset-password", response_model=ResetPasswordResponse)
async def reset_password(
    request: ResetPasswordRequest,
    user_repository: IUserRepository = Depends(get_user_repository),
    verification_repository=Depends(get_email_verification_repository),
    session_repository: ISessionRepository = Depends(get_session_repository),
    password_service: IPasswordService = Depends(get_password_service),
    event_bus: EventBus = Depends(get_event_bus_dependency),
):
    """Reset password with verification token."""
    from application.use_cases.reset_password import ResetPasswordUseCase

    use_case = ResetPasswordUseCase(
        user_repository,
        verification_repository,
        session_repository,
        password_service,
        event_bus,
    )
    await use_case.execute(request.token, request.new_password)

    return ResetPasswordResponse()
