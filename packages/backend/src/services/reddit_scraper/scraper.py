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

from core.config import settings

from .client import BlockedError, MaxRetriesExceeded


from .client import RedditClient

logger = logging.getLogger(__name__)

_REDDIT_BASE = "https://www.reddit.com/"
_MORE_CHILDREN_URL = "https://www.reddit.com/api/morechildren"


class RedditScraper:
    """
    Orchestrates subreddit and comment scraping.
    """

    # ----------------------------------------------------------------- public

    def scrape_subreddit(
        self,
        subreddit: str,
        limit: int,
        sorting_type: str = "hot",
    ) -> list[dict]:
        """Scrape the /new listing of subreddit and return up to limit posts."""

        after_token = None
        remaining_limit = limit
        posts: list[dict] = []

        logger.info("Scraping r/%s (limit=%d) …", subreddit, limit)

        while remaining_limit > 0:
            current_limit = min(remaining_limit, 100)
            if sorting_type == "hot":
                url = f"{_REDDIT_BASE}/r/{subreddit}.json?limit={current_limit}"
            elif sorting_type == "new":
                url = f"{_REDDIT_BASE}/r/{subreddit}/new.json?limit={current_limit}"
            elif sorting_type == "rising":
                url = f"{_REDDIT_BASE}/r/{subreddit}/rising.json?limit={current_limit}"
            elif sorting_type == "top":
                url = f"{_REDDIT_BASE}/r/{subreddit}/top.json?limit={current_limit}"
            elif sorting_type == "controversial":
                url = f"{_REDDIT_BASE}/r/{subreddit}/controversial.json?limit={current_limit}"
            else:
                url = f"{_REDDIT_BASE}/r/{subreddit}.json?limit={current_limit}"

            if after_token:
                url += f"&after={after_token}"

            new_posts = []
            html = ""

            for _ in range(3):
                try:
                    client = RedditClient()
                    html = client.get(url)
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
                except Exception:
                    pass

                if not html:
                    logger.warning(
                        "r/%s: empty listing response — aborting", subreddit
                    )
                    break

                try:
                    data = json.loads(html)
                    dist = data.get("data", {}).get("dist", 0)
                    new_posts = data.get("data", {}).get("children", [])
                    posts.extend(new_posts)
                    after_token = data.get("data", {}).get("after")

                    if dist == 0:
                        logger.info(
                            "r/%s: no posts found on page (dist==0)", subreddit
                        )
                        break

                    if new_posts:
                        break

                except Exception as exc:  # noqa: BLE001
                    logger.error(
                        "r/%s: failed to parse listing HTML: %s", subreddit, exc
                    )

            if not new_posts:
                logger.info(
                    "r/%s: no posts found on page (no posts)", subreddit
                )
                break

            logger.debug(
                "r/%s: %d posts collected so far", subreddit, len(posts)
            )

            remaining_limit -= len(posts)

        fetched = posts[:limit]
        logger.info("r/%s: fetched %d posts", subreddit, len(fetched))
        return fetched

    def scrape_post_with_comments(
        self,
        subreddit: str,
        id: str,
    ) -> tuple[dict | None, list[dict]]:
        """Fetch the comments page for post and return (post_data, comments)."""
        subreddit = subreddit.lower()
        url = f"{_REDDIT_BASE}/r/{subreddit}/comments/{id}.json"

        logger.info("Fetching comments: %s", url)

        html = ""
        comments = []
        post_data = {}

        for _ in range(3):
            try:
                client = RedditClient()
                html = client.get(url)
            except MaxRetriesExceeded as exc:
                logger.error(
                    "Max retries fetching comments for post %s: %s",
                    id,
                    exc,
                )
                return None, []
            except Exception as exc:
                logger.error(
                    "Failed to fetch comments for post %s: %s",
                    id,
                    exc,
                )

            if not html:
                logger.warning("Empty HTML for comments page of post %s", id)
                continue

            try:
                response_data = json.loads(html)
                post_data = (
                    response_data[0]
                    .get("data", {})
                    .get("children", [])[0]["data"]
                )
                comments = response_data[1].get("data", {}).get("children", [])

                if post_data is None:
                    logger.warning(
                        "parse_post_from_comments_page returned None for post %s",
                        id,
                    )
                    continue

                break

            except Exception as exc:  # noqa: BLE001
                logger.error(
                    "Failed to parse comments page for post %s: %s",
                    id,
                    exc,
                )
                continue

        logger.debug(
            "Post %s: parsed %d top-level comments",
            id,
            len(comments),
        )

        all_comments = []

        def recursive_collect(node):
            kind = node.get("kind")
            data = node.get("data", {})
            all_comments.append(data)

            if kind == "t1":
                replies = data.get("replies")
                if isinstance(replies, dict):
                    children = replies.get("data", {}).get("children", [])
                    for child in children:
                        recursive_collect(child)

            return data

        for comment in comments:
            recursive_collect(comment)

        logger.info(
            "Post %s: %d total comments after pagination",
            id,
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
                client = RedditClient()
                raw = client.post(_MORE_CHILDREN_URL, data=form_data)
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

            logger.debug(
                "Post %s: +%d comments from morechildren (%d total)",
                post["post_id"],
                len(new_comments),
                len(all_comments),
            )

            stub = result.get("stub")

        return all_comments
