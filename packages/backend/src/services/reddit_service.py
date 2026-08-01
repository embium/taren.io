"""
services/reddit_service.py
--------------------------
Orchestrates Reddit scraping + LLM analysis as a background task.

Flow:
  1. Update job status → "scraping"
  2. For each subreddit: scrape posts + comments (sync, run in thread executor)
  3. Save posts & comments to DB
  4. Update job status → "analyzing"
  5. For each subreddit: call OpenRouter LLM with analysis prompt
  6. Save pain points + evidence to DB
  7. Update job status → "done" (or "failed" on error)
"""

from __future__ import annotations

import asyncio
import json
import logging
import re
import datetime
from typing import Optional

import httpx
from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from core.config import settings
from models.reddit import (
    RedditJob,
    RedditPost,
    RedditComment,
    RedditPainPoint,
    RedditEvidence,
)
from services.reddit_scraper import (
    RedditClient,
    RedditScraper,
    ScraperConfig,
    ScraperMetrics,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# LLM Analysis helpers
# ---------------------------------------------------------------------------

ANALYSIS_PROMPT_TEMPLATE = """\
You are a market research analyst. Analyze the Reddit comments below from r/{subreddit} \
and identify distinct pain points expressed by users.

For each pain point:
1. Give it a short, descriptive **title** (max 10 words).
2. Assign a **severity** score from 0 to 100 using these guidelines:
   - 80–100: Widespread, high emotional intensity, clear unmet need
   - 60–79: Moderate frequency, real frustration, but workarounds exist
   - 40–59: Niche or low-frequency, mild inconvenience
   - Below 40: Edge case or minor preference
3. List all relevant **evidence** comments. For each, include:
   - **comment_id**: the original comment_id from the data
   - **content**: the original comment text from the data
   - **link**: the full Reddit URL provided in the data

Only include pain points that have at least 2 supporting comments. \
Do not invent or paraphrase evidence quotes — use exact words from the comments.

Return ONLY valid JSON (no markdown fences) in this exact structure:
[
  {{
    "title": "...",
    "severity": 85,
    "evidence": [
      {{
        "comment_id": "...",
        "content": "...",
        "link": "..."
      }}
    ]
  }}
]

--- COMMENTS ---
{comments_json}
"""


def _strip_json_fence(text: str) -> str:
    """Strip Markdown JSON fences from LLM response."""
    match = re.search(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL)
    return match.group(1) if match else text


def _build_reddit_link(subreddit: str, post_id: str, comment_id: str) -> str:
    return f"https://reddit.com/r/{subreddit}/comments/{post_id}/comment/{comment_id}"


async def _call_openrouter(prompt: str) -> str:
    """Call the OpenRouter chat completions API asynchronously."""
    async with httpx.AsyncClient(timeout=120.0) as client:
        resp = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {settings.openrouter_api_key}"},
            json={
                "model": settings.openrouter_model,
                "messages": [{"role": "user", "content": prompt}],
            },
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]


# ---------------------------------------------------------------------------
# DB helpers (async SQLAlchemy)
# ---------------------------------------------------------------------------


async def _update_job_status(
    session_factory: async_sessionmaker,
    job_id: str,
    status: str,
    error_message: Optional[str] = None,
    **counts,
) -> None:
    """Update a job's status in a fresh session."""
    async with session_factory() as session:
        values = {
            "status": status,
            "updated_at": datetime.datetime.now(datetime.timezone.utc),
        }
        if error_message is not None:
            values["error_message"] = error_message
        values.update(counts)
        await session.execute(
            update(RedditJob).where(RedditJob.id == job_id).values(**values)
        )
        await session.commit()


# ---------------------------------------------------------------------------
# Scraping helpers (sync — run in executor)
# ---------------------------------------------------------------------------


def _make_scraper(limit: int) -> "RedditScraper":
    """Create a fresh scraper instance from current settings."""
    config = ScraperConfig(
        proxy_url=settings.proxy_url,
        scrape_limit=limit,
        max_retries=5,
        base_backoff_s=1.0,
        request_timeout_s=30,
        rate_limit_s=1.0,
    )
    metrics = ScraperMetrics()
    client = RedditClient(config, metrics)
    return RedditScraper(client, metrics, config)


def _scrape_listing_sync(subreddit: str, limit: int) -> list[dict]:
    """
    Synchronous: fetch only the subreddit post listing (no comments).
    Returns a list of post stub dicts.
    """
    return _make_scraper(limit).scrape_subreddit(subreddit, limit=limit)


