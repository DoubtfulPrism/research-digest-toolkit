# TUI Phase 2: Read-Only Integration Implementation Plan

Created: 2026-03-11
Status: VERIFIED
Approved: Yes
Iterations: 0
Worktree: No
Type: Feature

## Summary

**Goal:** Replace placeholder content in TUI screens with real data from `research_config.yaml` and the SQLite database (`research_digest_state.db`). Create a service layer for data access, use Polars for analytics queries, and build a content browser (timeline view) and text-based analytics dashboard.

**Architecture:** Service classes (`ConfigService`, `DataService`) wrap config loading and Polars database queries. Services are created by the App and made accessible to screens via `self.app`. Screens read from services during `on_mount()` to populate widgets with real data.

**Tech Stack:**
- Textual 0.85.0 (TUI framework, already installed)
- Polars (new dependency — DataFrame analytics over SQLite)
- Existing: YAML config, SQLite database, Pydantic models

## Scope

### In Scope

- Service layer: `ConfigService` (config reading) and `DataService` (Polars queries)
- Dashboard: dynamic ScraperCards from config, real item counts and last-run times
- Scraper Management: real config values, real item counts per scraper
- Logs screen → Content Browser: timeline of all processed items from database, source filters
- History/Analytics: summary stats, source distribution text tables, daily trends, time range filters
- Unit tests for services, updated screen tests, integration tests

### Out of Scope

- Writing/modifying config (Phase 4)
- Running scrapers from TUI (Phase 3)
- Live progress updates / real-time streaming (Phase 3)
- Schedule management logic (Phase 5)
- Configuration editing forms (Phase 4)

## Context for Implementer

> Write for an implementer who has never seen the codebase.

- **Patterns to follow:**
  - `analysis.py:16-39` — existing Polars + SQLite pattern using `pl.read_database(query, conn)`
  - `research_digest.py:46-66` — config loading with Pydantic validation via `ResearchDigestConfig`
  - `research_digest_tui/screens/dashboard.py` — current Phase 1 screen pattern (compose → yield widgets)
  - `research_digest_tui/widgets/scraper_card.py` — reactive widget pattern with `reactive[]` properties
  - `tests/test_tui_integration.py` — async pilot tests using `app.run_test()`

- **Conventions:**
  - Screens: One file per screen in `research_digest_tui/screens/`
  - Widgets: Extend `Container` or `Widget`, use `reactive` properties
  - CSS: Screen-specific `.tcss` files, colors match Rich theme
  - Services: New `research_digest_tui/services/` directory
  - Tests: `pytest.importorskip("textual")` at top of TUI test files, `@pytest.mark.unit` / `@pytest.mark.tui` markers

- **Key files:**
  - `database.py` — SQLite schema: `processed_items(source, unique_id, processed_at, title, url)`, `topics`, `keywords`, `topic_occurrences`. Includes `get_items()`, `get_item_counts()`.
  - `config_models.py` — Pydantic models: `ResearchDigestConfig`, `ScrapersConfig`, `HNConfig`, `RSSConfig`, `RedditConfig`, `ArxivConfig`
  - `research_config.yaml` — YAML config with scrapers, topics, processing, output sections
  - `research_digest_state.db` — live database with scraped items across 4 sources
  - `research_digest.py:258-263` — current TUI launch point (creates `ResearchDigestApp()` with no args)
  - `research_digest_tui/services/config_service.py` — ConfigService (Task 1: COMPLETE)
  - `research_digest_tui/services/data_service.py` — DataService with Polars queries (Task 2: COMPLETE)
  - `tests/test_config_service.py` — ConfigService unit tests (Task 1: COMPLETE)
  - `tests/test_tui_services.py` — DataService unit tests (Task 2: COMPLETE)

- **Gotchas:**
  - Database `processed_items` has `source`, `unique_id`, `processed_at`, `title`, `url` columns. Schema migration in `database._migrate_schema()` adds title/url to existing databases.
  - `analysis.py` uses `pl.read_database(query, conn)` where `conn` is a `sqlite3.Connection` — Polars reads directly from SQLite connections. **Note:** `analysis.py` uses `with get_connection() as conn:` which manages transactions, NOT connection close. DataService should use try/finally with explicit `conn.close()`.
  - The `topics` and `topic_occurrences` tables are currently empty (0 rows) — handle gracefully.
  - ScraperCard widget uses `scraper_name` (not `name`) to avoid conflict with Textual's `Widget.name`.
  - App currently uses `push_screen("dashboard")` in `on_mount()` — navigation uses `switch_screen()`.
  - Config scraper keys don't always match scraper names: config uses `hackernews` but scraper reports as `hn`.

