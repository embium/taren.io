"""Hybrid analysis

Revision ID: 96ed3a57e025
Revises: c859c289394a
Create Date: 2026-08-08 08:53:22.079365

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '96ed3a57e025'
down_revision: Union[str, Sequence[str], None] = 'c859c289394a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Rename table
    op.rename_table('reddit_pain_points', 'reddit_findings')
    
    # Rename indexes
    op.execute("ALTER INDEX IF EXISTS ix_reddit_pain_points_job_id RENAME TO ix_reddit_findings_job_id")
    op.execute("ALTER INDEX IF EXISTS ix_reddit_pain_points_subreddit RENAME TO ix_reddit_findings_subreddit")
    
    # Rename columns in reddit_findings
    op.alter_column('reddit_findings', 'severity', new_column_name='relevance_score')
    op.alter_column('reddit_findings', 'target_audience', new_column_name='context')
    
    # Rename columns in reddit_evidence
    op.alter_column('reddit_evidence', 'pain_point_id', new_column_name='finding_id')
    op.execute("ALTER INDEX IF EXISTS ix_reddit_evidence_pain_point_id RENAME TO ix_reddit_evidence_finding_id")
    
    # Add columns to reddit_jobs
    op.add_column('reddit_jobs', sa.Column('analysis_type', sa.String(length=20), server_default='template', nullable=False))
    op.add_column('reddit_jobs', sa.Column('template_id', sa.String(length=50), nullable=True))
    op.add_column('reddit_jobs', sa.Column('custom_objective', sa.Text(), nullable=True))
    
    # Rename pain_point_count to finding_count
    op.alter_column('reddit_jobs', 'pain_point_count', new_column_name='finding_count')


def downgrade() -> None:
    """Downgrade schema."""
    # Reverse finding_count to pain_point_count
    op.alter_column('reddit_jobs', 'finding_count', new_column_name='pain_point_count')
    
    # Remove columns from reddit_jobs
    op.drop_column('reddit_jobs', 'custom_objective')
    op.drop_column('reddit_jobs', 'template_id')
    op.drop_column('reddit_jobs', 'analysis_type')
    
    # Rename columns in reddit_evidence back
    op.execute("ALTER INDEX IF EXISTS ix_reddit_evidence_finding_id RENAME TO ix_reddit_evidence_pain_point_id")
    op.alter_column('reddit_evidence', 'finding_id', new_column_name='pain_point_id')
    
    # Rename columns in reddit_findings back
    op.alter_column('reddit_findings', 'context', new_column_name='target_audience')
    op.alter_column('reddit_findings', 'relevance_score', new_column_name='severity')
    
    # Rename indexes back
    op.execute("ALTER INDEX IF EXISTS ix_reddit_findings_subreddit RENAME TO ix_reddit_pain_points_subreddit")
    op.execute("ALTER INDEX IF EXISTS ix_reddit_findings_job_id RENAME TO ix_reddit_pain_points_job_id")
    
    # Rename table back
    op.rename_table('reddit_findings', 'reddit_pain_points')
