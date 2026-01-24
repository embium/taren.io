"""Global error handlers for FastAPI."""

from fastapi import Request, status
from fastapi.responses import JSONResponse

from domain.exceptions import (
    DomainException,
    InvalidCredentialsException,
    InvalidEmailException,
    InvalidPasswordException,
    InvalidTokenException,
    SessionExpiredException,
    SessionNotFoundException,
    UserAlreadyExistsException,
    UserNotFoundException,
)


def register_error_handlers(app):
    """Register all error handlers with the FastAPI app."""

    @app.exception_handler(UserAlreadyExistsException)
    async def user_already_exists_handler(
        request: Request, exc: UserAlreadyExistsException
    ):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "detail": exc.message,
                "error_code": "USER_ALREADY_EXISTS",
            },
        )

    @app.exception_handler(InvalidCredentialsException)
    async def invalid_credentials_handler(
        request: Request, exc: InvalidCredentialsException
    ):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "detail": exc.message,
                "error_code": "INVALID_CREDENTIALS",
            },
        )

    @app.exception_handler(InvalidEmailException)
    async def invalid_email_handler(
        request: Request, exc: InvalidEmailException
    ):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": exc.message, "error_code": "INVALID_EMAIL"},
        )

    @app.exception_handler(InvalidPasswordException)
    async def invalid_password_handler(
        request: Request, exc: InvalidPasswordException
    ):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": exc.message, "error_code": "INVALID_PASSWORD"},
        )

    @app.exception_handler(SessionExpiredException)
    async def session_expired_handler(
        request: Request, exc: SessionExpiredException
    ):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": exc.message, "error_code": "SESSION_EXPIRED"},
        )

    @app.exception_handler(SessionNotFoundException)
    async def session_not_found_handler(
        request: Request, exc: SessionNotFoundException
    ):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": exc.message, "error_code": "SESSION_NOT_FOUND"},
        )

    @app.exception_handler(UserNotFoundException)
    async def user_not_found_handler(
        request: Request, exc: UserNotFoundException
    ):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": exc.message, "error_code": "USER_NOT_FOUND"},
        )

    @app.exception_handler(InvalidTokenException)
    async def invalid_token_handler(
        request: Request, exc: InvalidTokenException
    ):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": exc.message, "error_code": "INVALID_TOKEN"},
        )

    @app.exception_handler(DomainException)
    async def domain_exception_handler(request: Request, exc: DomainException):
        """Catch-all handler for any unhandled domain exceptions."""
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": exc.message, "error_code": "DOMAIN_ERROR"},
        )