- **Domain context:** The Research Digest Toolkit aggregates content from HN, RSS, Reddit, and ArXiv. The database tracks every URL/ID ever processed for deduplication. Phase 2 makes this data visible in the TUI — showing what's configured and what's been collected.

## Assumptions

- Polars can be installed in the worktree environment — supported by `analysis.py` already using it — Tasks 2, 6, 7 depend on this
- The `processed_items` table schema won't change during implementation — supported by `database.py` being stable since Phase 1 — Tasks 2, 6, 7 depend on this
- Config loading via `ResearchDigestConfig` is sufficient (no need for raw YAML) — supported by `research_digest.py:46-66` — Tasks 1, 4, 5 depend on this
- Textual DataTable widget is available in v0.85.0 for the content browser — Tasks 6 depends on this

## Testing Strategy

- **Unit tests:** ConfigService and DataService tested with fixtures (temp YAML files, temp SQLite databases). No network, no real config files.
- **Integration tests:** Async pilot tests verifying screens render real data from test fixtures. Use `app.run_test()` pattern from existing `test_tui_integration.py`.
- **Manual verification:** Launch TUI with real database, verify all screens show actual data, test source filters on content browser, test time range filters on analytics.

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
| ---- | ---------- | ------ | ---------- |
| Polars installation fails in worktree | Low | High | `analysis.py` already uses Polars — it's a known-good dependency. Install via `uv pip install polars`. |
| Database has no data (fresh install) | Medium | Medium | All screens show "No data yet" gracefully when queries return empty. DataService methods return empty DataFrames. |
| Config file missing or invalid | Low | Medium | ConfigService catches exceptions and returns default config. Dashboard shows "Config not found" warning. |
| Textual DataTable not suitable for timeline | Low | Medium | DataTable is a core Textual widget since v0.40+. Fallback: use ListView with Static items. |
| Source name mismatch (config "hackernews" vs DB "hn") | High | Low | ConfigService provides a source name mapping dict. Normalize to DB names when querying. |

## Pre-Mortem

*Assume this plan failed. Most likely internal reasons:*

1. **Service injection pattern doesn't work with Textual's screen lifecycle** (Task 3) → Trigger: screens can't access `self.app.config_service` during `compose()` because app isn't mounted yet. Resolution: load data in `on_mount()` instead of `compose()`, use reactive properties to trigger re-renders.
2. **Polars queries block the TUI event loop** (Tasks 6, 7) → Trigger: TUI freezes for >200ms when switching to History or Content Browser screens with large datasets. Resolution: use Textual's `@work(thread=True)` decorator for queries, show loading indicator.
3. **Text table rendering breaks with edge cases** (Task 7) → Trigger: zero-count sources, very long source names, or 0 total items cause division by zero. Resolution: guard all divisions, cap label width, handle empty data gracefully.

## Goal Verification

### Truths

1. Dashboard shows real scraper names, enabled/disabled status, and item counts from the database
2. Scraper Management shows actual config values (topics, feeds, subreddits) from research_config.yaml
3. Content Browser (Logs screen) shows a scrollable timeline of all processed items with source filtering
4. History/Analytics shows total items, items per source, daily counts in text-based tables
5. Time range filters on History screen change the displayed data
6. Source filter buttons on Content Browser screen filter the displayed items
7. All screens handle empty database gracefully (show "No data" messages)

### Artifacts

- `research_digest_tui/services/config_service.py` — config loading and scraper config access
- `research_digest_tui/services/data_service.py` — Polars queries against SQLite
- Updated screens: `dashboard.py`, `scraper_management.py`, `logs.py`, `history.py`
- `tests/test_tui_services.py` — unit tests for services
- Updated `tests/test_tui_screens.py` and `tests/test_tui_integration.py`

### Key Links

- `ResearchDigestApp` creates `ConfigService` and `DataService` → screens access via `self.app`
- `research_digest.py` passes `config_path` to `ResearchDigestApp` constructor
- `ConfigService` loads `research_config.yaml` → returns `ResearchDigestConfig` Pydantic model
- `DataService` queries `research_digest_state.db` via Polars → returns DataFrames and dicts
- Dashboard `on_mount()` → reads services → populates ScraperCards dynamically
- Content Browser `on_mount()` → reads `DataService.get_items_timeline()` → populates DataTable
- History `on_mount()` → reads `DataService.get_summary_stats()` + `get_source_distribution()` → renders charts

