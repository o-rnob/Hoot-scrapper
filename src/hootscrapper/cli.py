"""Command-line interface for Hoot Scrapper."""

import argparse
import logging
import sys

from hootscrapper.config import DEFAULT_CSV_PATH, DEFAULT_DB_PATH, LOG_FORMAT, LOG_LEVEL
from hootscrapper.scrapers.sec_edgar import SECEdgarScraper
from hootscrapper.storage import FilingStorage


def setup_logging(level: str = LOG_LEVEL) -> None:
    """Configure logging."""
    logging.basicConfig(level=getattr(logging, level.upper()), format=LOG_FORMAT)


def cmd_scrape(args: argparse.Namespace) -> None:
    """Run the scraper."""
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)

    logger.info(f"Starting scrape: source={args.source}, limit={args.limit}")

    if args.source == "sec-edgar":
        scraper = SECEdgarScraper(delay=args.delay)
        filings = scraper.scrape(limit=args.limit)

        if not filings:
            logger.error("No filings scraped")
            sys.exit(1)

        storage = FilingStorage(args.out)
        inserted = storage.insert_filings(filings)

        logger.info(f"✅ Scrape complete: {inserted} new filings saved to {args.out}")
    else:
        logger.error(f"Unknown source: {args.source}")
        sys.exit(1)


def cmd_export(args: argparse.Namespace) -> None:
    """Export data to CSV."""
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)

    storage = FilingStorage(args.db)
    storage.export_to_csv(args.out)

    logger.info(f"✅ Export complete: {args.out}")


def cmd_summary(args: argparse.Namespace) -> None:
    """Show data summary."""
    setup_logging(args.log_level)

    storage = FilingStorage(args.db)
    summary = storage.get_summary()

    print("\n📊 Hoot Scrapper Summary")
    print("=" * 50)
    print(f"\nTotal filings: {summary['total_filings']}")

    print("\n🔝 Top filing types:")
    for filing_type, count in summary["top_filing_types"]:
        print(f"  {filing_type}: {count}")

    print("\n🏢 Top companies:")
    for company, count in summary["top_companies"]:
        print(f"  {company}: {count}")

    print()


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Hoot Scrapper - Portfolio-ready SEC EDGAR scraper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument("--log-level", default=LOG_LEVEL, help="Logging level")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # scrape command
    scrape_parser = subparsers.add_parser("scrape", help="Scrape data from a source")
    scrape_parser.add_argument(
        "--source", default="sec-edgar", help="Data source (default: sec-edgar)"
    )
    scrape_parser.add_argument(
        "--limit", type=int, default=100, help="Max number of items to scrape"
    )
    scrape_parser.add_argument("--out", default=DEFAULT_DB_PATH, help="Output database path")
    scrape_parser.add_argument(
        "--delay", type=float, default=0.5, help="Delay between requests (seconds)"
    )
    scrape_parser.set_defaults(func=cmd_scrape)

    # export command
    export_parser = subparsers.add_parser("export", help="Export data to CSV")
    export_parser.add_argument("--db", default=DEFAULT_DB_PATH, help="Database path")
    export_parser.add_argument("--out", default=DEFAULT_CSV_PATH, help="Output CSV path")
    export_parser.set_defaults(func=cmd_export)

    # summary command
    summary_parser = subparsers.add_parser("summary", help="Show data summary")
    summary_parser.add_argument("--db", default=DEFAULT_DB_PATH, help="Database path")
    summary_parser.set_defaults(func=cmd_summary)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
