"""API request and response schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


# Authentication Schemas
class RegisterUserRequest(BaseModel):
    """Request schema for user registration."""

    email: EmailStr = Field(..., description="User's email address")
    username: str = Field(
        ...,
        min_length=3,
        max_length=30,
        pattern="^[a-zA-Z0-9_-]+$",
        description="User's username",
    )
    password: str = Field(
        ...,
        min_length=8,
        description="User's password (min 8 characters)",
    )
    name: Optional[str] = Field(
        None, max_length=255, description="User's full name"
    )


class LoginRequest(BaseModel):
    """Request schema for user login."""

    email: EmailStr
    password: str


class RefreshTokenRequest(BaseModel):
    """Request schema for refreshing access token."""

    refresh_token: str


class VerifyEmailRequest(BaseModel):
    """Request schema for email verification."""

    token: str = Field(..., description="Email verification token")


class ResendVerificationRequest(BaseModel):
    """Request schema for resending verification email."""

    email: EmailStr


class ForgotPasswordRequest(BaseModel):
    """Request schema for forgot password."""

    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """Request schema for password reset."""

    token: str = Field(..., description="Password reset token")
    new_password: str = Field(..., min_length=8, description="New password")


# User Schemas
class UserResponse(BaseModel):
    """Response schema for user data."""

    id: str
    email: str
    username: str
    name: Optional[str] = None
    avatar: Optional[str] = None
    created_at: datetime
    is_active: bool
    is_email_verified: bool
    username_last_changed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    """Response schema for user login."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class RegisterUserResponse(BaseModel):
    """Response schema for user registration."""

    user_id: str
    email: str
    username: str
    created_at: datetime
    message: str = "User registered successfully"
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: Optional[int] = None


class RefreshTokenResponse(BaseModel):
    """Response schema for token refresh."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int


class VerifyEmailResponse(BaseModel):
    """Response schema for email verification."""

    message: str
    email: str
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: Optional[int] = None


class CheckUsernameResponse(BaseModel):
    """Response schema for checking username."""

    exists: bool


class UpdateUserRequest(BaseModel):
    """Request schema for updating user profile."""

    name: Optional[str] = Field(None, max_length=255)
    email: Optional[EmailStr] = None
    avatar: Optional[str] = Field(None, description="Base64 encoded image")
    username: Optional[str] = Field(None, max_length=30)


class ChangePasswordRequest(BaseModel):
    """Request schema for changing password."""

    current_password: str
    new_password: str = Field(..., min_length=8, description="New password")


class DeleteAccountRequest(BaseModel):
    """Request schema for deleting account."""

    password: str = Field(..., description="Current password for verification")


# Standard Responses
class MessageResponse(BaseModel):
    """Standard message response."""

    message: str
