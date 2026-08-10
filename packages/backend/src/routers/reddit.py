"""Reddit analysis router — job management and results retrieval."""

import asyncio
import logging
from datetime import datetime, timezone
from typing import List, cast

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from core.rate_limit import limiter

from core.database import get_db, AsyncSessionLocal
from core.dependencies import get_current_user
from models.user import User
from models.reddit import (
    RedditJob,
    RedditFinding,
    RedditEvidence,
    RedditProfession,
    RedditSubreddit,
)
from schemas.reddit import (
    CreateJobRequest,
    JobResponse,
    JobResultsResponse,
    FindingResponse,
    EvidenceResponse,
    TemplateResponse,
    ProfessionResponse,
    SubredditDetailResponse,
    ProfessionSubredditsResponse,
    SubredditSearchRequest,
    SubredditSearchJobResponse,
    SubredditSearchJobStatusResponse,
)
from core.queue import get_redis_pool
from services.agent_service import run_agent_search
from fastapi.concurrency import run_in_threadpool
from core.config import settings
from core.templates import TEMPLATES

router = APIRouter(prefix="/reddit", tags=["Reddit Analysis"])
logger = logging.getLogger(__name__)

# Plan limits table — single source of truth used by both /usage and /jobs
PLAN_LIMITS: dict[str, dict] = {
    "Starter": {"daily_scans": 10, "max_subreddits": 3, "max_posts": 15},
    "Professional": {
        "daily_scans": None,
        "max_subreddits": 10,
        "max_posts": 100,
    },
}


def require_subscription(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.subscription_tier not in PLAN_LIMITS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You must have an active subscription to access this feature.",
        )
    return current_user


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
# GET /reddit/templates  — get available analysis templates
# ---------------------------------------------------------------------------


@router.get(
    "/templates",
    response_model=List[TemplateResponse],
    summary="Get available analysis templates",
)
async def get_templates(
    current_user: User = Depends(require_subscription),
) -> List[TemplateResponse]:
    """Return all pre-built analysis templates."""
    return [
        TemplateResponse(
            id=t.id,
            name=t.name,
            description=t.description,
        )
        for t in TEMPLATES
    ]


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
    current_user: User = Depends(require_subscription),
    db: AsyncSession = Depends(get_db),
) -> JobResponse:
    """Create a job record and immediately launch the background scraper."""

    # -----------------------------------------------------------------------
    # Plan limits
    # -----------------------------------------------------------------------
    tier = current_user.subscription_tier
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
        analysis_type=job_data.analysis_type,
        template_id=job_data.template_id,
        custom_objective=job_data.custom_objective,
        sorting_type=job_data.sorting_type,
        post_count=0,
        comment_count=0,
        finding_count=0,
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
        analysis_type=job_data.analysis_type,
        template_id=job_data.template_id,
        custom_objective=job_data.custom_objective,
        sorting_type=job_data.sorting_type,
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
    current_user: User = Depends(require_subscription),
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
    current_user: User = Depends(require_subscription),
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
# GET /reddit/jobs/{job_id}/results  — finding + evidence
# ---------------------------------------------------------------------------


@router.get(
    "/jobs/{job_id}/results",
    response_model=JobResultsResponse,
    summary="Get findings and evidence for a completed job",
)
async def get_job_results(
    job_id: str,
    current_user: User = Depends(require_subscription),
    db: AsyncSession = Depends(get_db),
) -> JobResultsResponse:
    """Return all findings with evidence for a job."""
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

    # Fetch findings with evidence eagerly loaded
    finding_result = await db.execute(
        select(RedditFinding)
        .where(RedditFinding.job_id == job_id)
        .options(selectinload(RedditFinding.evidence))
        .order_by(RedditFinding.relevance_score.desc())
    )
    findings = finding_result.scalars().all()

    is_starter = (
        not current_user.subscription_tier
        or current_user.subscription_tier == "Starter"
    )

    finding_responses = [
        FindingResponse(
            id=f.id,
            job_id=str(f.job_id),
            subreddit=str(f.subreddit),
            title=str(f.title),
            description=str(f.description),
            relevance_score=f.relevance_score,
            context=(str(f.context) if f.context else ""),
            created_at=cast(datetime, f.created_at),
            evidence=[
                EvidenceResponse(
                    id=ev.id,
                    comment_id=ev.comment_id,
                    quote=ev.quote,
                    link=ev.link,
                )
                for ev in (f.evidence[:10] if is_starter else f.evidence)
            ],
        )
        for f in findings
    ]

    return JobResultsResponse(
        job_id=job_id,
        status=str(job.status),
        findings=finding_responses,
    )


