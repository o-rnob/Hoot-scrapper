"""Test CLI commands."""

import subprocess


def test_cli_help():
    """Test that CLI help runs without error."""
    result = subprocess.run(["hoot", "--help"], capture_output=True, text=True)
    assert result.returncode == 0
    assert "Hoot Scrapper" in result.stdout


def test_cli_scrape_help():
    """Test scrape command help."""
    result = subprocess.run(["hoot", "scrape", "--help"], capture_output=True, text=True)
    assert result.returncode == 0
    assert "scrape" in result.stdout.lower()