def _scrape_post_comments_sync(post: dict) -> tuple[dict | None, list[dict]]:
    """
    Synchronous: fetch comments for a single post stub.
    Returns (post_data, comments) — post_data is None on failure.
    """
    # Create a fresh scraper per-call so rate limiting starts clean
    scraper = _make_scraper(limit=1)
    return scraper.scrape_post_with_comments(post)


# ---------------------------------------------------------------------------
# Main background task
# ---------------------------------------------------------------------------


async def run_reddit_job(
    job_id: str,
    subreddit_list: list[str],
    scrape_limit: int,
    session_factory: async_sessionmaker,
) -> None:
    """
    Full scrape + analysis pipeline for a Reddit job.
    Called as asyncio.create_task(...).
    """
    logger.info("Job %s: starting (%d subreddits)", job_id, len(subreddit_list))

    try:
        # ------------------------------------------------------------------ scraping
        await _update_job_status(session_factory, job_id, "scraping")

        loop = asyncio.get_event_loop()
        total_posts = 0
        total_comments = 0

        # Map: subreddit → list of comment dicts (for analysis)
        subreddit_comments: dict[str, list[dict]] = {}

        for subreddit in subreddit_list:
            logger.info("Job %s: scraping r/%s", job_id, subreddit)

            # Step 1: fetch post listing (blocking, but fast — just one page of HTML)
            try:
                raw_posts = await loop.run_in_executor(
                    None, _scrape_listing_sync, subreddit, scrape_limit
                )
            except Exception as exc:
                logger.error(
                    "Job %s: listing error for r/%s: %s", job_id, subreddit, exc
                )
                continue

            logger.info(
                "Job %s: r/%s — %d posts to scrape",
                job_id,
                subreddit,
                len(raw_posts),
            )

            sub_comments_for_analysis: list[dict] = []
            seen_comment_ids: set[str] = set()

            # Step 2: scrape each post's comments individually so we can update live counts
            for post_stub in raw_posts:
                try:
                    post_data, comments = await loop.run_in_executor(
                        None, _scrape_post_comments_sync, post_stub
                    )
                except Exception as exc:
                    logger.error(
                        "Job %s: error scraping post %s: %s",
                        job_id,
                        post_stub.get("post_id"),
                        exc,
                    )
                    continue

                if not post_data:
                    continue

                post_id_str = post_data.get("post_id", "")
                post_comments_count = 0

                async with session_factory() as session:
                    # Upsert post — ignore conflicts on (job_id, post_id)
                    post_stmt = (
                        pg_insert(RedditPost)
                        .values(
                            job_id=job_id,
                            post_id=post_id_str,
                            subreddit=subreddit,
                            title=post_data.get("title", ""),
                            author=post_data.get("author") or "[deleted]",
                            content=post_data.get("content") or "",
                            score=int(post_data.get("score", 0) or 0),
                            num_comments=int(
                                post_data.get("num_comments", 0) or 0
                            ),
                            url=post_data.get("url") or "",
                            created_at=post_data.get("created_at", None),
                        )
                        .on_conflict_do_nothing(
                            constraint="uq_reddit_posts_job_post"
                        )
                        .returning(RedditPost.id)
                    )
                    result = await session.execute(post_stmt)
                    returned_id = result.scalar_one_or_none()

                    if returned_id is None:
                        # Row already existed — fetch the existing id
                        existing = await session.execute(
                            select(RedditPost.id).where(
                                RedditPost.job_id == job_id,
                                RedditPost.post_id == post_id_str,
                            )
                        )
                        returned_id = existing.scalar_one()
                    else:
                        total_posts += 1

                    post_db_id = returned_id

                    # Save comments
                    for c in comments:
                        body = c.get("body", "")
                        comment_id_str = c.get("comment_id", "")
                        if not body or not comment_id_str:
                            continue

                        # Skip duplicates seen so far for this subreddit
                        dedup_key = f"{post_db_id}:{comment_id_str}"
                        if dedup_key in seen_comment_ids:
                            continue
                        seen_comment_ids.add(dedup_key)

                        comment_stmt = (
                            pg_insert(RedditComment)
                            .values(
                                post_id=post_db_id,
                                comment_id=comment_id_str,
                                subreddit=subreddit,
                                author=c.get("author") or "[deleted]",
                                content=body,
                                score=int(c.get("score", 0) or 0),
                                parent_comment_id=c.get("parent_comment_id"),
                                created_at=post_data.get("created_at", None),
                            )
                            .on_conflict_do_nothing(
                                constraint="uq_reddit_comments_post_comment"
                            )
                        )
                        await session.execute(comment_stmt)
                        total_comments += 1
                        post_comments_count += 1

                        # Prepare for LLM
                        sub_comments_for_analysis.append(
                            {
                                "comment_id": comment_id_str,
                                "content": body,
                                "subreddit": subreddit,
                                "link": _build_reddit_link(
                                    subreddit,
                                    post_id_str,
                                    comment_id_str,
                                ),
                            }
                        )

                    # Commit this post + its comments immediately
                    await session.commit()

                # Push live counts to the DB after every post so the frontend sees progress
                logger.info(
                    "Job %s: r/%s — saved post %s (%d comments) [total: %d posts, %d comments]",
                    job_id,
                    subreddit,
                    post_id_str,
                    post_comments_count,
                    total_posts,
                    total_comments,
                )
                await _update_job_status(
                    session_factory,
                    job_id,
                    "scraping",
                    post_count=total_posts,
                    comment_count=total_comments,
                )

            subreddit_comments[subreddit] = sub_comments_for_analysis

        # ------------------------------------------------------------------ analyzing
        await _update_job_status(
            session_factory,
            job_id,
            "analyzing",
            post_count=total_posts,
            comment_count=total_comments,
        )

        total_pain_points = 0

        for subreddit, comments_list in subreddit_comments.items():
            if not comments_list:
                logger.info(
                    "Job %s: r/%s has no comments, skipping analysis",
                    job_id,
                    subreddit,
                )
                continue

            logger.info(
                "Job %s: analyzing %d comments from r/%s",
                job_id,
                len(comments_list),
                subreddit,
            )

            prompt = ANALYSIS_PROMPT_TEMPLATE.format(
                subreddit=subreddit,
                comments_json=json.dumps(comments_list, ensure_ascii=False),
            )

            pain_points_raw = []
            for attempt in range(3):
                try:
                    raw = await _call_openrouter(prompt)
                    pain_points_raw = json.loads(_strip_json_fence(raw))
                    break
                except Exception as exc:
                    logger.warning(
                        "Job %s: LLM attempt %d failed for r/%s: %s",
                        job_id,
                        attempt + 1,
                        subreddit,
                        exc,
                    )

            if not pain_points_raw:
                logger.warning(
                    "Job %s: all LLM attempts failed for r/%s",
                    job_id,
                    subreddit,
                )
                continue

            # Save pain points + evidence
            async with session_factory() as session:
                for item in pain_points_raw:
                    pp = RedditPainPoint(
                        job_id=job_id,
                        subreddit=subreddit,
                        title=item.get("title", "Untitled"),
                        description=item.get("description", ""),
                        severity=int(item.get("severity", 0)),
                        target_audience=item.get("target_audience", ""),
                    )
                    session.add(pp)
                    await session.flush()

                    seen_ev_keys = set()
                    for ev in item.get("evidence", []):
                        comment_id = ev.get("comment_id")
                        content = ev.get("content", "")

                        # Deduplicate by comment_id if available, otherwise by exact content match
                        dedup_key = comment_id if comment_id else content
                        if dedup_key in seen_ev_keys:
                            continue
                        if dedup_key:
                            seen_ev_keys.add(dedup_key)

                        evidence = RedditEvidence(
                            pain_point_id=pp.id,
                            comment_id=comment_id,
                            content=content,
                            link=ev.get("link", ""),
                        )
                        session.add(evidence)

                    total_pain_points += 1

                await session.commit()

        # ------------------------------------------------------------------ done
        await _update_job_status(
            session_factory,
            job_id,
            "done",
            post_count=total_posts,
            comment_count=total_comments,
            pain_point_count=total_pain_points,
        )
        logger.info(
            "Job %s: done — %d posts, %d comments, %d pain points",
            job_id,
            total_posts,
            total_comments,
            total_pain_points,
        )

    except Exception as exc:
        logger.error("Job %s: unhandled error: %s", job_id, exc, exc_info=True)
        await _update_job_status(
            session_factory,
            job_id,
            "failed",
            error_message=str(exc),
        )
