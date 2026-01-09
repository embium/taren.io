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

    def __init__(self):
        super().__init__("User not found")


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
