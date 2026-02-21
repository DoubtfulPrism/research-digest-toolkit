# Project: Research Digest Toolkit

**Last Updated:** 2026-02-21

## Overview

Automated research aggregation toolkit for software leadership, innovation, and academic research. Discovers, scrapes, and organizes content from HackerNews, RSS feeds, Reddit, arXiv, Twitter/X threads, and YouTube transcripts. Outputs are date-organized, Obsidian-ready with YAML frontmatter, and NotebookLM-ready with automatic file splitting.

## Technology Stack

- **Language:** Python 3.9+
- **CLI Framework:** Typer (modern CLI with type hints)
- **Terminal UI:** Rich (progress bars, color-coded output, tables)
- **HTTP Client:** HTTPX + DiskCache (async HTTP with caching)
- **Retry Logic:** Tenacity (exponential backoff, automatic retries)
- **Testing:** Pytest (86 tests, 89%+ coverage)
- **Linting:** Ruff
- **Formatting:** Black + isort
- **Config:** YAML (research_config.yaml)

## Directory Structure

```
.
├── research_digest.py          # Main orchestrator (plugin loader)
├── scrapers/                   # Plugin directory
│   ├── base.py                 # ScraperBase abstract class
│   ├── arxiv_scraper.py        # arXiv scientific papers
│   ├── hn_scraper.py           # HackerNews discussions
│   ├── reddit_scraper.py       # Reddit posts
│   └── rss_scraper.py          # RSS/Atom feeds
├── database.py                 # SQLite deduplication (URL/title)
├── retry_utils.py              # Tenacity retry decorators
├── http_client.py              # HTTPX + DiskCache integration
├── rich_utils.py               # Rich console helpers
├── scheduler_utils.py          # Schedule library wrapper
├── utils.py                    # Filename generation, HTML cleaning
├── obsidian_prep.py            # YAML frontmatter + auto-tagging
├── file_splitter.py            # Split large files (NotebookLM limit)
├── file_converter.py           # Document format conversion
├── web_scraper.py              # Manual article scraping
├── youtube_transcript.py       # YouTube video transcripts
├── thread_reader.py            # Twitter/X thread download
├── research_config.yaml        # Main configuration
├── tests/                      # Test suite (86 tests)
│   ├── conftest.py             # Shared fixtures
│   ├── test_database.py        # Deduplication tests
│   ├── test_plugin_loading.py  # Plugin architecture tests
│   └── test_utils.py           # Utility function tests
└── research_digest/            # Output directory (date-organized)
    └── YYYY-MM-DD/
        ├── raw/                # Original content
        ├── obsidian/           # Formatted & tagged
        └── REPORT.md           # Summary
```

## Key Files

- **Configuration:** `research_config.yaml`, `pyproject.toml`, `pytest.ini`
- **Entry Points:** `research_digest.py` (main orchestrator), `scrapers/*.py` (plugins), utility scripts (`*.py`)
- **Tests:** `tests/` (pytest suite with markers: @pytest.mark.unit, @pytest.mark.integration, @pytest.mark.database)

## Development Commands

```bash
# Install
pip install -r requirements.txt
# Native tools (optional): sudo dnf install pandoc poppler-utils

# Run
./research_digest.py                              # One-time run
./research_digest.py --schedule "every(4).hours"  # Scheduled

# Test
pytest -q                                         # Quiet mode
pytest -q --cov=. --cov-fail-under=80            # With coverage
pytest -m "not slow"                              # Skip slow tests

# Lint & Format
ruff format .                                     # Format
ruff check . --fix                                # Lint
basedpyright .                                    # Type check
```

## Architecture Notes

**Plugin Architecture:** research_digest.py dynamically loads scraper plugins from `scrapers/` that inherit from `ScraperBase`. Each plugin implements `run(config, output_dir)`. Plugins are enabled/disabled via `research_config.yaml` under `scrapers.{name}.enabled`.

**Resilient Network Operations:** All HTTP requests use `retry_utils.py` decorators (@retry_with_logging, @retry_api_call) with exponential backoff. Retries on 5xx server errors and 429 rate limits. Custom HTTPX transports in `http_client.py` cache GET requests with DiskCache.

**Deduplication:** `database.py` uses SQLite to track scraped items by URL and title. Prevents duplicate processing across runs.

**Output Pipeline:** Raw content → Obsidian formatting (YAML frontmatter, auto-tagging) → File splitting (400k char limit for NotebookLM) → Date-organized folders.

**CI/CD:** GitHub Actions runs tests on Python 3.9-3.12, linting with ruff/black, and security scanning with Bandit.
