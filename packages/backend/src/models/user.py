"""User model with business logic."""

from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base


class User(Base):
    """User model with integrated business logic."""

    __tablename__ = "users"

    # Fields
    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    username: Mapped[str] = mapped_column(
        String(30), unique=True, nullable=False, index=True
    )
    name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    avatar: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )
    is_email_verified: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    username_last_changed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    sessions: Mapped[list["Session"]] = relationship(
        "Session", back_populates="user", cascade="all, delete-orphan"
    )
    email_verifications: Mapped[list["EmailVerification"]] = relationship(
        "EmailVerification", back_populates="user", cascade="all, delete-orphan"
    )

    def __init__(
        self,
        email: str,
        username: str,
        password_hash: str,
        name: Optional[str] = None,
        avatar: Optional[str] = None,
        id: Optional[str] = None,
        **kwargs,
    ):
        """Initialize user with required fields."""
        super().__init__(
            id=id or str(uuid4()),
            email=email,
            username=username,
            password_hash=password_hash,
            name=name,
            avatar=avatar,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            is_active=True,
            is_email_verified=False,
            **kwargs,
        )

    # Business methods
    def verify_email(self) -> None:
        """Mark user email as verified."""
        self.is_email_verified = True
        self.updated_at = datetime.now(timezone.utc)

    def deactivate(self) -> None:
        """Deactivate the user account."""
        self.is_active = False
        self.updated_at = datetime.now(timezone.utc)

    def activate(self) -> None:
        """Activate the user account."""
        self.is_active = True
        self.updated_at = datetime.now(timezone.utc)

    def update_password(self, new_password_hash: str) -> None:
        """Update user password."""
        self.password_hash = new_password_hash
        self.updated_at = datetime.now(timezone.utc)

    def update_profile(
        self,
        name: Optional[str] = None,
        email: Optional[str] = None,
        avatar: Optional[str] = None,
        username: Optional[str] = None,
    ) -> None:
        """Update user profile information."""
        if name is not None:
            self.name = name
        if email is not None:
            self.email = email
        if avatar is not None:
            self.avatar = avatar
        if username is not None and username != self.username:
            # Only update timestamp if username is actually changing
            self.username = username
            self.username_last_changed_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)

    def can_change_username(self) -> bool:
        """Check if user can change username (30-day restriction)."""
        if not self.username_last_changed_at:
            return True
        days_since_change = (
            datetime.now(timezone.utc) - self.username_last_changed_at
        ).days
        return days_since_change >= 30

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, username={self.username})>"


class Session(Base):
    """Session model for managing authentication sessions."""

    __tablename__ = "sessions"

    # Fields
    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True)
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    is_revoked: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="sessions")

    def __init__(
        self,
        user_id: str,
        expiry_days: int = 7,
        id: Optional[str] = None,
        **kwargs,
    ):
        """Initialize session with expiration time."""
        now = datetime.now(timezone.utc)
        super().__init__(
            id=id or str(uuid4()),
            user_id=user_id,
            created_at=now,
            expires_at=now + timedelta(days=expiry_days),
            is_revoked=False,
            **kwargs,
        )

    # Business methods
    def is_valid(self) -> bool:
        """Check if session is valid (not expired and not revoked)."""
        return (
            not self.is_revoked and datetime.now(timezone.utc) < self.expires_at
        )

    def is_expired(self) -> bool:
        """Check if session has expired."""
        return datetime.now(timezone.utc) >= self.expires_at

    def revoke(self) -> None:
        """Revoke the session (logout)."""
        self.is_revoked = True

    def refresh(self, expiry_days: int = 7) -> None:
        """Extend session expiration time."""
        if self.is_valid():
            self.expires_at = datetime.now(timezone.utc) + timedelta(
                days=expiry_days
            )

    def __repr__(self) -> str:
        return f"<Session(id={self.id}, user_id={self.user_id}, valid={self.is_valid()})>"


class EmailVerification(Base):
    """Email verification model for managing verification tokens."""

    __tablename__ = "email_verifications"

    # Fields
    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True)
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    token: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True, index=True
    )
    verification_type: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    is_used: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User", back_populates="email_verifications"
    )

    def __init__(
        self,
        user_id: str,
        email: str,
        token: str,
        verification_type: str,
        expiry_hours: int = 24,
        id: Optional[str] = None,
        **kwargs,
    ):
        """Initialize email verification with expiration time."""
        now = datetime.now(timezone.utc)
        super().__init__(
            id=id or str(uuid4()),
            user_id=user_id,
            email=email,
            token=token,
            verification_type=verification_type,
            created_at=now,
            expires_at=now + timedelta(hours=expiry_hours),
            is_used=False,
            **kwargs,
        )

    # Business methods
    def is_valid(self) -> bool:
        """Check if verification token is valid (not expired and not used)."""
        return not self.is_used and datetime.now(timezone.utc) < self.expires_at

    def is_expired(self) -> bool:
        """Check if verification token has expired."""
        return datetime.now(timezone.utc) >= self.expires_at

    def mark_as_used(self) -> None:
        """Mark the verification token as used."""
        self.is_used = True

    def __repr__(self) -> str:
        return f"<EmailVerification(id={self.id}, email={self.email}, type={self.verification_type}, valid={self.is_valid()})>"
