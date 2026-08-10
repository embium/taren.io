"""
scraper/scraper.py  (taren backend edition)
-------------------------------------------
RedditScraper — high-level scraping orchestration.

Identical to new_reddit_analysis/scraper/scraper.py but imports
the parser from the new_reddit_analysis package path via sys.path
injection handled by reddit_scraper_service.py at runtime.
"""

from __future__ import annotations

import json
import logging
import sys
import os
from typing import TYPE_CHECKING

# ---------------------------------------------------------------------------
# Parser import — new_reddit_analysis/parser.py is a sibling package.
# We resolve the path at import time.
# ---------------------------------------------------------------------------

_ANALYSIS_ROOT = os.path.normpath(
    os.path.join(
        os.path.dirname(__file__), "..", "..", "..", "..", "new_reddit_analysis"
    )
)
if _ANALYSIS_ROOT not in sys.path:
    sys.path.insert(0, _ANALYSIS_ROOT)

from .parser import (  # noqa: E402
    extract_modhash,
    parse_comments,
    parse_more_children_response,
    parse_more_children_stub,
    parse_post_from_comments_page,
    parse_posts,
)

from .client import BlockedError, MaxRetriesExceeded

if TYPE_CHECKING:
    from .client import RedditClient
    from .config import ScraperConfig
    from .metrics import ScraperMetrics

logger = logging.getLogger(__name__)

_REDDIT_BASE = "https://old.reddit.com"
_MORE_CHILDREN_URL = "https://old.reddit.com/api/morechildren"