## Progress Tracking

- [x] Task 1: ConfigService — config loading and scraper config access
- [x] Task 2: DataService — Polars database queries
- [x] Task 3: Wire services into App and screens
- [x] Task 4: Dashboard with real data
- [x] Task 5: Scraper Management with real config
- [x] Task 6: Content Browser (Logs screen) with timeline view
- [x] Task 7: History/Analytics with stats and text tables

**Total Tasks:** 7 | **Completed:** 7 | **Remaining:** 0

## Implementation Tasks

### Task 1: ConfigService — Config Loading and Scraper Config Access

**Objective:** Create a service class that loads `research_config.yaml` and provides typed access to scraper configurations, topics, and output settings.

**Dependencies:** None

**Files:**
- Create: `research_digest_tui/services/__init__.py`
- Create: `research_digest_tui/services/config_service.py`
- Create: `tests/test_tui_services.py`

**Key Decisions / Notes:**
- Reuse `config_models.ResearchDigestConfig` for Pydantic validation (same as `research_digest.py:46-66`)
- Provide `get_scraper_configs()` → list of dicts with `name`, `enabled`, `config_summary` (human-readable settings string)
- Provide source name mapping: config key → DB source name (e.g., `"hackernews"` → `"hn"`, `"rss"` → `"rss"`, `"reddit"` → `"reddit"`, `"arxiv"` → `"arxiv"`)
- Handle missing config file gracefully — return defaults
- Constructor takes `config_path: Path` parameter
- **Register `tui` marker:** The project uses `--strict-markers`. Before writing any tests with `@pytest.mark.tui`, register the marker in `pyproject.toml` under `[tool.pytest.ini_options]` markers: `"tui: Tests for the Textual TUI screens and widgets"`

**Definition of Done:**
- [ ] `tui` pytest marker registered in `pyproject.toml`
- [ ] ConfigService loads YAML and returns validated ResearchDigestConfig
- [ ] `get_scraper_configs()` returns list with name, enabled, and config summary for each scraper
- [ ] Missing config file returns default config without crashing
- [ ] Source name mapping works for all 4 scrapers
- [ ] All tests pass

**Verify:**
- `uv run pytest tests/test_tui_services.py -q`

---

### Task 2: DataService — Polars Database Queries

**Objective:** Create a service class that queries the SQLite database using Polars and returns analytics data for TUI screens.

**Dependencies:** None (parallel with Task 1)

**Files:**
- Create: `research_digest_tui/services/data_service.py`
- Modify: `tests/test_tui_services.py` (add DataService tests)

**Key Decisions / Notes:**
- Use `pl.read_database(query, conn)` with `sqlite3.Connection` (similar to `analysis.py:20-26`)
- **Connection lifecycle:** Do NOT use `get_connection()` as a context manager — `sqlite3.Connection`'s `with` manages transactions only, not connection close. Instead use `conn = sqlite3.connect(str(db_path))` in try/finally with `conn.close()`. Each method opens and closes its own connection.
- Methods:
  - `get_item_counts_by_source()` → `dict[str, int]` (e.g., `{"hn": 193, "arxiv": 204}`)
  - `get_items_timeline(source_filter: str | None = None, limit: int = 100)` → `list[dict]` with `source`, `unique_id`, `processed_at`
  - `get_daily_counts(days: int = 7)` → `list[dict]` with `date`, `count`
  - `get_summary_stats(days: int | None = None)` → `dict` with `total_items`, `source_count`, `date_range`, `avg_per_day`. When `days` is not None, filter `processed_at` to the last N days before computing stats.
  - `get_source_distribution(days: int | None = None)` → `list[dict]` with `source`, `count`, `percentage`. When `days` is not None, filter to the last N days.
- Constructor takes `db_path: Path` parameter
- Return empty results (not exceptions) when database is empty or missing
- All queries should handle the case where `processed_items` table is empty

**Definition of Done:**
- [ ] DataService queries SQLite via Polars for all 5 methods
- [ ] Empty database returns empty results gracefully
- [ ] Missing database file returns empty results without crashing
- [ ] Tests use `tmp_path` with populated test databases
- [ ] All tests pass

**Verify:**
- `uv run pytest tests/test_tui_services.py -q`

---

### Task 3: Wire Services into App and Screens

**Objective:** Modify `ResearchDigestApp` to create services and make them accessible to all screens.

**Dependencies:** Task 1, Task 2

