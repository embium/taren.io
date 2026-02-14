"""Schemas package."""

from schemas.auth import (
    ChangePasswordRequest,
    CheckUsernameResponse,
    DeleteAccountRequest,
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
    UpdateUserRequest,
    UserResponse,
    VerifyEmailRequest,
    VerifyEmailResponse,
)

__all__ = [
    # Auth
    "RegisterUserRequest",
    "RegisterUserResponse",
    "LoginRequest",
    "LoginResponse",
    "RefreshTokenRequest",
    "RefreshTokenResponse",
    "VerifyEmailRequest",
    "VerifyEmailResponse",
    "ResendVerificationRequest",
    "ForgotPasswordRequest",
    "ResetPasswordRequest",
    "CheckUsernameResponse",
    # User
    "UserResponse",
    "UpdateUserRequest",
    "ChangePasswordRequest",
    "DeleteAccountRequest",
    # Common
    "MessageResponse",
]
