"""Application exceptions."""

from fastapi import HTTPException, status


class AuthError(HTTPException):
    """Base authentication error."""

    def __init__(
        self, detail: str, status_code: int = status.HTTP_401_UNAUTHORIZED
    ):
        super().__init__(status_code=status_code, detail=detail)


class InvalidCredentialsError(AuthError):
    """Invalid username or password."""

    def __init__(self):
        super().__init__(detail="Invalid email or password")


class InvalidProviderError(AuthError):
    """Invalid OAuth provider."""

    def __init__(self):
        super().__init__(detail="User signed up with a different provider")


class UserNotFoundError(AuthError):
    """User not found."""

    def __init__(self):
        super().__init__(
            detail="User not found", status_code=status.HTTP_404_NOT_FOUND
        )


class EmailAlreadyExistsError(HTTPException):
    """Email already registered."""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )


class UsernameAlreadyCurrentError(HTTPException):
    """Username already current."""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already current",
        )


class UsernameAlreadyExistsError(HTTPException):
    """Username already taken."""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already taken",
        )


class InvalidTokenError(AuthError):
    """Invalid or expired token."""

    def __init__(self):
        super().__init__(detail="Invalid or expired token")


class EmailNotVerifiedError(AuthError):
    """Email not verified."""

    def __init__(self):
        super().__init__(
            detail="Please verify your email before logging in",
            status_code=status.HTTP_403_FORBIDDEN,
        )


class AccountInactiveError(AuthError):
    """Account is inactive."""

    def __init__(self):
        super().__init__(
            detail="Account is inactive",
            status_code=status.HTTP_403_FORBIDDEN,
        )


class UsernameChangeRestrictedError(HTTPException):
    """Username change restricted (30 day limit)."""

    def __init__(self, days_remaining: int):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"You can only change your username once every 30 days. Please wait {days_remaining} more days.",
        )
