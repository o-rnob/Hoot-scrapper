"""Utility functions for rate limiting and robots.txt checking."""

import logging
import time
from typing import Optional
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import requests

from hootscrapper.config import REQUEST_DELAY, TIMEOUT, USER_AGENT

logger = logging.getLogger(__name__)


class RateLimiter:
    """Simple rate limiter using time delays."""

    def __init__(self, delay: float = REQUEST_DELAY):
        """Initialize rate limiter with delay in seconds."""
        self.delay = delay
        self.last_request_time: Optional[float] = None

    def wait(self) -> None:
        """Wait if necessary to maintain rate limit."""
        if self.last_request_time is not None:
            elapsed = time.time() - self.last_request_time
            if elapsed < self.delay:
                sleep_time = self.delay - elapsed
                logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f}s")
                time.sleep(sleep_time)
        self.last_request_time = time.time()


def check_robots_txt(url: str, user_agent: str = USER_AGENT) -> bool:
    """
    Check if scraping is allowed by robots.txt.

    Args:
        url: The URL to check
        user_agent: User agent string to check against

    Returns:
        True if allowed, False if disallowed
    """
    parsed = urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"

    try:
        rp = RobotFileParser()
        rp.set_url(robots_url)
        rp.read()

        can_fetch = rp.can_fetch(user_agent, url)
        logger.info(f"robots.txt check for {url}: {'ALLOWED' if can_fetch else 'BLOCKED'}")
        return can_fetch
    except Exception as e:
        logger.warning(f"Could not check robots.txt for {url}: {e}. Assuming allowed.")
        return True


def make_request(
    url: str, rate_limiter: RateLimiter, headers: Optional[dict] = None
) -> requests.Response:
    """
    Make a rate-limited HTTP request.

    Args:
        url: URL to fetch
        rate_limiter: RateLimiter instance
        headers: Optional headers dict

    Returns:
        Response object

    Raises:
        requests.RequestException on failure
    """
    if headers is None:
        headers = {}

    headers.setdefault("User-Agent", USER_AGENT)

    rate_limiter.wait()
    logger.debug(f"Fetching: {url}")

    response = requests.get(url, headers=headers, timeout=TIMEOUT)
    response.raise_for_status()

    return response
