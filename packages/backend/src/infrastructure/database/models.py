"""SQLAlchemy ORM models for database tables."""

from datetime import datetime, timezone
from typing import List

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infrastructure.database.connection import Base


class UserModel(Base):
    """SQLAlchemy model for users table."""

    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    avatar: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )
    is_email_verified: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )

    # Relationships
    sessions: Mapped[List["SessionModel"]] = relationship(
        "SessionModel", back_populates="user", cascade="all, delete-orphan"
    )
    email_verifications: Mapped[List["EmailVerificationModel"]] = relationship(
        "EmailVerificationModel",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<UserModel(id={self.id}, email={self.email})>"


class SessionModel(Base):
    """SQLAlchemy model for sessions table."""

    __tablename__ = "sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True)
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now(timezone.utc), nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    is_revoked: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )

    # Relationships
    user: Mapped["UserModel"] = relationship(
        "UserModel", back_populates="sessions"
    )

    def __repr__(self) -> str:
        return f"<SessionModel(id={self.id}, user_id={self.user_id})>"


class EmailVerificationModel(Base):
    """SQLAlchemy model for email_verifications table."""

    __tablename__ = "email_verifications"

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
        DateTime, default=datetime.now(timezone.utc), nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, index=True
    )
    is_used: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )

    # Relationships
    user: Mapped["UserModel"] = relationship(
        "UserModel", back_populates="email_verifications"
    )

    def __repr__(self) -> str:
        return f"<EmailVerificationModel(id={self.id}, email={self.email}, type={self.verification_type})>"
