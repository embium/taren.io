"""
scraper/config.py
-----------------
Central configuration for the Reddit scraper.
All values have sensible defaults and can be overridden via environment variables.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field

from dotenv import load_dotenv

load_dotenv()


@dataclass
class ScraperConfig:
    """Holds every tuneable knob for the scraper, HTTP client, and DB layer."""

    # ------------------------------------------------------------------ Proxy
    proxy_url: str = "http://proxy.proxying.io:8080"
    """Proxy endpoint.  IP-auth assumed — no credentials in URL required."""

    # --------------------------------------------------------- Retry / backoff
    max_retries: int = 5
    """Maximum number of HTTP attempts per request before giving up."""

    base_backoff_s: float = 1.0
    """Base seconds for exponential backoff: wait = base * 2^attempt + jitter."""

    # ------------------------------------------------------- Request settings
    request_timeout_s: int = 30
    """Per-request timeout in seconds."""

    rate_limit_s: float = 1.0
    """Minimum seconds to sleep between outgoing requests (politeness delay)."""

    user_agents_file: str = "user_agents.txt"
    """Path to the plain-text file containing one user-agent per line."""

    subreddits_file: str = "subreddits_aidev.txt"
    """Path to the plain-text file containing one subreddit name per line."""

    # --------------------------------------------------------- Sentinel string
    block_sentinel: str = "You've been blocked by network security."
    """String that indicates Reddit (or a proxy) has blocked the request."""

    # ---------------------------------------------------------------- Database
    db_drop_on_init: bool = True
    """If True, drop and recreate all tables at startup (safe for dev/testing)."""

    # ----------------------------------------------------------------- Class method
    @classmethod
    def from_env(cls) -> "ScraperConfig":
        """
        Build a :class:`ScraperConfig` from environment variables.

        Every env-var is optional; the dataclass default is used when absent.
        """
        return cls(
            proxy_url=os.environ.get(
                "PROXY_URL", "http://proxy.proxying.io:8080"
            ),
            max_retries=int(os.environ.get("MAX_RETRIES", "5")),
            base_backoff_s=float(os.environ.get("BASE_BACKOFF_S", "1.0")),
            request_timeout_s=int(os.environ.get("REQUEST_TIMEOUT_S", "30")),
            rate_limit_s=float(os.environ.get("RATE_LIMIT_S", "1.0")),
            subreddits_file=os.environ.get(
                "SUBREDDITS_FILE", "subreddits_aidev.txt"
            ),
            db_drop_on_init=os.environ.get("DB_DROP_ON_INIT", "true").lower()
            == "true",
        )
