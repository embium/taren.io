"""Email service interface."""

from abc import ABC, abstractmethod


class IEmailService(ABC):
    """Abstract interface for email service operations."""

    @abstractmethod
    async def send_verification_email(
        self, email: str, verification_token: str, user_name: str | None = None
    ) -> None:
        """Send email verification email to user."""
        pass

    @abstractmethod
    async def send_password_reset_email(
        self, email: str, reset_token: str, user_name: str | None = None
    ) -> None:
        """Send password reset email to user."""
        pass

    @abstractmethod
    async def send_additional_email_verification(
        self, email: str, verification_token: str, user_name: str | None = None
    ) -> None:
        """Send verification email for additional email address."""
        pass