**Files:**
- Modify: `research_digest_tui/app.py`
- Modify: `research_digest_tui/__init__.py` (update exports if needed)
- Modify: `research_digest.py` (pass config_path to App)
- Modify: `tests/test_tui_screens.py` (update App instantiation)
- Modify: `tests/test_tui_integration.py` (update App instantiation)

**Key Decisions / Notes:**
- `ResearchDigestApp.__init__` accepts optional `config_path: Path | None = None` and `db_path: Path | None = None`
- **Must pass `**kwargs` to `super().__init__()`** — Textual's `App.__init__` expects keyword args for CSS/watch initialization: `def __init__(self, config_path=None, db_path=None, **kwargs): super().__init__(**kwargs)`
- Defaults: `config_path` = `Path("research_config.yaml")`, `db_path` = `Path("research_digest_state.db")`
- Services created in `__init__`: `self.config_service = ConfigService(config_path)` and `self.data_service = DataService(db_path)`
- Screens access via `self.app.config_service` and `self.app.data_service`
- Update `research_digest.py:258-262` to pass config path: `ResearchDigestApp(config_path=Path(config))`
- Existing tests that instantiate `ResearchDigestApp()` must still work (default paths)

**Definition of Done:**
- [ ] App creates ConfigService and DataService on init
- [ ] `research_digest.py` passes config_path to App
- [ ] Existing tests still pass with default parameters
- [ ] Screens can access `self.app.config_service` and `self.app.data_service`
- [ ] Test: `ResearchDigestApp()` with no args still works (has config_service and data_service)
- [ ] Test: `ResearchDigestApp(config_path=path)` instantiates correctly
- [ ] All tests pass

**Verify:**
- `uv run pytest tests/test_tui_screens.py tests/test_tui_integration.py -q`

---

### Task 4: Dashboard with Real Data

**Objective:** Replace hardcoded dashboard content with real scraper status and item counts from services.

**Dependencies:** Task 3

**Files:**
- Modify: `research_digest_tui/screens/dashboard.py`
- Modify: `research_digest_tui/widgets/scraper_card.py` (add `enabled` property)
- Modify: `tests/test_tui_integration.py` (update dashboard tests)

**Key Decisions / Notes:**
- In `on_mount()`, read `self.app.config_service.get_scraper_configs()` to get scraper list
- In `on_mount()`, read `self.app.data_service.get_item_counts_by_source()` for counts
- In `on_mount()`, read `self.app.data_service.get_summary_stats()` for status bar
- Replace hardcoded 4 ScraperCards in `compose()` with dynamic creation based on config
- Status bar shows: "Items Collected: {total} | Sources: {count} | Data: {date_range}"
- ScraperCard shows enabled/disabled status and real item count
- Handle empty data: show "No data collected yet" in status bar
- **compose() must not call services** — use placeholders in compose(), populate in on_mount()

**Definition of Done:**
- [ ] Dashboard ScraperCards are created from config (not hardcoded)
- [ ] ScraperCards show real item counts from database
- [ ] Status bar shows real total items and date range
- [ ] Empty database shows graceful "No data" message
- [ ] All tests pass

**Verify:**
- `uv run pytest tests/test_tui_integration.py -q`

---

### Task 5: Scraper Management with Real Config

**Objective:** Replace hardcoded scraper details with actual config values and database statistics. Also extend DataService with `get_last_run_per_source()`.

**Dependencies:** Task 3

**Files:**
- Modify: `research_digest_tui/services/data_service.py` (add `get_last_run_per_source()`)
- Modify: `research_digest_tui/screens/scraper_management.py`
- Modify: `tests/test_tui_services.py` (add test for `get_last_run_per_source()`)
- Modify: `tests/test_tui_integration.py` (add scraper management tests)

**Key Decisions / Notes:**
- **Add `get_last_run_per_source() -> dict[str, str]` to DataService:** runs `SELECT source, MAX(processed_at) AS last_run FROM processed_items GROUP BY source` and returns `{source: iso_date_string}`. Returns `{}` for empty/missing DB.
- In `on_mount()`, read config service for scraper settings
- Display real values: topics, feeds, subreddits, search queries per scraper
- Show item count per scraper from `data_service.get_item_counts_by_source()`
- Show last processed date per scraper from `data_service.get_last_run_per_source()`
- Dynamically generate scraper rows based on config (not hardcoded 4 rows)
- Keep action buttons disabled (Phase 3: Run Now, Phase 4: Configure)
- Show [ENABLED] or [DISABLED] badge based on config
- **compose() creates container structure**, `on_mount()` populates with real data

