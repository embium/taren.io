"""Add user name field

Revision ID: a1b2c3d4e5f6
Revises: 0eab2c87f95b
Create Date: 2026-01-10 11:30:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "0eab2c87f95b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add name column to users table."""
    op.add_column(
        "users",
        sa.Column("name", sa.String(length=255), nullable=True),
    )


def downgrade() -> None:
    """Remove name column from users table."""
    op.drop_column("users", "name")
