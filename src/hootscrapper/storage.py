"""SQLite storage for filings."""

import csv
import logging
import sqlite3
from pathlib import Path
from typing import List

from hootscrapper.scrapers.sec_edgar import Filing

logger = logging.getLogger(__name__)


class FilingStorage:
    """SQLite storage for SEC filings."""

    def __init__(self, db_path: str):
        """Initialize storage with database path."""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        """Initialize database schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS filings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cik TEXT NOT NULL,
                company_name TEXT NOT NULL,
                filing_type TEXT NOT NULL,
                filing_date TEXT NOT NULL,
                accession_number TEXT NOT NULL UNIQUE,
                document_url TEXT,
                scraped_at TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_cik ON filings(cik)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_filing_type ON filings(filing_type)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_filing_date ON filings(filing_date)
        """)

        conn.commit()
        conn.close()
        logger.info(f"Database initialized: {self.db_path}")

    def insert_filings(self, filings: List[Filing]) -> int:
        """
        Insert filings into database.

        Args:
            filings: List of Filing objects

        Returns:
            Number of filings inserted (skips duplicates)
        """
        if not filings:
            return 0

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        inserted_count = 0
        for filing in filings:
            try:
                cursor.execute(
                    """
                    INSERT INTO filings 
                    (cik, company_name, filing_type, filing_date, accession_number, 
                     document_url, scraped_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        filing.cik,
                        filing.company_name,
                        filing.filing_type,
                        filing.filing_date,
                        filing.accession_number,
                        filing.document_url,
                        filing.scraped_at,
                    ),
                )
                inserted_count += 1
            except sqlite3.IntegrityError:
                logger.debug(f"Skipping duplicate filing: {filing.accession_number}")
                continue

        conn.commit()
        conn.close()

        logger.info(f"Inserted {inserted_count} new filings (skipped duplicates)")
        return inserted_count

    def get_all_filings(self) -> List[dict]:
        """Get all filings from database."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM filings ORDER BY filing_date DESC")
        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def export_to_csv(self, csv_path: str) -> None:
        """
        Export all filings to CSV.

        Args:
            csv_path: Path to output CSV file
        """
        csv_path = Path(csv_path)
        csv_path.parent.mkdir(parents=True, exist_ok=True)

        filings = self.get_all_filings()

        if not filings:
            logger.warning("No filings to export")
            return

        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=filings[0].keys())
            writer.writeheader()
            writer.writerows(filings)

        logger.info(f"Exported {len(filings)} filings to {csv_path}")

    def get_summary(self) -> dict:
        """Get summary statistics."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM filings")
        total = cursor.fetchone()[0]

        cursor.execute("""
            SELECT filing_type, COUNT(*) as count 
            FROM filings 
            GROUP BY filing_type 
            ORDER BY count DESC 
            LIMIT 10
        """)
        top_types = cursor.fetchall()

        cursor.execute("""
            SELECT company_name, COUNT(*) as count 
            FROM filings 
            GROUP BY company_name 
            ORDER BY count DESC 
            LIMIT 10
        """)
        top_companies = cursor.fetchall()

        conn.close()

        return {
            "total_filings": total,
            "top_filing_types": top_types,
            "top_companies": top_companies,
        }
