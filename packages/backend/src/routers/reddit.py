"""Reddit analysis router — job management and results retrieval."""

import asyncio
import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db, AsyncSessionLocal
from core.dependencies import get_current_user
from models.user import User
from models.reddit import RedditJob, RedditPainPoint, RedditEvidence
from schemas.reddit import (
    CreateJobRequest,
    JobResponse,
    JobResultsResponse,
    PainPointResponse,
    EvidenceResponse,
)
from services.reddit_service import run_reddit_job

router = APIRouter(prefix="/reddit", tags=["Reddit Analysis"])
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# POST /reddit/jobs  — create + enqueue a new job
# ---------------------------------------------------------------------------


@router.post(
    "/jobs",
    response_model=JobResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Start a new Reddit scrape + analysis job",
)
async def create_job(
    request: CreateJobRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> JobResponse:
    """Create a job record and immediately launch the background scraper."""

    if current_user.subscription_tier is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You must have a subscription to create a job.",
        )

    # Normalise subreddits (strip r/ prefix and whitespace)
    subreddits = [
        s.strip().lstrip("r/").strip() for s in request.subreddits if s.strip()
    ]
    if not subreddits:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="At least one subreddit is required.",
        )

    job = RedditJob(
        user_id=current_user.id,
        subreddits=",".join(subreddits),
        scrape_limit=request.scrape_limit,
        status="pending",
        post_count=0,
        comment_count=0,
        pain_point_count=0,
    )
    db.add(job)
    await db.flush()
    job_id = job.id
    await db.commit()

    # Fire-and-forget background task
    asyncio.create_task(
        run_reddit_job(
            job_id=job_id,
            subreddit_list=subreddits,
            scrape_limit=request.scrape_limit,
            session_factory=AsyncSessionLocal,
        )
    )

    logger.info(
        "Job %s created for user %s — subreddits: %s",
        job_id,
        current_user.id,
        subreddits,
    )

    # Re-fetch to get server-generated timestamps
    result = await db.execute(select(RedditJob).where(RedditJob.id == job_id))
    job = result.scalar_one()
    return JobResponse.model_validate(job)


# ---------------------------------------------------------------------------
# GET /reddit/jobs  — list all jobs (newest first)
# ---------------------------------------------------------------------------


@router.get(
    "/jobs",
    response_model=List[JobResponse],
    summary="List all Reddit analysis jobs",
)
async def list_jobs(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[JobResponse]:
    """Return all jobs, newest first."""
    result = await db.execute(
        select(RedditJob)
        .where(RedditJob.user_id == current_user.id)
        .order_by(RedditJob.created_at.desc())
    )
    jobs = result.scalars().all()
    return [JobResponse.model_validate(j) for j in jobs]


# ---------------------------------------------------------------------------
# GET /reddit/jobs/{job_id}  — single job detail
# ---------------------------------------------------------------------------


@router.get(
    "/jobs/{job_id}",
    response_model=JobResponse,
    summary="Get a single job's status and counts",
)
async def get_job(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> JobResponse:
    """Get details for a specific job."""
    result = await db.execute(
        select(RedditJob).where(
            RedditJob.user_id == current_user.id, RedditJob.id == job_id
        )
    )
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Job not found."
        )
    return JobResponse.model_validate(job)


# ---------------------------------------------------------------------------
# GET /reddit/jobs/{job_id}/results  — pain points + evidence
# ---------------------------------------------------------------------------


@router.get(
    "/jobs/{job_id}/results",
    response_model=JobResultsResponse,
    summary="Get pain points and evidence for a completed job",
)
async def get_job_results(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> JobResultsResponse:
    """Return all pain points with evidence for a job."""
    # Fetch job
    result = await db.execute(
        select(RedditJob).where(
            RedditJob.user_id == current_user.id, RedditJob.id == job_id
        )
    )
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Job not found."
        )

    # Fetch pain points with evidence eagerly loaded
    pp_result = await db.execute(
        select(RedditPainPoint)
        .where(RedditPainPoint.job_id == job_id)
        .options(selectinload(RedditPainPoint.evidence))
        .order_by(RedditPainPoint.severity.desc())
    )
    pain_points = pp_result.scalars().all()

    pain_point_responses = [
        PainPointResponse(
            id=pp.id,
            job_id=pp.job_id,
            subreddit=pp.subreddit,
            title=pp.title,
            description=pp.description,
            severity=pp.severity,
            target_audience=pp.target_audience,
            created_at=pp.created_at,
            evidence=[
                EvidenceResponse(
                    id=ev.id,
                    comment_id=ev.comment_id,
                    content=ev.content,
                    link=ev.link,
                )
                for ev in pp.evidence
            ],
        )
        for pp in pain_points
    ]

    return JobResultsResponse(
        job_id=job_id,
        status=job.status,
        pain_points=pain_point_responses,
    )
