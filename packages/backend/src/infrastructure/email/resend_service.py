"""Resend email service implementation."""

import resend
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path

from application.services.email_service import IEmailService
from config.settings import settings


class ResendEmailService(IEmailService):
    """Email service implementation using Resend API."""

    def __init__(self):
        """Initialize Resend email service with API key and template engine."""
        resend.api_key = settings.resend_api_key

        # Set up Jinja2 template environment
        template_dir = Path(__file__).parent / "templates"
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=select_autoescape(["html", "xml"]),
        )

    async def send_verification_email(
        self, email: str, verification_token: str, user_name: str | None = None
    ) -> None:
        """Send email verification email to user."""
        verification_url = (
            f"{settings.frontend_url}/verify?token={verification_token}"
        )

        template = self.jinja_env.get_template("verify_email.html")
        html_content = template.render(
            user_name=user_name or "there",
            verification_url=verification_url,
            app_name=settings.app_name,
        )

        resend.Emails.send(
            {
                "from": f"{settings.email_from_name} <{settings.email_from_address}>",
                "to": [email],
                "subject": f"Verify your {settings.app_name} account",
                "html": html_content,
            }
        )

    async def send_password_reset_email(
        self, email: str, reset_token: str, user_name: str | None = None
    ) -> None:
        """Send password reset email to user."""
        reset_url = (
            f"{settings.frontend_url}/reset-password?token={reset_token}"
        )

        template = self.jinja_env.get_template("reset_password.html")
        html_content = template.render(
            user_name=user_name or "there",
            reset_url=reset_url,
            app_name=settings.app_name,
        )

        resend.Emails.send(
            {
                "from": f"{settings.email_from_name} <{settings.email_from_address}>",
                "to": [email],
                "subject": f"Reset your {settings.app_name} password",
                "html": html_content,
            }
        )

    async def send_additional_email_verification(
        self, email: str, verification_token: str, user_name: str | None = None
    ) -> None:
        """Send verification email for additional email address."""
        verification_url = f"{settings.frontend_url}/settings/verify-email?token={verification_token}"

        template = self.jinja_env.get_template("verify_additional_email.html")
        html_content = template.render(
            user_name=user_name or "there",
            verification_url=verification_url,
            app_name=settings.app_name,
        )

        resend.Emails.send(
            {
                "from": f"{settings.email_from_name} <{settings.email_from_address}>",
                "to": [email],
                "subject": f"Verify your new email address for {settings.app_name}",
                "html": html_content,
            }
        )
