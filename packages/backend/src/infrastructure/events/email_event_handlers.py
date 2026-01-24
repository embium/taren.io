"""Event handlers for email verification."""

import logging

from application.services.email_service import IEmailService
from domain.events import (
    EmailVerificationRequested,
    PasswordResetRequested,
)

logger = logging.getLogger(__name__)


async def handle_email_verification_requested(
    event: EmailVerificationRequested,
    email_service: IEmailService,
) -> None:
    """Handle email verification requested event by sending verification email."""
    try:
        logger.info(
            f"Sending verification email to {event.email} (type: {event.verification_type})"
        )

        if event.verification_type == "registration":
            await email_service.send_verification_email(
                email=str(event.email),
                verification_token=event.verification_token,
            )
        elif event.verification_type == "additional_email":
            await email_service.send_additional_email_verification(
                email=str(event.email),
                verification_token=event.verification_token,
            )
        else:
            logger.warning(
                f"Unknown verification type: {event.verification_type}"
            )

        logger.info(f"Successfully sent verification email to {event.email}")
    except Exception as e:
        logger.error(f"Failed to send verification email to {event.email}: {e}")
        # Don't raise - we don't want to fail user registration if email fails


async def handle_password_reset_requested(
    event: PasswordResetRequested,
    email_service: IEmailService,
) -> None:
    """Handle password reset requested event by sending reset email."""
    try:
        logger.info(f"Sending password reset email to {event.email}")

        await email_service.send_password_reset_email(
            email=str(event.email),
            reset_token=event.reset_token,
        )

        logger.info(f"Successfully sent password reset email to {event.email}")
    except Exception as e:
        logger.error(
            f"Failed to send password reset email to {event.email}: {e}"
        )
        # Don't raise - we don't want to fail the request if email fails
