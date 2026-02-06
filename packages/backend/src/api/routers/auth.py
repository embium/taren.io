"""Authentication router with registration, login, logout, and token refresh endpoints."""

from fastapi import APIRouter, Depends, status, Response

from api.dependencies import (
    get_current_user,
    get_email_verification_repository,
    get_event_bus_dependency,
    get_password_service,
    get_session_repository,
    get_token_service,
    get_user_repository,
)
from config.settings import settings
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
    CheckUsernameRequest,
    CheckUsernameResponse,
)
from application.services.password_service import IPasswordService
from application.services.token_service import ITokenService
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
    response: Response,
    request: RegisterUserRequest,
    user_repository: IUserRepository = Depends(get_user_repository),
    session_repository: ISessionRepository = Depends(get_session_repository),
    password_service: IPasswordService = Depends(get_password_service),
    token_service: ITokenService = Depends(get_token_service),
    event_bus: EventBus = Depends(get_event_bus_dependency),
    verification_repository=Depends(get_email_verification_repository),
):
    """Register a new user account and automatically log them in."""
    from application.use_cases.auth.register_user import RegisterUserUseCase
    from domain.entities import Session
    from domain.events import UserLoggedIn
    from datetime import datetime, timezone

    use_case = RegisterUserUseCase(
        user_repository, password_service, event_bus, verification_repository
    )
    user = await use_case.execute(
        request.email, request.username, request.password, request.name
    )

    # Auto-login: Create session and generate tokens
    session = Session.create(user_id=user.id)
    session = await session_repository.save(session)

    # Generate tokens
    access_token = token_service.create_access_token(user.id, session.id)
    refresh_token = token_service.create_refresh_token(user.id, session.id)

    # Publish domain event
    event = UserLoggedIn(
        occurred_at=datetime.now(timezone.utc),
        user_id=user.id,
        session_id=session.id,
    )
    await event_bus.publish(event)

    # Set HTTP-only cookies for tokens
    is_production = settings.environment == "production"

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=is_production,
        samesite="lax",
        max_age=token_service.get_access_token_expiry_seconds(),
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=is_production,
        samesite="lax",
        max_age=7 * 24 * 60 * 60,  # 7 days in seconds
    )

    return RegisterUserResponse(
        user_id=str(user.id),
        email=str(user.email),
        username=str(user.username),
        created_at=user.created_at,
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=token_service.get_access_token_expiry_seconds(),
    )


@router.get(
    "/check-username-exists",
    response_model=CheckUsernameResponse,
    summary="Check if username exists",
    description="Check if a username is already taken",
)
async def check_username_exists(
    username: str,
    user_repository: IUserRepository = Depends(get_user_repository),
):
    """Check if a username is already taken."""
    from application.use_cases.auth.check_username import CheckUsernameUseCase

    use_case = CheckUsernameUseCase(user_repository)
    exists = await use_case.execute(username)
    return CheckUsernameResponse(exists=exists)


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="Login user",
    description="Authenticate user and receive JWT tokens",
)
async def login(
    response: Response,
    request: LoginRequest,
    user_repository: IUserRepository = Depends(get_user_repository),
    session_repository: ISessionRepository = Depends(get_session_repository),
    password_service: IPasswordService = Depends(get_password_service),
    token_service: ITokenService = Depends(get_token_service),
    event_bus: EventBus = Depends(get_event_bus_dependency),
):
    """Authenticate user and create a session."""
    from application.use_cases.auth.login_user import LoginUserUseCase

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

    # Set HTTP-only cookies for tokens
    # Note: In dev with different ports (5173 vs 8000), cookies won't work cross-origin
    # This is mainly for production or when frontend/backend are on same origin
    is_production = settings.environment == "production"

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=is_production,  # Only secure in production (HTTPS)
        samesite="lax",  # Always lax - stricter but works without secure flag
        max_age=token_service.get_access_token_expiry_seconds(),
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=is_production,  # Only secure in production (HTTPS)
        samesite="lax",  # Always lax
        max_age=7 * 24 * 60 * 60,  # 7 days in seconds
    )

    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=token_service.get_access_token_expiry_seconds(),
        user=UserResponse(
            id=str(user.id),
            email=str(user.email),
            username=str(user.username),
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
    response: Response,
    current_user: User = Depends(get_current_user),
    session_repository: ISessionRepository = Depends(get_session_repository),
    event_bus: EventBus = Depends(get_event_bus_dependency),
):
    """Logout the current user by revoking their session."""
    from application.use_cases.auth.logout_user import LogoutUserUseCase

    use_case = LogoutUserUseCase(session_repository, event_bus)

    # Note: We need to get the session ID from the token
    # For now, we'll revoke all sessions for the user
    # In production, you'd want to get the specific session ID from the request
    await session_repository.revoke_all_for_user(current_user.id)

    # Clear HTTP-only cookies
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")

    return LogoutResponse()


