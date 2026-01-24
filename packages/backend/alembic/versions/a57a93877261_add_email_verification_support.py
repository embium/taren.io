"""add_email_verification_support

Revision ID: a57a93877261
Revises: a1b2c3d4e5f6
Create Date: 2026-01-14 13:26:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a57a93877261"
down_revision: Union[str, None] = "9df36e391922"  # Points to add_avatar_field
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add email verification support to users and create email_verifications table."""
    # Add is_email_verified column to users table
    op.add_column(
        "users",
        sa.Column(
            "is_email_verified",
            sa.Boolean(),
            nullable=False,
            server_default="false",
        ),
    )

    # Update existing users to have verified emails (grandfathering)
    op.execute("UPDATE users SET is_email_verified = true")

    # Remove server default after setting existing rows
    op.alter_column("users", "is_email_verified", server_default=None)

    # Create email_verifications table
    op.create_table(
        "email_verifications",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("token", sa.String(length=255), nullable=False),
        sa.Column("verification_type", sa.String(length=50), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column(
            "is_used", sa.Boolean(), nullable=False, server_default="false"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )

    # Create indexes for email_verifications
    op.create_index(
        op.f("ix_email_verifications_id"),
        "email_verifications",
        ["id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_email_verifications_user_id"),
        "email_verifications",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_email_verifications_email"),
        "email_verifications",
        ["email"],
        unique=False,
    )
    op.create_index(
        op.f("ix_email_verifications_token"),
        "email_verifications",
        ["token"],
        unique=True,
    )
    op.create_index(
        op.f("ix_email_verifications_verification_type"),
        "email_verifications",
        ["verification_type"],
        unique=False,
    )
    op.create_index(
        op.f("ix_email_verifications_expires_at"),
        "email_verifications",
        ["expires_at"],
        unique=False,
    )


def downgrade() -> None:
    """Remove email verification support."""
    # Drop email_verifications table and its indexes
    op.drop_index(
        op.f("ix_email_verifications_expires_at"),
        table_name="email_verifications",
    )
    op.drop_index(
        op.f("ix_email_verifications_verification_type"),
        table_name="email_verifications",
    )
    op.drop_index(
        op.f("ix_email_verifications_token"), table_name="email_verifications"
    )
    op.drop_index(
        op.f("ix_email_verifications_email"), table_name="email_verifications"
    )
    op.drop_index(
        op.f("ix_email_verifications_user_id"), table_name="email_verifications"
    )
    op.drop_index(
        op.f("ix_email_verifications_id"), table_name="email_verifications"
    )
    op.drop_table("email_verifications")

    # Remove is_email_verified column from users
    op.drop_column("users", "is_email_verified")
