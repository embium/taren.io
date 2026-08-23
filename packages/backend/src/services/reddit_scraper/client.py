"""
scraper/client.py
-----------------
RedditClient — all HTTP operations live here.

Responsibilities
~~~~~~~~~~~~~~~~
* Single ``_get`` / ``_post`` primitives used by all callers
* Exponential backoff with jitter on every failure
* User-agent rotation across requests
* Block-sentinel detection → raises :exc:`BlockedError`
* Rate limiting (politeness sleep between requests)
* Structured logging at DEBUG / WARNING / ERROR
* Records every request outcome to :class:`~scraper.metrics.ScraperMetrics`

No HTML parsing or business logic belongs in this module.
"""

from __future__ import annotations

import itertools
import logging
import random
import time
from typing import TYPE_CHECKING

import curl_cffi
import curl_cffi.requests
from curl_cffi.requests.session import ProxySpec

from core.config import settings

from .config import ScraperConfig

if TYPE_CHECKING:
    from .metrics import ScraperMetrics

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Custom exceptions
# ---------------------------------------------------------------------------


class BlockedError(Exception):
    """Raised when Reddit (or a proxy layer) returns the block sentinel."""


class MaxRetriesExceeded(Exception):
    """Raised when all retry attempts for a request are exhausted."""


# ---------------------------------------------------------------------------
# Client
# ---------------------------------------------------------------------------


class RedditClient:
    """
    Thin HTTP wrapper around ``curl_cffi`` with retry / backoff / rate-limiting.

    Parameters
    ----------
    config:
        :class:`~scraper.config.ScraperConfig` instance carrying all tuneable
        settings (proxy, timeouts, retry counts, etc.).
    metrics:
        :class:`~scraper.metrics.ScraperMetrics` instance to record outcomes.
    """

    _BASE_HEADERS: dict[str, str] = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://reddit.com/",
    }

    def __init__(
        self,
        warming: bool = True,
    ) -> None:
        self.config = ScraperConfig(
            proxy_url=settings.proxy_url,
            max_retries=5,
            base_backoff_s=1.0,
            request_timeout_s=30,
            rate_limit_s=1.0,
        )
        self.proxies: ProxySpec = {
            "https": self.config.proxy_url,
            "http": self.config.proxy_url,
        }

        with open(self.config.user_agents_file, "r") as f:
            user_agents = f.read().splitlines()

        self._ua_cycle = itertools.cycle(user_agents)
        self._last_request_time: float = 0.0
        self.warming = warming

        headers = self._next_headers()
        self.session = curl_cffi.requests.Session(
            headers=headers, proxies=self.proxies, impersonate="firefox"
        )

    # ------------------------------------------------------------------ helpers

    def _next_headers(self) -> dict[str, str]:
        """Return a copy of the base headers with the next user-agent."""
        headers = dict(self._BASE_HEADERS)
        headers["User-Agent"] = next(self._ua_cycle)
        return headers

    def _rate_limit(self) -> None:
        """Sleep long enough to honour the configured rate-limit."""
        elapsed = time.monotonic() - self._last_request_time
        wait = self.config.rate_limit_s - elapsed
        if wait > 0:
            headers = self._next_headers()
            self.session = curl_cffi.requests.Session(
                headers=headers, proxies=self.proxies, impersonate="firefox"
            )
            logger.debug("Rate-limiting: sleeping %.2fs", wait)
            time.sleep(wait)

    def _backoff(self, attempt: int) -> None:
        """Sleep with exponential backoff + random jitter."""
        wait = self.config.base_backoff_s * (2**attempt) + random.uniform(
            0, 0.5
        )
        headers = self._next_headers()
        self.session = curl_cffi.requests.Session(
            headers=headers, proxies=self.proxies, impersonate="firefox"
        )
        logger.debug("Backoff attempt %d: sleeping %.2fs", attempt, wait)
        time.sleep(wait)

    def _decode_response(self, r: curl_cffi.requests.Response) -> str:
        """
        Safely decode the response body.

        Returns an empty string if the body is empty (rather than raising).
        Raises :exc:`BlockedError` if the block sentinel is detected.
        """
        if not r.content:
            logger.warning("Empty response body (status=%s)", r.status_code)
            return ""

        text = r.content.decode("utf-8", errors="replace")

        if self.config.block_sentinel in text:
            logger.warning(
                "Block sentinel detected — status=%s, url=%s",
                r.status_code,
                r.url,
            )

        return text

    # ---------------------------------------------------------------- public API

    def get(self, url: str) -> str | None:
        """
        Perform a GET request with retry / backoff.

        Returns
        -------
        str
            Decoded response body.

        Raises
        ------
        MaxRetriesExceeded
            If all attempts fail.
        """
        return self._request("GET", url)

    def post(self, url: str, data: dict) -> str | None:
        """
        Perform a POST request with retry / backoff.

        Returns
        -------
        str
            Decoded response body.

        Raises
        ------
        MaxRetriesExceeded
            If all attempts fail.
        """
        return self._request("POST", url, data=data)

    # --------------------------------------------------------------- internals

    def _request(
        self, method: str, url: str, data: dict | None = None
    ) -> str | None:
        """
        Core request loop: rate-limit → send → validate → return body.

        On failure: log the error, apply backoff, retry up to
        ``config.max_retries`` times, then raise :exc:`MaxRetriesExceeded`.
        """

        last_exc: Exception = RuntimeError("No attempts made")
        if self.warming:
            r = self.session.get(
                "https://reddit.com/",
            )
            if r.status_code >= 400:
                logger.warning(
                    "HTTP %s for %s %s",
                    r.status_code,
                    "WARMING",
                    "https://reddit.com/",
                )

        try:

            if method == "GET":
                r = self.session.get(
                    url,
                    timeout=self.config.request_timeout_s,
                )
            else:
                r = self.session.post(
                    url,
                    data=data,
                    timeout=self.config.request_timeout_s,
                )

            if r.status_code >= 400:
                logger.warning(
                    "HTTP %s for %s %s",
                    r.status_code,
                    method,
                    url,
                )

            return self._decode_response(r)

        except BlockedError:
            # Re-raise immediately; outer caller decides what to do.
            raise

        except Exception as exc:  # noqa: BLE001
            self._last_request_time = time.monotonic()
            logger.warning(
                "%s %s failed: %s",
                method,
                url,
                exc,
            )