**Definition of Done:**
- [ ] `DataService.get_last_run_per_source()` implemented and tested
- [ ] Scraper rows generated from config (not hardcoded)
- [ ] Config summary shows real values (topics, feeds, etc.)
- [ ] Item counts and last-run dates from database
- [ ] Enabled/disabled status from config
- [ ] Empty config handled gracefully
- [ ] All tests pass

**Verify:**
- `uv run pytest tests/test_tui_integration.py -q`

---

### Task 6: Content Browser (Logs Screen) with Timeline View

**Objective:** Transform the Logs placeholder into a content browser showing a chronological timeline of all processed items from the database, with source filtering. Also update `get_items_timeline()` to include title/url.

**Dependencies:** Task 3

**Files:**
- Modify: `research_digest_tui/services/data_service.py` (update `get_items_timeline()` to select title, url)
- Modify: `research_digest_tui/screens/logs.py`
- Modify: `research_digest_tui/screens/logs.tcss`
- Modify: `tests/test_tui_services.py` (update timeline tests for title/url)
- Modify: `tests/test_tui_integration.py` (add content browser tests)

**Key Decisions / Notes:**
- **Update `get_items_timeline()` to select `source, unique_id, title, url, processed_at`** — display Title as primary column (fall back to unique_id when title is NULL for older rows)
- Use Textual `DataTable` widget for the timeline (sortable columns, scrollable)
- Columns: Source, Title (fallback to unique_id), Date
- Load data in `on_mount()` via `self.app.data_service.get_items_timeline(limit=200)`
- Source filter buttons: All, HN, RSS, Reddit, ArXiv — clicking filters the DataTable. **Filter buttons must only pass validated source strings** from `SOURCE_NAME_MAPPING` values to prevent SQL injection.
- Replace the filter buttons from Phase 1 (INFO/WARN/ERROR) with source filters
- Keep screen title as "Content Browser" (update from "Logs" in the heading, but keep screen class name `Logs` and keyboard binding `l` unchanged to avoid breaking navigation)
- Handle empty database: show "No content collected yet — run a scraper to populate"
- Truncate long URLs/titles in columns for display

**Definition of Done:**
- [ ] `get_items_timeline()` returns title and url columns
- [ ] DataTable shows processed items with Source, Title, Date columns
- [ ] Title column falls back to unique_id when title is NULL
- [ ] Source filter buttons filter the displayed items
- [ ] "All" filter shows all items
- [ ] Empty database shows helpful message
- [ ] DataTable is scrollable for large datasets
- [ ] All tests pass

**Verify:**
- `uv run pytest tests/test_tui_integration.py -q`

---

### Task 7: History/Analytics with Stats and Text Tables

**Objective:** Replace the History placeholder with an analytics dashboard showing summary stats, source distribution, and daily trends using text-based tables powered by Polars.

**Dependencies:** Task 3

**Files:**
- Modify: `research_digest_tui/screens/history.py`
- Modify: `research_digest_tui/screens/history.tcss`
- Modify: `tests/test_tui_integration.py` (add analytics tests)

**Key Decisions / Notes:**
- Summary section at top: Total Items, Average/Day, Most Active Source, Date Range (using Static widgets)
- Source distribution: text-based table showing source name, item count, and percentage (using Static widgets, one per source)
- Daily counts: show last N days with counts as a text list
- Time range filter buttons: 7 Days, 30 Days, All Time — clicking re-queries DataService
- Make filter buttons functional: on press → call `data_service.get_summary_stats(days=N)` and `get_source_distribution(days=N)` and update display
- Load data in `on_mount()` via data service methods
- Handle edge cases: zero items, single source, all items on one day
- Handle empty database: show "No data collected yet" with helpful guidance

**Definition of Done:**
- [ ] Summary section shows total items, avg/day, most active source, date range
- [ ] Source distribution displayed as text table with counts and percentages
- [ ] Daily counts shown for selected time range
- [ ] Time range filter buttons change the displayed data
- [ ] Empty database shows graceful message
- [ ] Division by zero and edge cases handled
- [ ] All tests pass

**Verify:**
- `uv run pytest tests/test_tui_integration.py -q`
- `uv run pytest -q` (full suite)

---

## Open Questions

None — all design decisions resolved during planning.

## Deferred Ideas

- **Topic analytics**: The `topics` and `topic_occurrences` tables exist but are currently empty. When populated, could add topic trend charts to History screen.
- **Export functionality**: Polars makes CSV/Parquet export trivial. Could add export buttons in Phase 3+.
- **Content preview**: Show article title/summary when clicking a row in Content Browser. Requires storing more metadata in database.
