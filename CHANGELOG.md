# Changelog

All notable changes to the Research Digest Toolkit are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] - 2026-05-07

### Added
- **Full TUI rewrite** — Replaced the legacy `research_digest_tui` module with a structured
  `rdt/` package built on Textual 8+, with dedicated screens, services, and widgets.
- **Dashboard screen** — Live status bar, per-scraper cards with progress bars, and a
  top-bar **Run All Now** button to fire all enabled scrapers in one click.
- **Scraper Management screen** — Per-scraper Run/Configure/Enable-Disable controls with
  live output modal.
- **Configuration screen** — Editable config fields for every scraper:
  - HackerNews: `search_topics`, `min_points`, `max_results`
  - ArXiv: `search_queries`, `max_results`
  - Reddit: `subreddits`, `time_filter` *(new)*
  - RSS: feed list management (add/remove)
- **Global `rdt` CLI command** — Replaces the old `Research_Toolkit` entry point.
  - `rdt tui` — Launch the TUI.
  - `rdt convert <file>` — Convert a PDF/DOCX directly from the command line.
- **`install.sh` installer** — One-command setup that installs dependencies via `uv` and
  writes a global wrapper to `~/.local/bin/rdt`. No manual venv activation required.
- **Hybrid ingestion engine** — `rdt/core/converter.py` uses native Linux tools
  (`pdftotext`, `pandoc`) where available, falling back to PyMuPDF on other platforms.
- **Obsidian and Substack adapters** — Export converted markdown directly to either format.
- **Converter TUI screen** — Point-and-click document conversion inside the TUI.
- **TDD test suite additions** — New tests covering:
  - Dashboard composition and `Run All` button rendering
  - Configuration screen field mapping per scraper
  - RunnerService path resolution

### Fixed
- Back button crash (`IndexError: pop from empty list`) when navigating from a pushed
  Configuration screen back to Dashboard.
- Configuration screen content truncation — enforced `height: auto` on inner containers
  so long RSS feed lists scroll correctly.
- Dashboard `Run All` button not visible — resolved CSS layout collapse with explicit
  `height: 3` and `width: 1fr` on the action bar.
- Scraper `Run Now` path resolution errors after package restructuring.
- `Add New Scraper` and `Run All` buttons were permanently disabled.

### Changed
- Version bumped to `1.0.0` — Production/Stable classifier applied.
- `pyproject.toml` updated with `rdt` entry point alongside legacy `Research_Toolkit`.
- README overhauled — installation section updated to reflect `install.sh` workflow.

### Known Issues
- `tests/test_rss_scraper.py::TestFetchFeed` — 3 tests require `pytest-httpx` (not in
  dev dependencies). All other 402 tests pass. Will be resolved in a follow-up patch.

---

## [0.x.x] - Pre-release development

Initial shell-script based implementation, ported progressively to Python.
See git history for individual commit details.
