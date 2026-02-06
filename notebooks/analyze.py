"""Simple analysis script for scraped SEC filings."""

import sqlite3
from collections import Counter
from pathlib import Path


def analyze_filings(db_path: str = "data/hoot.sqlite") -> None:
    """Analyze scraped filings and print summary."""
    
    if not Path(db_path).exists():
        print(f"❌ Database not found: {db_path}")
        print("Run 'hoot scrape' first to collect data.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Total filings
    cursor.execute("SELECT COUNT(*) FROM filings")
    total = cursor.fetchone()[0]

    # Filing types distribution
    cursor.execute("SELECT filing_type, COUNT(*) FROM filings GROUP BY filing_type")
    filing_types = cursor.fetchall()

    # Most active companies
    cursor.execute("""
        SELECT company_name, COUNT(*) as count 
        FROM filings 
        GROUP BY company_name 
        ORDER BY count DESC 
        LIMIT 10
    """)
    top_companies = cursor.fetchall()

    # Recent filings
    cursor.execute("""
        SELECT company_name, filing_type, filing_date 
        FROM filings 
        ORDER BY filing_date DESC 
        LIMIT 5
    """)
    recent = cursor.fetchall()

    conn.close()

    # Print analysis
    print("\n" + "="*60)
    print("📊 SEC EDGAR FILINGS ANALYSIS")
    print("="*60)
    
    print(f"\n📈 Total Filings Collected: {total}")
    
    print("\n📋 Filing Types Distribution:")
    for filing_type, count in sorted(filing_types, key=lambda x: x[1], reverse=True):
        percentage = (count / total * 100) if total > 0 else 0
        print(f"  {filing_type:15s} {count:4d} ({percentage:5.1f}%)")
    
    print("\n🏢 Top 10 Most Active Companies:")
    for i, (company, count) in enumerate(top_companies, 1):
        print(f"  {i:2d}. {company[:50]:50s} {count:3d} filings")
    
    print("\n🕒 5 Most Recent Filings:")
    for company, filing_type, date in recent:
        print(f"  {date} - {filing_type:10s} - {company[:40]}")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    analyze_filings()
