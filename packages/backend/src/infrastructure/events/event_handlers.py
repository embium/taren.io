"""Event handlers for domain events."""

import logging
from datetime import datetime

from domain.events import (
    DomainEvent,
    PasswordChanged,
    SessionExpired,
    UserLoggedIn,
    UserLoggedOut,
    UserRegistered,
)

# Configure logging
logger = logging.getLogger(__name__)


async def log_user_registered(event: UserRegistered) -> None:
    """Log when a new user registers."""
    logger.info(
        f"User registered: {event.email} (ID: {event.user_id}) at {event.occurred_at}"
    )


async def log_user_logged_in(event: UserLoggedIn) -> None:
    """Log when a user logs in."""
    logger.info(
        f"User logged in: {event.user_id} (Session: {event.session_id}) at {event.occurred_at}"
    )


async def log_user_logged_out(event: UserLoggedOut) -> None:
    """Log when a user logs out."""
    logger.info(
        f"User logged out: {event.user_id} (Session: {event.session_id}) at {event.occurred_at}"
    )


async def log_password_changed(event: PasswordChanged) -> None:
    """Log when a user changes their password."""
    logger.warning(
        f"Password changed for user: {event.user_id} at {event.occurred_at}"
    )


async def log_session_expired(event: SessionExpired) -> None:
    """Log when a session expires."""
    logger.info(
        f"Session expired: {event.session_id} (User: {event.user_id}) at {event.occurred_at}"
    )


async def log_generic_event(event: DomainEvent) -> None:
    """Generic event logger for any domain event."""
    event_type = type(event).__name__
    logger.debug(f"Domain event: {event_type} at {event.occurred_at}")


def register_event_handlers(event_bus, email_service=None) -> None:
    """Register all event handlers with the event bus."""
    from infrastructure.events.event_bus import EventBus
    from domain.events import (
        EmailVerificationRequested,
        PasswordResetRequested,
    )
    from infrastructure.events.email_event_handlers import (
        handle_email_verification_requested,
        handle_password_reset_requested,
    )

    # Register specific event handlers
    event_bus.subscribe(UserRegistered, log_user_registered)
    event_bus.subscribe(UserLoggedIn, log_user_logged_in)
    event_bus.subscribe(UserLoggedOut, log_user_logged_out)
    event_bus.subscribe(PasswordChanged, log_password_changed)
    event_bus.subscribe(SessionExpired, log_session_expired)

    # Register email event handlers if email service is provided
    if email_service:

        async def email_verification_handler(
            event: EmailVerificationRequested,
        ) -> None:
            await handle_email_verification_requested(event, email_service)

        async def password_reset_handler(event: PasswordResetRequested) -> None:
            await handle_password_reset_requested(event, email_service)

        event_bus.subscribe(
            EmailVerificationRequested, email_verification_handler
        )
        event_bus.subscribe(PasswordResetRequested, password_reset_handler)

    # You can add more handlers here, e.g.:
    # - Send welcome email on UserRegistered
    # - Track login analytics on UserLoggedIn
    # - Clean up resources on UserLoggedOut
    # - Send security alert on PasswordChanged

    logger.info("Event handlers registered successfully")
