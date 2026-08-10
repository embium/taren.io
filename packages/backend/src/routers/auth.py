"""Authentication router."""

import urllib.parse

from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.responses import RedirectResponse
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.security import token_service
from core.config import settings
from schemas.auth import (
    CheckUsernameResponse,
    ForgotPasswordRequest,
    LoginRequest,
    LoginResponse,
    MessageResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
    RegisterUserRequest,
    RegisterUserResponse,
    ResendVerificationRequest,
    ResetPasswordRequest,
    VerifyEmailRequest,
    VerifyEmailResponse,
)
from services import auth_service
from services.email_service import EmailService

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Create email service instance
email_service = EmailService()


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    response: Response,
    request: RegisterUserRequest,
    db: AsyncSession = Depends(get_db),
) -> RegisterUserResponse:
    """Register a new user account and automatically log them in."""
    result = await auth_service.register_user(db, request, email_service)

    # Set cookies for auto-login
    if result.access_token:
        response.set_cookie(
            key="access_token",
            value=result.access_token,
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=result.expires_in or 900,
        )
    if result.refresh_token:
        response.set_cookie(
            key="refresh_token",
            value=result.refresh_token,
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=7 * 24 * 60 * 60,  # 7 days
        )

    return result


@router.get("/username/{username}/exists")
async def check_username_exists(
    username: str,
    db: AsyncSession = Depends(get_db),
) -> CheckUsernameResponse:
    """Check if a username is already taken."""
    exists = await auth_service.check_username_exists(db, username)
    return CheckUsernameResponse(exists=exists)


@router.post("/login")
async def login(
    response: Response,
    request: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> LoginResponse:
    """Authenticate user and create a session."""
    result = await auth_service.login_user(db, request)

    # Set cookies
    response.set_cookie(
        key="access_token",
        value=result.access_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=result.expires_in,
    )
    response.set_cookie(
        key="refresh_token",
        value=result.refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=7 * 24 * 60 * 60,
    )

    return result


@router.post("/logout")
async def logout(
    response: Response,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    """Logout the current user by revoking their session."""
    # Get access token from cookies
    access_token = request.cookies.get("access_token")

    if access_token:
        try:
            # Decode token to get session ID
            payload = token_service.decode_access_token(access_token)
            session_id = payload.get("session_id")

            if session_id:
                await auth_service.logout_user(db, session_id)
        except JWTError:
            pass  # Token invalid, but we still clear cookies

    # Clear cookies
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")

    return MessageResponse(message="Successfully logged out")


@router.post("/refresh")
async def refresh_token(
    response: Response,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> RefreshTokenResponse:
    """Refresh the access token using a valid refresh token from cookies."""
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token missing",
        )

    result = await auth_service.refresh_token(db, refresh_token)

    # Set new access token cookie
    response.set_cookie(
        key="access_token",
        value=result.access_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=result.expires_in,
    )

    return result


# Email Verification Endpoints


@router.post("/verify")
async def verify_email(
    response: Response,
    request: VerifyEmailRequest,
    db: AsyncSession = Depends(get_db),
) -> VerifyEmailResponse:
    """Verify user email with token and automatically log them in."""
    result = await auth_service.verify_email(db, request)

    # Set cookies for auto-login
    if result.access_token:
        response.set_cookie(
            key="access_token",
            value=result.access_token,
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=result.expires_in,
        )
    if result.refresh_token:
        response.set_cookie(
            key="refresh_token",
            value=result.refresh_token,
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=7 * 24 * 60 * 60,
        )

    return result


@router.post("/resend-verification")
async def resend_verification(
    request: ResendVerificationRequest,
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    """Resend verification email to user."""
    await auth_service.resend_verification(db, request, email_service)
    return MessageResponse(
        message="Verification email sent. Please check your inbox."
    )


@router.post("/forgot-password")
async def forgot_password(
    request: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    """Request password reset email."""
    await auth_service.forgot_password(db, request, email_service)
    return MessageResponse(
        message="If that email exists, a password reset link has been sent."
    )


@router.post("/reset-password")
async def reset_password(
    request: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    """Reset password with verification token."""
    await auth_service.reset_password(db, request)
    return MessageResponse(message="Password has been reset successfully")


@router.get("/google")
async def google_oauth_redirect() -> RedirectResponse:
    """Redirect user to Google OAuth consent screen."""
    params = urllib.parse.urlencode({
        "client_id": settings.google_client_id,
        "redirect_uri": settings.google_redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "select_account",
    })
    google_auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{params}"
    return RedirectResponse(url=google_auth_url)


@router.get("/google/callback")
async def google_oauth_callback(
    response: Response,
    code: str,
    db: AsyncSession = Depends(get_db),
) -> RedirectResponse:
    """Handle Google OAuth callback: exchange code, set cookies, redirect to frontend."""
    access_token, refresh_token, expires_in = await auth_service.google_oauth_login(
        db, code
    )

    redirect = RedirectResponse(url=f"{settings.frontend_url}/callback")
    redirect.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,  # Set True in production
        samesite="lax",
        max_age=expires_in,
    )
    redirect.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,  # Set True in production
        samesite="lax",
        max_age=7 * 24 * 60 * 60,
    )
    return redirect
