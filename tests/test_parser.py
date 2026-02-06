"""Test SEC EDGAR parser."""

from hootscrapper.scrapers.sec_edgar import Filing


def test_filing_dataclass():
    """Test Filing dataclass creation."""
    filing = Filing(
        cik="0001234567",
        company_name="Test Corp",
        filing_type="10-K",
        filing_date="2026-02-06",
        accession_number="0001234567-26-000001",
        document_url="https://www.sec.gov/test",
        scraped_at="2026-02-06T00:00:00",
    )

    assert filing.cik == "0001234567"
    assert filing.company_name == "Test Corp"
    assert filing.filing_type == "10-K"
    assert filing.accession_number == "0001234567-26-000001"
