"""Domain-specific exceptions for the authentication system."""


class DomainException(Exception):
    """Base exception for all domain-level errors."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class UserAlreadyExistsException(DomainException):
    """Raised when attempting to register a user with an existing email."""

    def __init__(self, email: str):
        super().__init__(f"User with email '{email}' already exists")


class InvalidCredentialsException(DomainException):
    """Raised when login credentials are invalid."""

    def __init__(self):
        super().__init__("Invalid email or password")


class EmailNotVerifiedException(DomainException):
    """Raised when user tries to login without verifying email."""

    def __init__(self):
        super().__init__(
            "Email address not verified. Please check your email for verification link."
        )


class InvalidVerificationTokenException(DomainException):
    """Raised when verification token is invalid."""

    def __init__(self):
        super().__init__("Invalid verification token")


class ExpiredVerificationTokenException(DomainException):
    """Raised when verification token has expired."""

    def __init__(self):
        super().__init__(
            "Verification token has expired. Please request a new one."
        )


class SessionExpiredException(DomainException):
    """Raised when a session has expired."""

    def __init__(self):
        super().__init__("Session has expired")


class SessionNotFoundException(DomainException):
    """Raised when a session is not found."""

    def __init__(self):
        super().__init__("Session not found")


class UserNotFoundException(DomainException):
    """Raised when a user is not found."""

    def __init__(self, email: str):
        super().__init__(f"User with email '{email}' not found")


class InvalidEmailException(DomainException):
    """Raised when email format is invalid."""

    def __init__(self, email: str):
        super().__init__(f"Invalid email format: '{email}'")


class InvalidPasswordException(DomainException):
    """Raised when password doesn't meet requirements."""

    def __init__(self, reason: str):
        super().__init__(f"Invalid password: {reason}")


class InvalidTokenException(DomainException):
    """Raised when a token is invalid or expired."""

    def __init__(self):
        super().__init__("Invalid or expired token")