# ---------------------------------------------------------------------------
# GET /reddit/professions  — list professions
# ---------------------------------------------------------------------------


@router.get(
    "/professions",
    response_model=List[ProfessionResponse],
    summary="List all discovered professions",
)
async def list_professions(
    current_user: User = Depends(require_subscription),
    db: AsyncSession = Depends(get_db),
) -> List[ProfessionResponse]:
    """Return all professions with generated slugs."""
    result = await db.execute(
        select(RedditProfession).order_by(RedditProfession.name.asc())
    )
    professions = result.scalars().all()

    return [
        ProfessionResponse(
            name=str(p.name),
            slug=p.name.lower().replace(" ", "-").replace("/", "-"),
        )
        for p in professions
    ]


# ---------------------------------------------------------------------------
# GET /reddit/professions/{slug}/subreddits  — list subreddits for profession
# ---------------------------------------------------------------------------


@router.get(
    "/professions/{slug}/subreddits",
    response_model=ProfessionSubredditsResponse,
    summary="Get subreddits associated with a specific profession",
)
async def get_profession_subreddits(
    slug: str,
    current_user: User = Depends(require_subscription),
    db: AsyncSession = Depends(get_db),
) -> ProfessionSubredditsResponse:
    """Return subreddits for a profession by its generated slug."""
    result = await db.execute(
        select(RedditProfession).options(
            selectinload(RedditProfession.subreddits)
        )
    )
    professions = result.scalars().all()

    target_prof = None
    for p in professions:
        p_slug = p.name.lower().replace(" ", "-").replace("/", "-")
        if p_slug == slug:
            target_prof = p
            break

    if not target_prof:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profession not found.",
        )

    return ProfessionSubredditsResponse(
        success=True,
        name=str(target_prof.name),
        subreddits=[
            SubredditDetailResponse.model_validate(sub)
            for sub in target_prof.subreddits
        ],
    )


# ---------------------------------------------------------------------------
# POST /reddit/search-subreddits  — AI search for subreddits
# ---------------------------------------------------------------------------


@router.post(
    "/search-subreddits",
    response_model=SubredditSearchJobResponse,
    summary="Search for subreddits using AI based on a keyword",
)
async def search_subreddits(
    request: SubredditSearchRequest,
    current_user: User = Depends(require_subscription),
) -> SubredditSearchJobResponse:
    """Use AI Agent to find subreddits related to a keyword in the background."""
    if not request.keyword or not request.keyword.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Keyword is required.",
        )

    try:
        redis_pool = get_redis_pool()
        job = await redis_pool.enqueue_job(
            "run_agent_search_task",
            request.keyword,
            settings.openrouter_keywords_model,
        )
        if job:
            return SubredditSearchJobResponse(
                success=True,
                job_id=job.job_id,
            )
        return SubredditSearchJobResponse(success=False, job_id="")
    except Exception as e:
        logger.error(f"AI search enqueue failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI search enqueue failed: {str(e)}",
        )


@router.get(
    "/search-subreddits/{job_id}",
    response_model=SubredditSearchJobStatusResponse,
    summary="Check status of an AI subreddit search job",
)
async def get_search_subreddits_status(
    job_id: str,
    current_user: User = Depends(require_subscription),
) -> SubredditSearchJobStatusResponse:
    from arq.jobs import Job, JobStatus

    redis_pool = get_redis_pool()
    job = Job(job_id, redis_pool)

    try:
        status_val = await job.status()
        if status_val == JobStatus.complete:
            result = await job.result()
            return SubredditSearchJobStatusResponse(
                status="complete",
                subreddits=[SubredditDetailResponse(**sub) for sub in result],
            )
        elif status_val in (
            JobStatus.in_progress,
            JobStatus.queued,
            JobStatus.deferred,
        ):
            return SubredditSearchJobStatusResponse(
                status="pending",
            )
        elif status_val == JobStatus.not_found:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found or expired.",
            )
        else:
            return SubredditSearchJobStatusResponse(
                status="failed",
            )
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        logger.error(f"Error checking job status for {job_id}: {e}")
        return SubredditSearchJobStatusResponse(
            status="failed",
        )
