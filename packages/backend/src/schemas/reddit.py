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
    quote: str
    link: str

    model_config = {"from_attributes": True}


class PainPointResponse(BaseModel):
    """A single identified pain point with evidence."""

    id: int
    job_id: str
    subreddit: str
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
    # post_count: int
    # comment_count: int
    pain_point_count: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class JobResultsResponse(BaseModel):
    """Full results for a completed job."""

    job_id: str
    status: str
    pain_points: List[PainPointResponse]


class ProfessionResponse(BaseModel):
    """A profession with its generated slug."""

    name: str
    slug: str


class SubredditDetailResponse(BaseModel):
    """Details for a subreddit associated with a profession."""

    name: str
    description: Optional[str] = None
    subscribers: Optional[int] = None
    activity_level: Optional[str] = None

    model_config = {"from_attributes": True}


class ProfessionSubredditsResponse(BaseModel):
    """Response containing a profession and its associated subreddits."""

    success: bool = True
    name: str
    subreddits: List[SubredditDetailResponse]

class SubredditSearchRequest(BaseModel):
    keyword: str
    model: Optional[str] = None

class SubredditSearchJobResponse(BaseModel):
    success: bool
    job_id: str

class SubredditSearchJobStatusResponse(BaseModel):
    status: str
    keyword: Optional[str] = None
    subreddits: Optional[List[SubredditDetailResponse]] = None

