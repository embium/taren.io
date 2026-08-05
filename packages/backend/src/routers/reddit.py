"""Reddit analysis router — job management and results retrieval."""

import asyncio
import logging
from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from core.rate_limit import limiter

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
from core.queue import get_redis_pool

router = APIRouter(prefix="/reddit", tags=["Reddit Analysis"])
logger = logging.getLogger(__name__)

# Plan limits table — single source of truth used by both /usage and /jobs
PLAN_LIMITS: dict[str, dict] = {
    "Starter": {"daily_scans": 10, "max_subreddits": 3, "max_posts": 15},
    "Professional": {
        "daily_scans": None,
        "max_subreddits": 10,
        "max_posts": 50,
    },
}


# ---------------------------------------------------------------------------
# GET /reddit/usage  — plan limits + today's scan count
# ---------------------------------------------------------------------------


@router.get("/usage", summary="Get current plan limits and today's scan usage")
async def get_usage(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Return the user's plan limits and how many scans they have run today."""
    tier = current_user.subscription_tier or ""
    plan = PLAN_LIMITS.get(tier, {})

    scans_today = 0
    if plan.get("daily_scans") is not None:
        today_utc = datetime.now(timezone.utc).date()
        day_start = datetime(
            today_utc.year, today_utc.month, today_utc.day, tzinfo=timezone.utc
        )
        count_result = await db.execute(
            select(func.count())
            .select_from(RedditJob)
            .where(
                RedditJob.user_id == current_user.id,
                RedditJob.created_at >= day_start,
            )
        )
        scans_today = count_result.scalar() or 0

    return {
        "tier": tier,
        "daily_scans": plan.get("daily_scans"),  # None = unlimited
        "max_subreddits": plan.get("max_subreddits"),
        "max_posts": plan.get("max_posts"),
        "scans_today": scans_today,
        "scans_remaining": (
            max(0, plan["daily_scans"] - scans_today)
            if plan.get("daily_scans") is not None
            else None  # None = unlimited
        ),
    }


# ---------------------------------------------------------------------------
# POST /reddit/jobs  — create + enqueue a new job
# ---------------------------------------------------------------------------


@router.post(
    "/jobs",
    response_model=JobResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Start a new Reddit scrape + analysis job",
)
@limiter.limit("5/minute")
async def create_job(
    request: Request,
    job_data: CreateJobRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> JobResponse:
    """Create a job record and immediately launch the background scraper."""

    # -----------------------------------------------------------------------
    # Plan limits
    # -----------------------------------------------------------------------
    tier = current_user.subscription_tier
    if tier not in PLAN_LIMITS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You must have an active Starter or Professional subscription to run scans.",
        )

    plan = PLAN_LIMITS[tier]

    # Enforce daily scan limit (Starter only)
    if plan["daily_scans"] is not None:
        today_utc = datetime.now(timezone.utc).date()
        day_start = datetime(
            today_utc.year, today_utc.month, today_utc.day, tzinfo=timezone.utc
        )
        count_result = await db.execute(
            select(func.count())
            .select_from(RedditJob)
            .where(
                RedditJob.user_id == current_user.id,
                RedditJob.created_at >= day_start,
            )
        )
        scans_today = count_result.scalar() or 0
        if scans_today >= plan["daily_scans"]:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=(
                    f"Daily scan limit reached ({plan['daily_scans']}/day on {tier}). "
                    "Upgrade to Professional for unlimited scans."
                ),
            )

    limit_per_job = min(plan["max_posts"], job_data.scrape_limit)
    max_subreddits = plan["max_subreddits"]

    # Normalise subreddits (strip r/ prefix and whitespace)
    subreddits = [
        s.strip().lstrip("r/").strip() for s in job_data.subreddits if s.strip()
    ]
    if not subreddits:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="At least one subreddit is required.",
        )

    subreddits = subreddits[:max_subreddits]

    job = RedditJob(
        user_id=current_user.id,
        subreddits=",".join(subreddits),
        scrape_limit=limit_per_job,
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
    redis_pool = get_redis_pool()
    await redis_pool.enqueue_job(
        "run_reddit_job",
        job_id=job_id,
        subreddit_list=subreddits,
        scrape_limit=job_data.scrape_limit,
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
            target_audience=(
                str(pp.target_audience) if pp.target_audience else ""
            ),
            created_at=pp.created_at,
            evidence=[
                EvidenceResponse(
                    id=ev.id,
                    comment_id=ev.comment_id,
                    quote=ev.quote,
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
