"""add post_id to RedditEvidence

Revision ID: 41208b6acd9c
Revises: 635f4374a22a
Create Date: 2026-08-04 06:36:21.409388

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '41208b6acd9c'
down_revision: Union[str, Sequence[str], None] = '635f4374a22a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "reddit_evidence",
        sa.Column("post_id", sa.String(length=20), nullable=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("reddit_evidence", "post_id")
