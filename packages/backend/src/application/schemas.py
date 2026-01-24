"""DTOs and Pydantic schemas for API requests and responses."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


# Registration DTOs
class RegisterUserRequest(BaseModel):
    """Request schema for user registration."""

    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(
        ...,
        min_length=8,
        description="User's password (min 8 characters, must include uppercase, lowercase, digit, special char)",
    )
    name: Optional[str] = Field(
        None, max_length=255, description="User's full name (optional)"
    )


class RegisterUserResponse(BaseModel):
    """Response schema for user registration."""

    user_id: str
    email: str
    created_at: datetime
    message: str = "User registered successfully"


# Login DTOs
class LoginRequest(BaseModel):
    """Request schema for user login."""

    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    """Response schema for user login."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds until access token expires
    user: "UserResponse"


# Token Refresh DTOs
class RefreshTokenRequest(BaseModel):
    """Request schema for refreshing access token."""

    refresh_token: str


class RefreshTokenResponse(BaseModel):
    """Response schema for token refresh."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int


# Logout DTOs
class LogoutResponse(BaseModel):
    """Response schema for logout."""

    message: str = "Successfully logged out"


# User DTOs
class UserResponse(BaseModel):
    """Response schema for user data."""

    id: str
    email: str
    name: Optional[str] = None
    avatar: Optional[str] = None
    created_at: datetime
    is_active: bool
    is_email_verified: bool


class UpdateUserRequest(BaseModel):
    """Request schema for updating user profile."""

    name: Optional[str] = Field(None, max_length=255)
    email: Optional[EmailStr] = None
    avatar: Optional[str] = Field(None, description="Base64 encoded image")


# Password Reset DTOs
class ChangePasswordRequest(BaseModel):
    """Request schema for changing password."""

    current_password: str
    new_password: str = Field(
        ...,
        min_length=8,
        description="New password (min 8 characters, must include uppercase, lowercase, digit, special char)",
    )


class ChangePasswordResponse(BaseModel):
    """Response schema for password change."""

    message: str = "Password changed successfully"


# Email Verification DTOs
class VerifyEmailRequest(BaseModel):
    """Request schema for email verification."""

    token: str = Field(..., description="Email verification token")


class VerifyEmailResponse(BaseModel):
    """Response schema for email verification."""

    message: str
    email: str


class ResendVerificationRequest(BaseModel):
    """Request schema for resending verification email."""

    email: EmailStr


class ResendVerificationResponse(BaseModel):
    """Response schema for resending verification."""

    message: str = "Verification email sent. Please check your inbox."


class ForgotPasswordRequest(BaseModel):
    """Request schema for forgot password."""

    email: EmailStr


class ForgotPasswordResponse(BaseModel):
    """Response schema for forgot password."""

    message: str = "If that email exists, a password reset link has been sent."


class ResetPasswordRequest(BaseModel):
    """Request schema for password reset."""

    token: str = Field(..., description="Password reset token")
    new_password: str = Field(
        ...,
        min_length=8,
        description="New password (min 8 characters, must include uppercase, lowercase, digit, special char)",
    )


class ResetPasswordResponse(BaseModel):
    """Response schema for password reset."""

    message: str = "Password has been reset successfully"


class AddEmailRequest(BaseModel):
    """Request schema for adding additional email."""

    email: EmailStr = Field(..., description="New email address to add")


class AddEmailResponse(BaseModel):
    """Response schema for adding additional email."""

    message: str = "Verification email sent to the new address"


class VerifyAdditionalEmailRequest(BaseModel):
    """Request schema for verifying additional email."""

    token: str = Field(..., description="Additional email verification token")


class VerifyAdditionalEmailResponse(BaseModel):
    """Response schema for verifying additional email."""

    message: str
    email: str


# Error Response
class ErrorResponse(BaseModel):
    """Standard error response schema."""

    detail: str
    error_code: Optional[str] = None


# Delete Account DTOs
class DeleteAccountRequest(BaseModel):
    """Request schema for deleting account."""

    password: str = Field(..., description="Current password for verification")


class DeleteAccountResponse(BaseModel):
    """Response schema for account deletion."""

    message: str = "Account successfully deactivated"
