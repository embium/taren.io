"""
scraper/metrics.py
------------------
Lightweight, in-process metrics collector for a single scrape run.
Call :meth:`ScraperMetrics.report` at the end of the run to print a
structured summary to the log.
"""

from __future__ import annotations

import logging
import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import DefaultDict

logger = logging.getLogger(__name__)


@dataclass
class ScraperMetrics:
    """Accumulates counters and latency data for one scrape run."""

    # --------------------------------------------------------- Post counters
    posts_scraped: int = 0
    posts_failed: int = 0
    posts_saved: int = 0

    # ------------------------------------------------------ Comment counters
    comments_scraped: int = 0
    comments_failed: int = 0
    comments_saved: int = 0

    # ------------------------------------------------------- HTTP diagnostics
    requests_total: int = 0
    requests_succeeded: int = 0
    blocks_encountered: int = 0
    retries_total: int = 0

    http_errors: DefaultDict[int, int] = field(
        default_factory=lambda: defaultdict(int)
    )
    """Counts HTTP errors keyed by status code (e.g. {403: 2, 429: 1})."""

    # ---------------------------------------------------------------- Timings
    _run_start: float = field(default_factory=time.monotonic, repr=False)
    _latencies_s: list[float] = field(default_factory=list, repr=False)

    # ----------------------------------------- Per-subreddit breakdown
    per_subreddit: DefaultDict[str, dict] = field(
        default_factory=lambda: defaultdict(
            lambda: {
                "posts": 0,
                "comments": 0,
                "failed": 0,
            }
        )
    )

    # ---------------------------------------------------------------- Helpers
    def record_request(
        self, latency_s: float, status_code: int | None = None
    ) -> None:
        """Record a completed HTTP request (successful or not)."""
        self.requests_total += 1
        self._latencies_s.append(latency_s)
        if status_code is not None and status_code >= 400:
            self.http_errors[status_code] += 1
        else:
            self.requests_succeeded += 1

    def record_block(self) -> None:
        """Record a request that returned the block sentinel."""
        self.blocks_encountered += 1

    def record_retry(self) -> None:
        """Record that a retry was triggered."""
        self.retries_total += 1

    def record_post_scraped(self, subreddit: str) -> None:
        self.posts_scraped += 1
        self.per_subreddit[subreddit]["posts"] += 1

    def record_post_failed(self, subreddit: str) -> None:
        self.posts_failed += 1
        self.per_subreddit[subreddit]["failed"] += 1

    def record_comment_scraped(self, subreddit: str) -> None:
        self.comments_scraped += 1
        self.per_subreddit[subreddit]["comments"] += 1

    def record_post_saved(self) -> None:
        self.posts_saved += 1

    def record_comment_saved(self) -> None:
        self.comments_saved += 1

    # ----------------------------------------------------------------- Report
    def report(self) -> None:
        """Log a human-readable summary of the completed scrape run."""
        elapsed = time.monotonic() - self._run_start
        avg_latency = (
            sum(self._latencies_s) / len(self._latencies_s)
            if self._latencies_s
            else 0.0
        )
        success_rate = (
            self.requests_succeeded / self.requests_total * 100
            if self.requests_total
            else 0.0
        )

        lines = [
            "",
            "=" * 60,
            "  SCRAPE RUN SUMMARY",
            "=" * 60,
            f"  Elapsed           : {elapsed:.1f}s",
            f"  Requests total    : {self.requests_total}",
            f"  Requests OK       : {self.requests_succeeded}  ({success_rate:.1f}%)",
            f"  Blocks hit        : {self.blocks_encountered}",
            f"  Retries issued    : {self.retries_total}",
            f"  Avg latency       : {avg_latency:.2f}s",
            "-" * 60,
            f"  Posts scraped     : {self.posts_scraped}",
            f"  Posts failed      : {self.posts_failed}",
            f"  Posts saved to DB : {self.posts_saved}",
            f"  Comments scraped  : {self.comments_scraped}",
            f"  Comments failed   : {self.comments_failed}",
            f"  Comments saved    : {self.comments_saved}",
        ]

        if self.http_errors:
            lines.append("-" * 60)
            lines.append("  HTTP error breakdown:")
            for code, count in sorted(self.http_errors.items()):
                lines.append(f"    {code}  →  {count}x")

        if self.per_subreddit:
            lines.append("-" * 60)
            lines.append("  Per-subreddit:")
            for sub, counts in self.per_subreddit.items():
                lines.append(
                    f"    r/{sub:<20}  posts={counts['posts']}  "
                    f"comments={counts['comments']}  failed={counts['failed']}"
                )

        lines.append("=" * 60)
        logger.info("\n".join(lines))
