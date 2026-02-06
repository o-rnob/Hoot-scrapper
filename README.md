
#  Hoot Scrapper
By 0w1nomics

Portfolio-ready **SEC EDGAR filings scraper** with CLI, tests, and GitHub Actions CI. Collects recent company filings (10-K, 10-Q, 8-K, etc.) from the SEC's public EDGAR database.

[![CI](https://github.com/o-rnob/hoot-scrapper/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR_USERNAME/hoot-scrapper/actions/workflows/ci.yml)

## 🎯 Features

- ✅ **Ethical scraping**: Respects robots.txt, rate limiting, proper User-Agent
- ✅ **Production-ready**: Type hints, logging, error handling
- ✅ **CLI interface**: Simple commands for scraping, exporting, and analysis
- ✅ **SQLite storage**: Local database with CSV export
- ✅ **GitHub Actions**: Automated testing + optional scheduled scraping
- ✅ **Codespaces ready**: Zero-config cloud development environment

## 🚀 Quick Start

### In GitHub Codespaces (Recommended)

1. Click **Code** → **Codespaces** → **Create codespace on main**
2. Wait for container to build (auto-installs dependencies)
3. Run your first scrape:

```bash
hoot scrape --source sec-edgar --limit 20
hoot summary
```


#Project structure
```bash
hoot-scrapper/
├── src/hootscrapper/
│   ├── __init__.py
│   ├── config.py           # Settings, URLs, constants
│   ├── cli.py              # CLI commands
│   ├── utils.py            # Rate limiter, robots.txt checker
│   ├── storage.py          # SQLite database operations
│   └── scrapers/
│       ├── __init__.py
│       └── sec_edgar.py    # SEC EDGAR scraper
├── tests/
│   ├── test_parser.py      # Data model tests
│   ├── test_storage.py     # Database tests
│   └── test_cli.py         # CLI smoke tests
├── notebooks/
│   └── analyze.py          # Analysis script
├── .github/workflows/
│   ├── ci.yml              # Test automation
│   └── scrape.yml          # Scheduled scraping (optional)
├── .devcontainer/
│   └── devcontainer.json   # Codespaces config
├── data/                   # Generated data (gitignored)
├── pyproject.toml          # Project config & dependencies
└── README.md

