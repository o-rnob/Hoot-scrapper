"""SEC EDGAR filings scraper."""

import logging
import re
from dataclasses import dataclass
from datetime import datetime
from typing import List

from bs4 import BeautifulSoup

from hootscrapper.config import SEC_BASE_URL, SEC_SEARCH_URL
from hootscrapper.utils import RateLimiter, check_robots_txt, make_request

logger = logging.getLogger(__name__)


@dataclass
class Filing:
    """Represents an SEC filing."""

    cik: str
    company_name: str
    filing_type: str
    filing_date: str
    accession_number: str
    document_url: str
    scraped_at: str


class SECEdgarScraper:
    """Scraper for SEC EDGAR recent filings."""

    def __init__(self, delay: float = 0.5):
        """Initialize scraper with rate limiter."""
        self.rate_limiter = RateLimiter(delay=delay)
        self.base_url = SEC_BASE_URL

    def scrape(self, limit: int = 100) -> List[Filing]:
        """
        Scrape recent SEC filings.

        Args:
            limit: Maximum number of filings to scrape

        Returns:
            List of Filing objects
        """
        logger.info(f"Starting SEC EDGAR scrape (limit={limit})")

        # Check robots.txt
        if not check_robots_txt(SEC_SEARCH_URL):
            logger.error("Scraping blocked by robots.txt")
            return []

        # Fetch the recent filings page
        try:
            response = make_request(SEC_SEARCH_URL, self.rate_limiter)
            soup = BeautifulSoup(response.content, "lxml")

            filings = self._parse_filings_table(soup, limit)
            logger.info(f"Successfully scraped {len(filings)} filings")

            return filings

        except Exception as e:
            logger.error(f"Failed to scrape SEC EDGAR: {e}")
            return []

    def _parse_filings_table(self, soup: BeautifulSoup, limit: int) -> List[Filing]:
        """Parse the filings table from SEC page."""
        filings = []
        scraped_at = datetime.utcnow().isoformat()

        # Find the table with recent filings
        table = soup.find("table", {"class": "tableFile2"})
        if not table:
            logger.warning("Could not find filings table")
            return filings

        rows = table.find_all("tr")[1:]  # Skip header

        for row in rows[:limit]:
            try:
                cols = row.find_all("td")
                if len(cols) < 5:
                    continue

                filing_type = cols[0].get_text(strip=True)
                company_name = cols[1].get_text(strip=True)
                cik_link = cols[1].find("a")
                filing_date = cols[3].get_text(strip=True)

                # Extract CIK from link
                cik = ""
                if cik_link and "CIK" in cik_link.get("href", ""):
                    cik_match = re.search(r"CIK=(\d+)", cik_link["href"])
                    if cik_match:
                        cik = cik_match.group(1).lstrip("0")

                # Get document link
                doc_link = cols[1].find("a")
                document_url = ""
                if doc_link:
                    href = doc_link.get("href", "")
                    if href:
                        document_url = self.base_url + href if href.startswith("/") else href

                # Extract accession number from URL
                accession_number = ""
                if document_url:
                    acc_match = re.search(r"accession-number=([0-9-]+)", document_url)
                    if acc_match:
                        accession_number = acc_match.group(1)

                filing = Filing(
                    cik=cik,
                    company_name=company_name,
                    filing_type=filing_type,
                    filing_date=filing_date,
                    accession_number=accession_number,
                    document_url=document_url,
                    scraped_at=scraped_at,
                )

                filings.append(filing)
                logger.debug(f"Parsed filing: {filing.company_name} - {filing.filing_type}")

            except Exception as e:
                logger.warning(f"Failed to parse row: {e}")
                continue

        return filings
