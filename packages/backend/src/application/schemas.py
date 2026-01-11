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
    created_at: datetime
    is_active: bool


class UpdateUserRequest(BaseModel):
    """Request schema for updating user profile."""

    email: Optional[EmailStr] = None


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


# Error Response
class ErrorResponse(BaseModel):
    """Standard error response schema."""

    detail: str
    error_code: Optional[str] = None