@router.post(
    "/refresh",
    response_model=RefreshTokenResponse,
    summary="Refresh access token",
    description="Get a new access token using a refresh token",
)
async def refresh_token(
    response: Response,
    request: RefreshTokenRequest,
    session_repository: ISessionRepository = Depends(get_session_repository),
    token_service: ITokenService = Depends(get_token_service),
):
    """Refresh the access token using a valid refresh token."""
    from application.use_cases.auth.refresh_token import RefreshTokenUseCase

    use_case = RefreshTokenUseCase(session_repository, token_service)
    access_token = await use_case.execute(request.refresh_token)

    # Update access token cookie
    is_production = settings.environment == "production"

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=is_production,  # Only secure in production (HTTPS)
        samesite="lax",  # Always lax
        max_age=token_service.get_access_token_expiry_seconds(),
    )

    return RefreshTokenResponse(
        access_token=access_token,
        expires_in=token_service.get_access_token_expiry_seconds(),
    )


# Email Verification Endpoints


@router.post("/verify-email", response_model=VerifyEmailResponse)
async def verify_email(
    response: Response,
    request: VerifyEmailRequest,
    user_repository: IUserRepository = Depends(get_user_repository),
    session_repository: ISessionRepository = Depends(get_session_repository),
    verification_repository=Depends(get_email_verification_repository),
    token_service: ITokenService = Depends(get_token_service),
    event_bus: EventBus = Depends(get_event_bus_dependency),
):
    """Verify user email with token and automatically log them in."""
    from application.use_cases.auth.verify_email import VerifyEmailUseCase
    from domain.entities import Session
    from domain.value_objects import Email
    from domain.events import UserLoggedIn
    from datetime import datetime, timezone

    # Verify the email
    use_case = VerifyEmailUseCase(
        user_repository, verification_repository, event_bus
    )
    message, email = await use_case.execute(request.token)

    # Auto-login: Create session and generate tokens
    email_vo = Email(value=email)
    user = await user_repository.find_by_email(email_vo)

    if user:
        # Create new session
        session = Session.create(user_id=user.id)
        session = await session_repository.save(session)

        # Generate tokens
        access_token = token_service.create_access_token(user.id, session.id)
        refresh_token = token_service.create_refresh_token(user.id, session.id)

        # Publish domain event
        event = UserLoggedIn(
            occurred_at=datetime.now(timezone.utc),
            user_id=user.id,
            session_id=session.id,
        )
        await event_bus.publish(event)

        # Set HTTP-only cookies for tokens (same as login endpoint)
        is_production = settings.environment == "production"

        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=is_production,  # Only secure in production (HTTPS)
            samesite="lax",  # Always lax - stricter but works without secure flag
            max_age=token_service.get_access_token_expiry_seconds(),
        )

        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=is_production,
            samesite="lax",
            max_age=7 * 24 * 60 * 60,  # 7 days in seconds
        )

        return VerifyEmailResponse(
            message=message,
            email=email,
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=token_service.get_access_token_expiry_seconds(),
        )

    # Fallback if user not found (shouldn't happen)
    return VerifyEmailResponse(message=message, email=email)


@router.post("/resend-verification", response_model=ResendVerificationResponse)
async def resend_verification(
    request: ResendVerificationRequest,
    user_repository: IUserRepository = Depends(get_user_repository),
    verification_repository=Depends(get_email_verification_repository),
    event_bus: EventBus = Depends(get_event_bus_dependency),
):
    """Resend verification email to user."""
    from application.use_cases.auth.resend_verification import (
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
    from application.use_cases.auth.request_password_reset import (
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
    from application.use_cases.auth.reset_password import ResetPasswordUseCase

    use_case = ResetPasswordUseCase(
        user_repository,
        verification_repository,
        session_repository,
        password_service,
        event_bus,
    )
    await use_case.execute(request.token, request.new_password)

    return ResetPasswordResponse()
