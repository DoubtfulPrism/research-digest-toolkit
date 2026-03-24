# Project: Research Digest Toolkit

**Last Updated:** 2026-03-13

## Overview

Automated research aggregation toolkit for software leadership, innovation, and academic research. Discovers, scrapes, and organizes content from HackerNews, RSS feeds, Reddit, arXiv, Twitter/X threads, and YouTube transcripts. Includes a Textual-based TUI for managing scrapers, viewing content, and analytics. Outputs are date-organized, Obsidian-ready with YAML frontmatter, and NotebookLM-ready with automatic file splitting.

## Technology Stack

- **Language:** Python 3.9+
- **CLI Framework:** Typer (modern CLI with type hints)
- **TUI Framework:** Textual 0.85.0 (6-screen terminal UI)
- **Terminal Output:** Rich (progress bars, color-coded output, tables)
- **HTTP Client:** HTTPX + DiskCache (async HTTP with caching)
- **Data Analysis:** Polars, scikit-learn
- **Retry Logic:** Tenacity (exponential backoff, automatic retries)
- **Config Validation:** Pydantic Settings
- **Testing:** Pytest (163 tests), pytest-asyncio
- **Linting:** Ruff
- **Formatting:** Black + isort
- **Config:** YAML (research_config.yaml)

## Directory Structure

```
.
├── research_digest.py          # Main orchestrator (plugin loader)
├── config_models.py            # Pydantic configuration models
├── database.py                 # SQLite deduplication (URL/title)
├── db_init.py                  # Database initialization from YAML config
├── analysis.py                 # Trend analysis with Polars/scikit-learn
├── scrapers/                   # Plugin directory
│   ├── base.py                 # ScraperBase abstract class
│   ├── arxiv_scraper.py        # arXiv scientific papers
│   ├── hn_scraper.py           # HackerNews discussions
│   ├── reddit_scraper.py       # Reddit posts
│   └── rss_scraper.py          # RSS/Atom feeds
├── research_digest_tui/        # Textual TUI application
│   ├── app.py                  # Main App class (ResearchDigestApp)
│   ├── app.tcss                # Global TUI styles
│   ├── screens/                # 6 navigable screens
│   │   ├── dashboard.py        # Dashboard overview
│   │   ├── scraper_management.py # Scraper status/controls
│   │   ├── configuration.py    # Config editor
│   │   ├── logs.py             # Content browser / logs
│   │   ├── history.py          # History / analytics
│   │   └── scheduler.py        # Schedule management
│   └── widgets/                # Reusable TUI widgets
│       └── scraper_card.py     # Scraper status card
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
├── tests/                      # Test suite (163 tests)
│   ├── conftest.py             # Shared fixtures
│   ├── test_database.py        # Deduplication tests
│   ├── test_plugin_loading.py  # Plugin architecture tests
│   ├── test_tui_integration.py # TUI app integration tests
│   ├── test_tui_screens.py     # TUI screen tests
│   ├── test_tui_widgets.py     # TUI widget tests
│   └── test_utils.py           # Utility function tests
├── docs/                       # Documentation
│   ├── specs/                  # Feature specifications
│   └── plans/                  # Implementation plans
└── research_digest/            # Output directory (date-organized)
    └── YYYY-MM-DD/
        ├── raw/                # Original content
        ├── obsidian/           # Formatted & tagged
        └── REPORT.md           # Summary
```

## Key Files

- **Configuration:** `research_config.yaml`, `config_models.py`, `pyproject.toml`, `pytest.ini`
- **Entry Points:** `research_digest.py` (CLI orchestrator), `python -m research_digest_tui` (TUI), `scrapers/*.py` (plugins)
- **Tests:** `tests/` (pytest suite with markers: unit, integration, database, slow, tui)

## Development Commands

```bash
# Install
uv pip install -r requirements.txt

# Run
./research_digest.py                              # CLI one-time run
./research_digest.py --schedule "every(4).hours"  # Scheduled
python -m research_digest_tui                     # Launch TUI

# Test
uv run pytest -q                                  # Quiet mode
uv run pytest -q --cov=. --cov-fail-under=80     # With coverage
uv run pytest -m "tui" -q                         # TUI tests only

# Lint & Format
ruff format .
ruff check . --fix
basedpyright .
```

## Architecture Notes

**Plugin Architecture:** research_digest.py dynamically loads scraper plugins from `scrapers/` that inherit from `ScraperBase`. Each plugin implements `run(config, output_dir)`. Plugins are enabled/disabled via `research_config.yaml` under `scrapers.{name}.enabled`.

**TUI Application:** `research_digest_tui/` is a Textual app with 6 screens navigable via keyboard shortcuts (d/s/c/l/h/u). Uses `switch_screen()` for navigation, per-screen TCSS files for styling. Phase 2 (in progress) adds service layer for real data integration.

**Resilient Network Operations:** HTTP requests use `retry_utils.py` decorators with exponential backoff. Custom HTTPX transports in `http_client.py` cache GET requests with DiskCache.

**Deduplication:** `database.py` uses SQLite to track scraped items by URL and title.

**Output Pipeline:** Raw content -> Obsidian formatting -> File splitting (400k char limit) -> Date-organized folders.
