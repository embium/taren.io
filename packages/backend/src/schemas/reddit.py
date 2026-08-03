"""Pydantic schemas for the Reddit analysis feature."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------


class CreateJobRequest(BaseModel):
    """Request to start a new Reddit scrape + analysis job."""

    subreddits: List[str] = Field(
        ...,
        min_length=1,
        description="List of subreddit names (without r/ prefix)",
    )
    scrape_limit: int = Field(
        default=25,
        ge=1,
        le=200,
        description="Maximum posts to scrape per subreddit",
    )


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------


class EvidenceResponse(BaseModel):
    """A supporting comment snippet for a pain point."""

    id: int
    comment_id: Optional[str] = None
    content: str
    link: str

    model_config = {"from_attributes": True}


class PainPointResponse(BaseModel):
    """A single identified pain point with evidence."""

    id: int
    job_id: str
    subreddits: List[str]
    title: str
    description: str
    severity: int  # 0–100
    target_audience: str
    created_at: datetime
    evidence: List[EvidenceResponse] = []

    model_config = {"from_attributes": True}


class JobResponse(BaseModel):
    """Summary of a Reddit analysis job."""

    id: str
    user_id: str
    subreddits: str  # comma-separated
    scrape_limit: int
    status: str
    error_message: Optional[str] = None
    post_count: int
    comment_count: int
    pain_point_count: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class JobResultsResponse(BaseModel):
    """Full results for a completed job."""

    job_id: str
    status: str
    pain_points: List[PainPointResponse]
