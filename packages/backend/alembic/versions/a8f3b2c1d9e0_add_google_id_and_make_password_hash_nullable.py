"""add google id and make password hash nullable

Revision ID: a8f3b2c1d9e0
Revises: 3523bb7e9b4e
Create Date: 2026-08-02 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a8f3b2c1d9e0'
down_revision = '3523bb7e9b4e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # We leave this empty because the DB is already upgraded (migration was applied but file was lost).
    pass


def downgrade() -> None:
    pass
