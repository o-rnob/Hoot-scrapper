"""Configuration and constants for Hoot Scrapper."""

import os
from typing import Final

# User agent - REQUIRED by SEC
# SEC requires you identify yourself: https://www.sec.gov/os/webmaster-faq#code-support
USER_AGENT: Final[str] = os.getenv(
    "HOOT_USER_AGENT",
    "HootScrapper/0.1 (Educational Portfolio Project; your.email@example.com)",
)

# Rate limiting - be polite to SEC servers
REQUEST_DELAY: Final[float] = float(os.getenv("HOOT_DELAY", "0.5"))  # seconds between requests
MAX_RETRIES: Final[int] = 3
TIMEOUT: Final[int] = 30  # request timeout in seconds

# SEC EDGAR URLs
SEC_BASE_URL: Final[str] = "https://www.sec.gov"
SEC_DAILY_INDEX_URL: Final[str] = f"{SEC_BASE_URL}/cgi-bin/browse-edgar"
SEC_SEARCH_URL: Final[str] = (
    f"{SEC_BASE_URL}/cgi-bin/browse-edgar?"
    "action=getcurrent&type=&company=&dateb=&owner=exclude&count=100"
)

# Data storage
DEFAULT_DB_PATH: Final[str] = "data/hoot.sqlite"
DEFAULT_CSV_PATH: Final[str] = "data/snapshot.csv"

# Logging
LOG_FORMAT: Final[str] = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_LEVEL: Final[str] = os.getenv("HOOT_LOG_LEVEL", "INFO")
