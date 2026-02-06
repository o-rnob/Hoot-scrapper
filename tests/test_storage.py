"""Test SQLite storage."""

import tempfile
from pathlib import Path

from hootscrapper.scrapers.sec_edgar import Filing
from hootscrapper.storage import FilingStorage


def test_storage_insert_and_retrieve():
    """Test inserting and retrieving filings."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        storage = FilingStorage(str(db_path))

        filings = [
            Filing(
                cik="1234567",
                company_name="Test Corp A",
                filing_type="10-K",
                filing_date="2026-02-06",
                accession_number="0001234567-26-000001",
                document_url="https://www.sec.gov/test1",
                scraped_at="2026-02-06T00:00:00",
            ),
            Filing(
                cik="7654321",
                company_name="Test Corp B",
                filing_type="10-Q",
                filing_date="2026-02-05",
                accession_number="0007654321-26-000002",
                document_url="https://www.sec.gov/test2",
                scraped_at="2026-02-06T00:00:00",
            ),
        ]

        inserted = storage.insert_filings(filings)
        assert inserted == 2

        all_filings = storage.get_all_filings()
        assert len(all_filings) == 2
        assert all_filings[0]["company_name"] in ["Test Corp A", "Test Corp B"]


def test_storage_duplicate_handling():
    """Test that duplicate accession numbers are skipped."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        storage = FilingStorage(str(db_path))

        filing = Filing(
            cik="1234567",
            company_name="Test Corp",
            filing_type="10-K",
            filing_date="2026-02-06",
            accession_number="DUPLICATE-123",
            document_url="https://www.sec.gov/test",
            scraped_at="2026-02-06T00:00:00",
        )

        inserted1 = storage.insert_filings([filing])
        assert inserted1 == 1

        inserted2 = storage.insert_filings([filing])
        assert inserted2 == 0  # Duplicate should be skipped

        all_filings = storage.get_all_filings()
        assert len(all_filings) == 1
