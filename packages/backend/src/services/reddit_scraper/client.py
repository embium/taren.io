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

if TYPE_CHECKING:
    from .config import ScraperConfig
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

    with open("user_agents.txt", "r") as f:
        user_agents = f.read().splitlines()

    _BASE_HEADERS: dict[str, str] = {
        "User-Agent": random.choice(user_agents),
        "Accept": (
            "text/html,application/xhtml+xml,application/xml;"
            "q=0.9,image/webp,image/apng,*/*;q=0.8"
        ),
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
        "Cache-Control": "max-age=0",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
    }

    def __init__(
        self, config: "ScraperConfig", metrics: "ScraperMetrics"
    ) -> None:
        self.config = config
        self.metrics = metrics
        self.proxies: ProxySpec = {
            "https": config.proxy_url,
            "http": config.proxy_url,
        }
        self._ua_cycle = itertools.cycle(config.user_agents)
        self._last_request_time: float = 0.0

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
            logger.debug("Rate-limiting: sleeping %.2fs", wait)
            time.sleep(wait)

    def _backoff(self, attempt: int) -> None:
        """Sleep with exponential backoff + random jitter."""
        wait = self.config.base_backoff_s * (2**attempt) + random.uniform(
            0, 0.5
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
            self.metrics.record_block()
            logger.warning(
                "Block sentinel detected — status=%s, url=%s",
                r.status_code,
                r.url,
            )
            raise BlockedError(f"Blocked on {r.url}")

        return text

    # ---------------------------------------------------------------- public API

    def get(self, url: str) -> str:
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

    def post(self, url: str, data: dict) -> str:
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

    def _request(self, method: str, url: str, data: dict | None = None) -> str:
        """
        Core request loop: rate-limit → send → validate → return body.

        On failure: log the error, apply backoff, retry up to
        ``config.max_retries`` times, then raise :exc:`MaxRetriesExceeded`.
        """
        last_exc: Exception = RuntimeError("No attempts made")

        for attempt in range(self.config.max_retries):
            if attempt > 0:
                self.metrics.record_retry()
                self._backoff(attempt - 1)

            self._rate_limit()
            headers = self._next_headers()
            t0 = time.monotonic()

            try:
                if method == "GET":
                    r = curl_cffi.get(
                        url,
                        impersonate="chrome",
                        headers=headers,
                        proxies=self.proxies,
                        timeout=self.config.request_timeout_s,
                    )
                else:
                    r = curl_cffi.post(
                        url,
                        impersonate="chrome",
                        headers=headers,
                        data=data,
                        proxies=self.proxies,
                        timeout=self.config.request_timeout_s,
                    )

                latency = time.monotonic() - t0
                self._last_request_time = time.monotonic()
                self.metrics.record_request(latency, r.status_code)
                logger.debug(
                    "%s %s → %s (%.2fs)", method, url, r.status_code, latency
                )

                if r.status_code >= 400:
                    logger.warning(
                        "HTTP %s for %s %s — retrying (%d/%d)",
                        r.status_code,
                        method,
                        url,
                        attempt + 1,
                        self.config.max_retries,
                    )
                    last_exc = RuntimeError(f"HTTP {r.status_code}")
                    continue

                return self._decode_response(r)

            except BlockedError:
                # Re-raise immediately; outer caller decides what to do.
                raise

            except Exception as exc:  # noqa: BLE001
                latency = time.monotonic() - t0
                self._last_request_time = time.monotonic()
                self.metrics.record_request(latency, None)
                logger.warning(
                    "%s %s failed (attempt %d/%d): %s",
                    method,
                    url,
                    attempt + 1,
                    self.config.max_retries,
                    exc,
                )
                last_exc = exc
                continue

        raise MaxRetriesExceeded(
            f"All {self.config.max_retries} attempts failed for {method} {url}"
        ) from last_exc
