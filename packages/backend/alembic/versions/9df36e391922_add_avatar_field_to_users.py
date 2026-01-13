"""add_avatar_field_to_users

Revision ID: 9df36e391922
Revises: a1b2c3d4e5f6
Create Date: 2026-01-11 19:54:02.956724

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9df36e391922"
down_revision: Union[str, Sequence[str], None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add avatar column to users table for base64 encoded images."""
    op.add_column(
        "users",
        sa.Column("avatar", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    """Remove avatar column from users table."""
    op.drop_column("users", "avatar")