class RedditScraper:
    """
    Orchestrates subreddit and comment scraping.
    """

    def __init__(
        self,
        client: "RedditClient",
        metrics: "ScraperMetrics",
        config: "ScraperConfig",
    ) -> None:
        self.client = client
        self.metrics = metrics
        self.config = config

    # ----------------------------------------------------------------- public

    def scrape_subreddit(
        self,
        subreddit: str,
        limit: int | None = None,
        sorting_type: str = "hot",
    ) -> list[dict]:
        """Scrape the /new listing of subreddit and return up to limit posts."""
        limit = limit if limit is not None else 5
        posts: list[dict] = []
        after: str | None = None

        logger.info("Scraping r/%s (limit=%d) …", subreddit, limit)

        while len(posts) < limit:
            if sorting_type == "hot":
                url = f"{_REDDIT_BASE}/r/{subreddit}/"
            elif sorting_type == "new":
                url = f"{_REDDIT_BASE}/r/{subreddit}/new"
            elif sorting_type == "rising":
                url = f"{_REDDIT_BASE}/r/{subreddit}/rising"
            elif sorting_type == "top":
                url = f"{_REDDIT_BASE}/r/{subreddit}/top"
            elif sorting_type == "controversial":
                url = f"{_REDDIT_BASE}/r/{subreddit}/controversial"
            else:
                url = f"{_REDDIT_BASE}/r/{subreddit}"

            if after:
                remaining = min(25, limit - len(posts))
                url += f"?count={remaining}&after={after}"

            try:
                html = self.client.get(url)
            except BlockedError:
                logger.warning(
                    "r/%s: blocked fetching subreddit listing — aborting subreddit",
                    subreddit,
                )
                break
            except MaxRetriesExceeded as exc:
                logger.error(
                    "r/%s: max retries exceeded fetching listing: %s",
                    subreddit,
                    exc,
                )
                break

            if not html:
                logger.warning(
                    "r/%s: empty listing response — aborting", subreddit
                )
                break

            try:
                new_posts = parse_posts(html)
            except Exception as exc:  # noqa: BLE001
                logger.error(
                    "r/%s: failed to parse listing HTML: %s", subreddit, exc
                )
                break

            if not new_posts:
                logger.info("r/%s: no posts found on page", subreddit)
                self.metrics.record_post_failed(subreddit)
                break

            posts.extend(new_posts)
            after = f"t3_{posts[-1]['post_id']}"
            logger.debug(
                "r/%s: %d posts collected so far", subreddit, len(posts)
            )

        fetched = posts[:limit]
        logger.info("r/%s: fetched %d posts", subreddit, len(fetched))
        for _ in fetched:
            self.metrics.record_post_scraped(subreddit)
        return fetched

    def scrape_post_with_comments(
        self, post: dict
    ) -> tuple[dict | None, list[dict]]:
        """Fetch the comments page for post and return (post_data, comments)."""
        subreddit = post["subreddit"].lower()
        url = f"{_REDDIT_BASE}/r/{subreddit}/comments/{post['post_id']}"
        logger.info("Fetching comments: %s", url)

        html = ""
        comments = []
        post_data = {}
        for _ in range(3):
            try:
                html = self.client.get(url)
            except BlockedError:
                logger.warning(
                    "Blocked on comments page for post %s", post["post_id"]
                )
                self.metrics.record_post_failed(subreddit)
                return None, []
            except MaxRetriesExceeded as exc:
                logger.error(
                    "Max retries fetching comments for post %s: %s",
                    post["post_id"],
                    exc,
                )
                self.metrics.record_post_failed(subreddit)
                return None, []

            if not html:
                logger.warning(
                    "Empty HTML for comments page of post %s", post["post_id"]
                )
                self.metrics.record_post_failed(subreddit)
                return None, []

            try:
                post_data = parse_post_from_comments_page(html)
                if post_data is None:
                    logger.warning(
                        "parse_post_from_comments_page returned None for post %s",
                        post["post_id"],
                    )
                    self.metrics.record_post_failed(subreddit)
                    continue

                comments = parse_comments(html) or []
            except Exception as exc:  # noqa: BLE001
                logger.error(
                    "Failed to parse comments page for post %s: %s",
                    post["post_id"],
                    exc,
                )
                self.metrics.record_post_failed(subreddit)
                return None, []
            break

        for _ in comments:
            self.metrics.record_comment_scraped(subreddit)

        logger.debug(
            "Post %s: parsed %d top-level comments",
            post["post_id"],
            len(comments),
        )

        # Paginate "load more" comments
        all_comments = list(comments)
        stub = parse_more_children_stub(html)

        if stub is not None:
            modhash = extract_modhash(html)
            if modhash:
                all_comments = self._fetch_more_children(
                    post, stub, modhash, all_comments, subreddit
                )

        logger.info(
            "Post %s: %d total comments after pagination",
            post["post_id"],
            len(all_comments),
        )
        return post_data, all_comments

    # --------------------------------------------------------------- internals

    def _fetch_more_children(
        self,
        post: dict,
        initial_stub: dict,
        modhash: str,
        existing_comments: list[dict],
        subreddit: str,
    ) -> list[dict]:
        """Follow the morechildren pagination until no more stubs remain."""
        all_comments = list(existing_comments)
        stub: dict | None = initial_stub

        while stub is not None:
            form_data = {
                "link_id": stub["link_id"],
                "sort": stub["sort"],
                "children": stub["children"],
                "id": stub["id"],
                "limit_children": stub["limit_children"],
                "r": post["subreddit"],
                "uh": modhash,
                "renderstyle": "html",
            }

            try:
                raw = self.client.post(_MORE_CHILDREN_URL, data=form_data)
            except BlockedError:
                logger.warning(
                    "Blocked while loading more children for post %s",
                    post["post_id"],
                )
                break
            except MaxRetriesExceeded as exc:
                logger.error(
                    "Max retries on morechildren for post %s: %s",
                    post["post_id"],
                    exc,
                )
                break

            if not raw:
                logger.warning(
                    "Empty morechildren response for post %s", post["post_id"]
                )
                break

            try:
                json_obj = json.loads(raw)
                result = parse_more_children_response(
                    json_obj, post["subreddit"]
                )
            except json.JSONDecodeError as exc:
                logger.error(
                    "JSONDecodeError on morechildren for post %s: %s",
                    post["post_id"],
                    exc,
                )
                break
            except Exception as exc:  # noqa: BLE001
                logger.error(
                    "Failed to parse morechildren for post %s: %s",
                    post["post_id"],
                    exc,
                )
                break

            new_comments: list[dict] = result.get("comments", [])
            all_comments.extend(new_comments)
            for _ in new_comments:
                self.metrics.record_comment_scraped(subreddit)

            logger.debug(
                "Post %s: +%d comments from morechildren (%d total)",
                post["post_id"],
                len(new_comments),
                len(all_comments),
            )

            stub = result.get("stub")

        return all_comments
