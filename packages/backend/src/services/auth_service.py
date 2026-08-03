"""Authentication service - handles all authentication-related business logic."""

from datetime import datetime, timezone
from typing import Optional
import re

import httpx
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.security import (
    generate_verification_token,
    password_service,
    token_service,
)
from core.config import settings
from exceptions import (
    AccountInactiveError,
    EmailAlreadyExistsError,
    EmailNotVerifiedError,
    InvalidCredentialsError,
    InvalidProviderError,
    InvalidTokenError,
    UserNotFoundError,
    UsernameAlreadyExistsError,
)
from models.user import EmailVerification, Session, User
from schemas.auth import (
    ForgotPasswordRequest,
    LoginRequest,
    LoginResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
    RegisterUserRequest,
    RegisterUserResponse,
    ResendVerificationRequest,
    ResetPasswordRequest,
    UserResponse,
    VerifyEmailRequest,
    VerifyEmailResponse,
)


class AuthService:
    """Service for handling authentication operations."""

    async def register_user(
        self, db: AsyncSession, data: RegisterUserRequest, email_service
    ) -> RegisterUserResponse:
        """Register a new user and create session."""
        # Check if email exists
        result = await db.scalar(select(User).where(User.email == data.email))
        if result:
            raise EmailAlreadyExistsError()

        # Check if username exists
        result = await db.scalar(
            select(User).where(User.username == data.username)
        )
        if result:
            raise UsernameAlreadyExistsError()

        # Create user
        user = User(
            email=data.email,
            username=data.username,
            password_hash=password_service.hash_password(data.password),
            name=data.name,
        )
        db.add(user)
        await db.flush()

        # Create email verification
        verification = EmailVerification(
            user_id=user.id,
            email=user.email,
            token=generate_verification_token(),
            verification_type="registration",
        )
        db.add(verification)
        await db.commit()

        # Send verification email
        await email_service.send_verification_email(
            email=user.email,
            verification_token=verification.token,
            user_name=user.name,
        )

        # Create session and tokens to auto-login
        session = Session(user_id=user.id)
        db.add(session)
        await db.commit()

        access_token = token_service.create_access_token(user.id, session.id)
        refresh_token = token_service.create_refresh_token(user.id, session.id)

        return RegisterUserResponse(
            user_id=user.id,
            email=user.email,
            username=user.username,
            created_at=user.created_at,
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=token_service.get_access_token_expiry_seconds(),
        )

    async def login_user(
        self, db: AsyncSession, data: LoginRequest
    ) -> LoginResponse:
        """Authenticate user and create session."""
        # Find user by email
        user = await db.scalar(select(User).where(User.email == data.email))
        if not user:
            raise InvalidCredentialsError()

        if not user.password_hash:
            raise InvalidProviderError()

        # Verify password
        is_valid, _ = password_service.verify_password(
            data.password, user.password_hash
        )
        if not is_valid:
            raise InvalidCredentialsError()

        # Check if account is active
        if not user.is_active:
            raise AccountInactiveError()

        # Create session
        session = Session(user_id=user.id)
        db.add(session)
        await db.commit()

        # Generate tokens
        access_token = token_service.create_access_token(user.id, session.id)
        refresh_token = token_service.create_refresh_token(user.id, session.id)

        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=token_service.get_access_token_expiry_seconds(),
            user=UserResponse.model_validate(user),
        )

    async def logout_user(self, db: AsyncSession, session_id: str) -> None:
        """Logout user by revoking session."""
        session = await db.get(Session, session_id)
        if session:
            session.revoke()
            await db.commit()

    async def refresh_token(
        self, db: AsyncSession, data: RefreshTokenRequest
    ) -> RefreshTokenResponse:
        """Refresh access token using refresh token."""
        try:
            payload = token_service.decode_refresh_token(data.refresh_token)
        except JWTError:
            raise InvalidTokenError()

        session_id = payload.get("session_id")

        # Validate session
        session = await db.get(Session, session_id)
        if not session or not session.is_valid():
            raise InvalidTokenError()

        # Refresh session expiry
        session.refresh()
        await db.commit()

        # Generate new access token
        access_token = token_service.create_access_token(
            session.user_id, session.id
        )

        return RefreshTokenResponse(
            access_token=access_token,
            expires_in=token_service.get_access_token_expiry_seconds(),
        )

    async def verify_email(
        self, db: AsyncSession, data: VerifyEmailRequest
    ) -> VerifyEmailResponse:
        """Verify user email with token."""
        # Find verification by token
        verification = await db.scalar(
            select(EmailVerification).where(
                EmailVerification.token == data.token
            )
        )

        if not verification or not verification.is_valid():
            raise InvalidTokenError()

        # Get user
        user = await db.get(User, verification.user_id)
        if not user:
            raise UserNotFoundError()

        # Mark verification as used
        verification.mark_as_used()

        # Verify user email
        user.verify_email()
        await db.commit()

        # Create session and auto-login
        session = Session(user_id=user.id)
        db.add(session)
        await db.commit()

        access_token = token_service.create_access_token(user.id, session.id)
        refresh_token = token_service.create_refresh_token(user.id, session.id)

        return VerifyEmailResponse(
            message="Email verified successfully",
            email=user.email,
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=token_service.get_access_token_expiry_seconds(),
        )

    async def resend_verification(
        self, db: AsyncSession, data: ResendVerificationRequest, email_service
    ) -> None:
        """Resend verification email."""
        user = await db.scalar(select(User).where(User.email == data.email))
        if not user:
            # Don't reveal if email exists
            return

        if user.is_email_verified:
            # Already verified, nothing to do
            return

        # Delete old verifications
        result = await db.execute(
            select(EmailVerification).where(
                EmailVerification.user_id == user.id,
                EmailVerification.verification_type == "registration",
            )
        )
        old_verifications = result.scalars().all()
        for old in old_verifications:
            await db.delete(old)

        # Create new verification
        verification = EmailVerification(
            user_id=user.id,
            email=user.email,
            token=generate_verification_token(),
            verification_type="registration",
        )
        db.add(verification)
        await db.commit()

        # Send email
        await email_service.send_verification_email(
            email=user.email,
            verification_token=verification.token,
            user_name=user.name,
        )

    async def forgot_password(
        self, db: AsyncSession, data: ForgotPasswordRequest, email_service
    ) -> None:
        """Request password reset email."""
        user = await db.scalar(select(User).where(User.email == data.email))
        if not user:
            # Don't reveal if email exists
            return

        # Delete old password reset tokens
        result = await db.execute(
            select(EmailVerification).where(
                EmailVerification.user_id == user.id,
                EmailVerification.verification_type == "password_reset",
            )
        )
        old_tokens = result.scalars().all()
        for old in old_tokens:
            await db.delete(old)

        # Create password reset token
        verification = EmailVerification(
            user_id=user.id,
            email=user.email,
            token=generate_verification_token(),
            verification_type="password_reset",
            expiry_hours=1,  # Password reset tokens expire quickly
        )
        db.add(verification)
        await db.commit()

        # Send reset email
        await email_service.send_password_reset_email(
            email=user.email,
            reset_token=verification.token,
            user_name=user.name,
        )

    async def reset_password(
        self, db: AsyncSession, data: ResetPasswordRequest
    ) -> None:
        """Reset password with token."""
        # Find verification by token
        verification = await db.scalar(
            select(EmailVerification).where(
                EmailVerification.token == data.token,
                EmailVerification.verification_type == "password_reset",
            )
        )

        if not verification or not verification.is_valid():
            raise InvalidTokenError()

        # Get user
        user = await db.get(User, verification.user_id)
        if not user:
            raise UserNotFoundError()

        # Update password
        user.update_password(password_service.hash_password(data.new_password))

        # Mark token as used
        verification.mark_as_used()

        # Revoke all sessions for security
        result = await db.execute(
            select(Session).where(Session.user_id == user.id)
        )
        sessions = result.scalars().all()
        for session in sessions:
            session.revoke()

        await db.commit()

    async def check_username_exists(
        self, db: AsyncSession, username: str
    ) -> bool:
        """Check if username is already taken."""
        result = await db.scalar(
            select(User.id).where(User.username == username)
        )
        return result is not None

    async def get_user_by_id(
        self, db: AsyncSession, user_id: str
    ) -> Optional[User]:
        """Get user by ID."""
        return await db.get(User, user_id)

    async def get_current_user_from_token(
        self, db: AsyncSession, token: str
    ) -> User:
        """Get current user from access token."""
        try:
            payload = token_service.decode_access_token(token)
        except JWTError:
            raise InvalidTokenError()

        user_id = payload.get("user_id")
        session_id = payload.get("session_id")

        # Validate session
        session = await db.get(Session, session_id)
        if not session or not session.is_valid():
            raise InvalidTokenError()

        # Get user
        user = await db.get(User, user_id)
        if not user:
            raise UserNotFoundError()

        return user

    async def google_oauth_login(
        self, db: AsyncSession, code: str
    ) -> tuple[str, str, int]:
        """Exchange Google auth code for tokens and upsert user. Returns (access_token, refresh_token, expires_in)."""
        async with httpx.AsyncClient() as client:
            # Exchange authorization code for Google tokens
            token_response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "code": code,
                    "client_id": settings.google_client_id,
                    "client_secret": settings.google_client_secret,
                    "redirect_uri": settings.google_redirect_uri,
                    "grant_type": "authorization_code",
                },
            )
            token_response.raise_for_status()
            token_data = token_response.json()

            # Fetch Google user info
            userinfo_response = await client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={
                    "Authorization": f"Bearer {token_data['access_token']}"
                },
            )
            userinfo_response.raise_for_status()
            userinfo = userinfo_response.json()

        google_id: str = userinfo["id"]
        email: str = userinfo["email"]
        name: Optional[str] = userinfo.get("name")
        avatar: Optional[str] = userinfo.get("picture")

        # Find existing user by google_id first, then by email
        user = await db.scalar(select(User).where(User.google_id == google_id))

        if not user:
            # Try to find by email (link existing account)
            user = await db.scalar(select(User).where(User.email == email))

        if user:
            # Update google_id and avatar if needed
            if not user.google_id:
                user.google_id = google_id
            if avatar and not user.avatar:
                user.avatar = avatar
            if name and not user.name:
                user.name = name
            user.is_email_verified = True  # Google emails are pre-verified
            await db.commit()
        else:
            # Create new user — generate a unique username from email
            base_username = email.split("@")[0].lower()
            # Sanitize: keep only alphanumeric/underscore/hyphen, max 28 chars
            base_username = (
                re.sub(r"[^a-z0-9_-]", "", base_username)[:28] or "user"
            )
            username = base_username
            suffix = 1
            while await db.scalar(
                select(User.id).where(User.username == username)
            ):
                username = f"{base_username}{suffix}"
                suffix += 1

            user = User(
                email=email,
                username=username,
                password_hash=None,
                name=name,
                avatar=avatar,
                google_id=google_id,
            )
            user.is_email_verified = True
            db.add(user)
            await db.commit()
            await db.refresh(user)

        # Create session
        session = Session(user_id=user.id)
        db.add(session)
        await db.commit()

        access_token = token_service.create_access_token(user.id, session.id)
        refresh_token = token_service.create_refresh_token(user.id, session.id)
        expires_in = token_service.get_access_token_expiry_seconds()

        return access_token, refresh_token, expires_in


# Global service instance
auth_service = AuthService()
