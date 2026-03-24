# TUI Migration Specification

**Status:** Proposed
**Created:** 2026-02-21
**Target Version:** 2.0.0

## Overview

Transform the Research Digest Toolkit from a CLI tool with Rich formatting into a full-featured Terminal User Interface (TUI) application. This will provide an interactive, real-time interface for managing research digestion workflows.

---

## Vision & Goals

### Primary Goals

1. **Interactive Management**: Replace command-line flags with interactive menus and forms
2. **Real-Time Monitoring**: Live progress updates, log streaming, and status dashboards
3. **Visual Configuration**: Edit `research_config.yaml` through a guided UI
4. **Workflow Orchestration**: Start/stop scrapers, schedule runs, view history
5. **Enhanced UX**: Reduce cognitive load, improve discoverability, enable multitasking

### Success Metrics

- Users can complete full workflows without touching YAML files
- Real-time visibility into scraper progress and errors
- Configuration changes can be made without restarting the app
- New users can onboard without reading documentation

---

## Current State Analysis

### Strengths to Preserve

- **Rich Console Output**: Clean, colored terminal output with progress bars
- **Plugin Architecture**: Dynamic scraper loading via `ScraperBase`
- **Robust Error Handling**: Tenacity retry logic, comprehensive logging
- **Configuration System**: Pydantic models with validation
- **Testing**: 151 tests, 89%+ coverage

### Pain Points to Address

1. **Configuration Complexity**: Editing YAML is error-prone for new users
2. **Limited Feedback**: Can't see what's happening during long-running scrapes
3. **No Interactivity**: Must restart to change settings or run different scrapers
4. **Log Management**: Console logs scroll away, hard to review past errors
5. **Workflow Friction**: Multiple commands needed for common tasks

---

## Proposed TUI Features

### Core Screens

#### 1. Dashboard (Main Screen)
```
┌─ Research Digest Toolkit ───────────────────────────────────────┐
│                                                                  │
│  Status: Running         Last Run: 2026-02-21 10:30            │
│  Active Scrapers: 3/4    Items Collected: 247                   │
│                                                                  │
│  ┌─ Active Scrapers ────────────────────────────────────┐      │
│  │ [●] ArXiv          Running    12 papers   ████░░ 80% │      │
│  │ [●] HackerNews     Running    45 stories  ██████ 100%│      │
│  │ [●] Reddit         Running    23 posts    ███░░░ 60% │      │
│  │ [ ] RSS            Disabled   —           ░░░░░░ 0%  │      │
│  └──────────────────────────────────────────────────────┘      │
│                                                                  │
│  ┌─ Recent Activity ────────────────────────────────────┐      │
│  │ 10:35:22  ArXiv     Found: "Attention Is All You..." │      │
│  │ 10:35:18  Reddit    Skipped: Already processed       │      │
│  │ 10:35:15  HN        Error: Rate limit (retrying...)  │      │
│  └──────────────────────────────────────────────────────┘      │
│                                                                  │
│  [S] Scrapers  [C] Config  [L] Logs  [H] History  [Q] Quit    │
└──────────────────────────────────────────────────────────────────┘
```

**Features:**
- Real-time status for all scrapers
- Visual progress bars
- Live activity feed
- Quick navigation to other screens

#### 2. Scraper Management Screen
```
┌─ Manage Scrapers ───────────────────────────────────────────────┐
│                                                                  │
│  > ArXiv Scraper                                    [ENABLED]   │
│    Search Queries: 3 configured                                 │
│    Last Run: 2 hours ago (12 papers collected)                  │
│    [Configure] [Run Now] [View Logs] [Disable]                 │
│                                                                  │
│  > HackerNews Scraper                               [ENABLED]   │
│    Topics: AI, Platform Engineering, DevOps                     │
│    Last Run: 30 minutes ago (45 stories collected)              │
│    [Configure] [Run Now] [View Logs] [Disable]                 │
│                                                                  │
│  > Reddit Scraper                                   [ENABLED]   │
│    Subreddits: r/Python, r/MachineLearning                      │
│    Last Run: 1 hour ago (23 posts collected)                    │
│    [Configure] [Run Now] [View Logs] [Disable]                 │
│                                                                  │
│  > RSS Scraper                                      [DISABLED]  │
│    Feeds: 0 configured                                          │
│    Last Run: Never                                              │
│    [Configure] [Enable]                                         │
│                                                                  │
│  [Add New Scraper] [Run All] [Back]                            │
└──────────────────────────────────────────────────────────────────┘
```

**Features:**
- Enable/disable scrapers individually
- Run scrapers on-demand
- View configuration summary
- Access scraper-specific logs

#### 3. Configuration Editor
```
┌─ Configuration: ArXiv Scraper ──────────────────────────────────┐
│                                                                  │
│  Enabled:        [✓] Yes  [ ] No                                │
│  Days Back:      [7________________]                            │
│  Max Results:    [50_______________]                            │
│                                                                  │
│  Search Queries:                                                │
│  ┌────────────────────────────────────────────────────────┐   │
│  │ 1. machine learning                            [Edit] [X]│   │
│  │ 2. natural language processing                 [Edit] [X]│   │
│  │ 3. computer vision                             [Edit] [X]│   │
│  └────────────────────────────────────────────────────────┘   │
│  [Add Query]                                                    │
│                                                                  │
│  Output Settings:                                               │
│  ┌────────────────────────────────────────────────────────┐   │
│  │ Output Dir:  [data/raw___________________________]        │   │
│  │ Format:      [●] Markdown  [ ] JSON  [ ] Both           │   │
│  └────────────────────────────────────────────────────────┘   │
│                                                                  │
│  [Save] [Cancel] [Test Configuration]                          │
└──────────────────────────────────────────────────────────────────┘
```

**Features:**
- Form-based configuration editing
- Inline validation
- Test configuration before saving
- Visual feedback for invalid inputs

#### 4. Log Viewer
```
┌─ Logs: HackerNews Scraper ──────────────────────────────────────┐
│                                                                  │
│  Filter: [All___________] [●] Info [✓] Warning [✓] Error       │
│                                                                  │
│  ┌─ Log Output ──────────────────────────────────────────┐    │
│  │ 10:35:22 INFO  Starting HackerNews scraper            │    │
│  │ 10:35:23 INFO  Searching for topic: 'AI'              │    │
│  │ 10:35:25 INFO  Found 12 stories matching criteria     │    │
│  │ 10:35:26 WARN  Rate limit approaching (8 req/min)     │    │
│  │ 10:35:28 INFO  Processing: "Show HN: My AI Project"   │    │
│  │ 10:35:30 INFO  Fetched 45 comments                    │    │
│  │ 10:35:32 ERROR HTTP 429: Rate limit exceeded          │    │
│  │ 10:35:33 INFO  Retrying in 5 seconds...               │    │
│  │ 10:35:38 INFO  Retry successful                       │    │
│  │ ...                                                    │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                  │
│  [Export Logs] [Clear] [Back]                                  │
└──────────────────────────────────────────────────────────────────┘
```

**Features:**
- Real-time log streaming
- Filter by level (INFO/WARN/ERROR)
- Search log contents
- Export logs to file

#### 5. History & Analytics
```
┌─ Collection History ────────────────────────────────────────────┐
│                                                                  │
│  Time Range: [Last 7 Days ▼]                                   │
│                                                                  │
│  Total Items Collected: 1,247                                   │
│  Avg Items/Day: 178                                             │
│                                                                  │
│  ┌─ By Source ──────────────────────────────────────────┐     │
│  │ ArXiv:         342 papers    ███████░░░ 27%          │     │
│  │ HackerNews:    589 stories   █████████████████ 47%   │     │
│  │ Reddit:        246 posts     ██████░░░ 20%           │     │
│  │ RSS:           70 articles   ██░░░ 6%                │     │
│  └──────────────────────────────────────────────────────┘     │
│                                                                  │
│  ┌─ By Date ────────────────────────────────────────────┐     │
│  │ 2026-02-21:  247 items  ███████████████              │     │
│  │ 2026-02-20:  193 items  ████████████░░░              │     │
│  │ 2026-02-19:  165 items  ██████████░░░░               │     │
│  │ 2026-02-18:  211 items  █████████████░               │     │
│  │ ...                                                   │     │
│  └──────────────────────────────────────────────────────┘     │
│                                                                  │
│  [Export CSV] [View Details] [Back]                            │
└──────────────────────────────────────────────────────────────────┘
```

**Features:**
- Historical metrics and trends
- Visual charts (bar/line graphs)
- Export data for analysis
- Date range filtering

#### 6. Scheduler (Using `schedule` library)
```
┌─ Schedule Manager ──────────────────────────────────────────────┐
│                                                                  │
│  > Daily Digest Run                                [ENABLED]    │
│    Schedule: every day at 06:00                                │
│    Scrapers: All enabled scrapers                               │
│    Next Run: Tomorrow at 06:00 (in 19h 25m)                    │
│    [Edit] [Disable] [Run Now]                                  │
│                                                                  │
│  > Weekly Deep Dive                                [ENABLED]    │
│    Schedule: every monday at 09:00                             │
│    Scrapers: ArXiv only (extended search)                       │
│    Next Run: Monday at 09:00 (in 2 days)                       │
│    [Edit] [Disable] [Run Now]                                  │
│                                                                  │
│  > Frequent Updates                                [ENABLED]    │
│    Schedule: every 4 hours                                     │
│    Scrapers: HackerNews, Reddit                                │
│    Next Run: Today at 14:00 (in 3h 15m)                        │
│    [Edit] [Disable] [Run Now]                                  │
│                                                                  │
│  [Add Schedule] [Back]                                          │
└──────────────────────────────────────────────────────────────────┘

When editing a schedule:
┌─ Edit Schedule: Daily Digest Run ───────────────────────────────┐
│                                                                  │
│  Frequency:                                                      │
│    [●] Time-based (specific time each day/week)                 │
│    [ ] Interval-based (every N hours/minutes)                   │
│                                                                  │
│  When:                                                           │
│    Run: [every day    ▼] at [06:00]                            │
│                                                                  │
│  Schedule Preview: "every day at 06:00"  ✓ Valid               │
│                                                                  │
│  Scrapers to Run:                                               │
│    [✓] ArXiv    [✓] HackerNews    [✓] Reddit    [✓] RSS        │
│                                                                  │
│  [Save] [Cancel] [Test Run]                                    │
└──────────────────────────────────────────────────────────────────┘
```

**Features:**
- Visual schedule builder generates valid `schedule` strings
- Leverages existing `scheduler_utils.setup_schedule()` and validation
- Natural language preview (no cron knowledge needed)
- Per-scraper or grouped schedules
- Manual trigger option
- Dropdown helpers:
  - "every day", "every monday", "every 4 hours", etc.
  - Time picker (HH:MM format)
  - Validation as you type

---

## Technical Architecture

### Core Technologies

#### 1. Textual (TUI Framework)

**Why Textual?**
- Built on Rich (already in use)
- Modern, reactive framework
- CSS-like styling system
- Excellent documentation
- Active development
- Async-native (works with current httpx usage)

#### 2. schedule (Scheduling) - Already In Use! ✅

**Current Implementation:**
The project already uses the `schedule` library in `scheduler_utils.py` with a safe, validated parser. This is perfect for the TUI!

**Why schedule is ideal:**
- Natural language syntax: `"every 4 hours"`, `"every day at 10:30"`
- Already validated and security-hardened (no eval, injection-safe)
- Easy to serialize for UI forms
- User-friendly (no cron knowledge needed)
- Existing `setup_schedule()` function ready to use

**TUI Integration:**
The scheduler screen will provide visual forms that generate valid schedule strings, making it even easier than typing them manually.

#### 3. Polars (Data Analytics) - NEW

**Why Polars?**
- **Performance**: 5-10x faster than pandas for large datasets
- **Memory efficiency**: Rust-based, lower memory footprint
- **Modern API**: Intuitive query syntax
- **SQLite integration**: Direct queries from database
- **Analytics**: Perfect for history/trends screens

**Use Cases in TUI:**
- History screen: Aggregate items by source, date, topic
- Trend analysis: Track collection patterns over time
- Export functionality: CSV, Parquet, JSON exports
- Real-time charts: Bar graphs, time series
- Search: Fast full-text search across collected items

**Installation:**
```toml
[project.dependencies]
textual = "^0.85.0"
polars = "^0.20.0"  # For data analytics
schedule = "^1.2.0"  # Already in use
```

### Application Structure

```
research_digest_tui/
├── __init__.py
├── app.py                    # Main TUI application
├── screens/
│   ├── __init__.py
│   ├── dashboard.py          # Main dashboard screen
│   ├── scraper_management.py # Scraper list/control
│   ├── configuration.py      # Config editor
│   ├── logs.py               # Log viewer
│   ├── history.py            # Analytics/history
│   └── scheduler.py          # Schedule manager
├── widgets/
│   ├── __init__.py
│   ├── scraper_card.py       # Individual scraper widget
│   ├── progress_panel.py     # Progress display
│   ├── config_form.py        # Dynamic form generator
│   ├── log_viewer.py         # Log display widget
│   └── chart.py              # ASCII/Unicode charts
├── services/
│   ├── __init__.py
│   ├── scraper_runner.py     # Background scraper execution
│   ├── config_manager.py     # YAML read/write
│   ├── log_aggregator.py     # Collect logs from scrapers
│   └── scheduler_service.py  # Schedule management
└── models/
    ├── __init__.py
    ├── app_state.py          # Global application state
    └── events.py             # Custom Textual events
```

### Key Design Patterns

#### 1. Reactive State Management

Use Textual's reactive system to auto-update UI:

```python
from textual.reactive import reactive

class ScraperCard(Widget):
    status = reactive("idle")  # Auto-updates UI when changed
    progress = reactive(0.0)

    def watch_status(self, new_status: str):
        """Called automatically when status changes"""
        self.update_display()
```

#### 2. Background Task Execution

Run scrapers in background without blocking UI:

```python
from textual import work

class ScraperRunner:
    @work(exclusive=True, thread=True)
    async def run_scraper(self, scraper_name: str):
        """Runs in background thread"""
        # Existing scraper logic
        # Post updates via events
        self.post_message(ScraperProgress(name=scraper_name, progress=0.5))
```

#### 3. Event-Driven Communication

Custom events for cross-widget communication:

```python
from textual.message import Message

class ScraperStarted(Message):
    def __init__(self, scraper_name: str):
        self.scraper_name = scraper_name
        super().__init__()

class ScraperProgress(Message):
    def __init__(self, scraper_name: str, progress: float, message: str):
        self.scraper_name = scraper_name
        self.progress = progress
        self.message = message
        super().__init__()
```

#### 4. Configuration Bridge

Bridge between Pydantic models and UI forms:

```python
from config_models import ArxivConfig

class ConfigEditor:
    def model_to_form(self, config: ArxivConfig) -> dict:
        """Convert Pydantic model to form fields"""
        return {
            "enabled": config.enabled,
            "days_back": config.days_back,
            "search_queries": config.search_queries
        }

    def form_to_model(self, form_data: dict) -> ArxivConfig:
        """Convert form back to Pydantic model (validates!)"""
        return ArxivConfig(**form_data)
```

#### 5. Polars for Analytics

Use Polars to query and analyze collection data efficiently:

```python
import polars as pl
from pathlib import Path

class AnalyticsService:
    def __init__(self, db_path: Path):
        """Initialize with SQLite database path"""
        self.db_uri = f"sqlite:///{db_path}"

    def get_collection_stats(self, days: int = 7) -> pl.DataFrame:
        """Get collection statistics for the last N days"""
        query = f"""
            SELECT
                source_type,
                DATE(timestamp) as date,
                COUNT(*) as item_count
            FROM items
            WHERE timestamp >= datetime('now', '-{days} days')
            GROUP BY source_type, date
            ORDER BY date DESC, source_type
        """
        return pl.read_database(query, self.db_uri)

    def get_source_distribution(self) -> dict[str, int]:
        """Get total items by source"""
        df = pl.read_database(
            "SELECT source_type, COUNT(*) as count FROM items GROUP BY source_type",
            self.db_uri
        )
        return dict(zip(df["source_type"], df["count"]))

    def get_daily_trend(self, days: int = 30) -> pl.DataFrame:
        """Get daily collection trends"""
        query = f"""
            SELECT
                DATE(timestamp) as date,
                COUNT(*) as total_items,
                COUNT(DISTINCT source_type) as active_sources
            FROM items
            WHERE timestamp >= datetime('now', '-{days} days')
            GROUP BY date
            ORDER BY date
        """
        return pl.read_database(query, self.db_uri)

    def export_to_csv(self, df: pl.DataFrame, output_path: Path):
        """Export DataFrame to CSV"""
        df.write_csv(output_path)

    def search_content(self, keyword: str, limit: int = 100) -> pl.DataFrame:
        """Fast full-text search across collected items"""
        query = f"""
            SELECT source_type, title, url, timestamp
            FROM items
            WHERE title LIKE '%{keyword}%' OR content LIKE '%{keyword}%'
            ORDER BY timestamp DESC
            LIMIT {limit}
        """
        return pl.read_database(query, self.db_uri)
```

**Performance Benefits:**
- Queries return results 5-10x faster than pandas for large datasets (10k+ items)
- Lower memory usage (important for TUI running in terminal)
- Native date/time handling
- Built-in chart-ready data structures

### Technology Synergy

**Why `schedule` + Polars + Textual is the Perfect Combo:**

| Component | Role | Benefit |
|-----------|------|---------|
| **Textual** | TUI framework | Modern, reactive UI built on Rich (already in use) |
| **schedule** | Job scheduling | Already integrated, natural language syntax, user-friendly |
| **Polars** | Data analytics | Fast queries for large datasets, perfect for history/trends |
| **Rich** | Terminal output | Foundation for Textual, already styling scraper output |
| **Pydantic** | Config models | Type-safe config validation (already in use) |

**User Experience Flow:**

1. User opens TUI → sees dashboard with real-time stats (Polars queries)
2. User edits schedule → visual form generates `"every day at 06:00"` string
3. TUI validates using `scheduler_utils.parse_schedule_string()` → instant feedback
4. User saves → config persists, schedule starts running
5. User views history → Polars aggregates 10k+ items in milliseconds
6. User exports data → Polars writes CSV/Parquet efficiently

**No Reinventing the Wheel:**
- `schedule` library: proven, well-maintained, already integrated ✅
- Polars: modern standard for fast data processing ✅
- Textual: official Rich framework for TUIs ✅

---

## Implementation Phases

### Phase 1: Foundation (Week 1-2)

**Goal:** Basic TUI shell with navigation

- [ ] Install Textual, create basic app structure
- [ ] Implement dashboard screen (static, no real data)
- [ ] Add navigation between Dashboard/Scrapers/Config screens
- [ ] Create scraper card widgets (static)
- [ ] Basic CSS styling

**Deliverables:**
- Navigable TUI with placeholder screens
- Visual design established
- No backend integration yet

### Phase 2: Read-Only Integration (Week 3-4)

**Goal:** Display real data from existing system

- [ ] Integrate `research_config.yaml` reading
- [ ] Display actual scraper configurations
- [ ] Set up Polars integration with SQLite database
- [ ] Show database statistics (item counts, last run times) using Polars queries
- [ ] Implement log viewer (read from log files)
- [ ] Add history/analytics screen with Polars-powered charts and aggregations

**Deliverables:**
- TUI displays actual config and data
- Users can browse but not modify
- Fast analytics queries via Polars (handles 10k+ items efficiently)

### Phase 3: Interactive Controls (Week 5-6)

**Goal:** Enable scraper execution from TUI

- [ ] Implement "Run Now" for individual scrapers
- [ ] Background task execution (non-blocking)
- [ ] Real-time progress updates
- [ ] Live log streaming
- [ ] Error handling and display

**Deliverables:**
- Users can run scrapers from TUI
- Real-time feedback during execution
- Logs update live

### Phase 4: Configuration Management (Week 7-8)

**Goal:** Edit configuration through UI

- [ ] Build dynamic form generator for config models
- [ ] Implement config editor for each scraper
- [ ] Add validation with helpful error messages
- [ ] YAML file read/write
- [ ] Configuration testing (validate before save)

**Deliverables:**
- Users can edit all settings via TUI
- Configuration changes persist to YAML
- No need to manually edit files

### Phase 5: Scheduling & Automation (Week 9-10)

**Goal:** Schedule management UI

- [ ] Build visual schedule editor that generates `schedule` strings
- [ ] Integrate with existing `scheduler_utils.setup_schedule()` and validation
- [ ] Display existing schedules with next-run times
- [ ] Add/edit/delete schedules (writes to config file)
- [ ] Dropdown helpers for common patterns ("every day", "every 4 hours", etc.)
- [ ] Time picker for HH:MM format
- [ ] Real-time validation using `scheduler_utils.parse_schedule_string()`
- [ ] Manual trigger for scheduled tasks

**Deliverables:**
- Full schedule management via TUI
- Natural language scheduling (no cron knowledge needed)
- Leverages existing, battle-tested `schedule` library

### Phase 6: Polish & Testing (Week 11-12)

**Goal:** Production-ready release

- [ ] Comprehensive testing (unit + integration)
- [ ] Performance testing with large datasets:
  - Test Polars queries with 10k, 50k, 100k items
  - Benchmark history screen load times
  - Optimize chart rendering for large data
- [ ] Performance optimization (large log files, many items)
- [ ] Keyboard shortcuts & accessibility
- [ ] Help system & tooltips
- [ ] Error recovery & graceful degradation
- [ ] Documentation & user guide
- [ ] Test schedule validation edge cases (using existing test suite)

**Deliverables:**
- ≥80% test coverage for TUI code
- Performance benchmarks showing Polars benefits
- User documentation
- Release v2.0.0

---

### Phase 7: RSS Feed Management UI (To Be Planned)

**Goal:** Make it easy to add, remove, and manage RSS feeds through the TUI without manually editing YAML.

**Background:** RSS feeds are currently configured by hand-editing `research_config.yaml` under `scrapers.rss.feeds`. This is error-prone and invisible to new users. A dedicated feed management flow in the TUI would lower the barrier significantly.

**Candidate features (to be detailed during planning):**
- Add feed by pasting a URL — auto-detect feed URL from site URL if needed
- Validate feed URL before saving (attempt fetch, check for valid RSS/Atom)
- Display feed name, URL, tags, and last-fetched count in the Scraper Management screen
- Edit/remove existing feeds in place
- Tag suggestions based on feed content or user-defined topics
- Import OPML files (common export format from feed readers like Feedly, NewsBlur)

**Dependencies:** Phase 4 (Config Management UI must exist to persist feed changes)

**Open questions for planning:**
- Should feed discovery (auto-detect from site URL) be attempted? Needs HTTP fetch at add-time.
- Is OPML import in scope for the first iteration or a follow-on?

---

### Phase 8: Proton Pass CLI Integration for Password-Protected Sources (To Be Planned)

**Goal:** Allow users to optionally configure Proton Pass CLI as a credential provider so that password-protected content sources (e.g., Medium member-only articles) can be scraped using stored credentials.

**Background:** Some high-value research sources sit behind paywalls or login walls (Medium, Substack paid tiers, private newsletters). Proton Pass CLI (`pass`) can serve credentials from the user's encrypted vault without exposing passwords in config files or environment variables.

**Candidate features (to be detailed during planning):**
- Optional setup wizard in TUI: detect if `proton-pass` CLI is installed, guide user through linking
- Per-scraper credential mapping: associate a Proton Pass secret path with a scraper config entry
- Credential retrieval at scrape-time (not stored in `research_config.yaml`)
- TUI indicator showing which scrapers have credentials configured
- Graceful fallback: if Proton Pass is unavailable, skip credentialed sources with a clear warning rather than crashing
- Medium scraper plugin as the first concrete use case (login-based article fetching)

**Dependencies:** Phase 6 complete (stable v2.0.0 before adding optional credential layer); Proton Pass CLI must be available on the user's system

**Open questions for planning:**
- Which Proton Pass CLI version/API to target? (`proton-pass export`? `pass show`?)
- Should credential fetching be synchronous at startup or lazy (fetched only when scraper runs)?
- Are there other password managers worth supporting as alternatives (1Password CLI, Bitwarden CLI)?
- What is the scope of the Medium scraper plugin itself — is that a separate spec?

---

## Migration Strategy

### Dual-Mode Operation

Maintain both CLI and TUI during transition:

```bash
# CLI mode (existing)
python research_digest.py --config research_config.yaml

# TUI mode (new)
python research_digest.py --tui
# or
python research_digest_tui.py
```

### Gradual Adoption

- v2.0.0: TUI available, CLI still default
- v2.1.0: TUI becomes default, CLI via `--cli` flag
- v3.0.0: CLI deprecated, TUI only

### Configuration Compatibility

- Same `research_config.yaml` format
- TUI reads/writes to existing config
- No breaking changes to config schema
- Existing automations continue working

---

## Testing Strategy

### Unit Tests

Test individual widgets and components:

```python
from textual.widgets import Button
from research_digest_tui.widgets import ScraperCard

async def test_scraper_card_status_change():
    """Test that scraper card updates when status changes"""
    card = ScraperCard(name="ArXiv", status="idle")

    # Change status
    card.status = "running"

    # Verify UI updated
    assert "running" in card.render().plain.lower()
```

### Integration Tests

Test full screens and interactions:

```python
from textual.app import App
from research_digest_tui.screens import Dashboard

async def test_dashboard_scraper_run():
    """Test running scraper from dashboard"""
    app = App()
    app.push_screen(Dashboard())

    # Simulate user clicking "Run" button
    await app.pilot.click("#arxiv-run-button")

    # Verify scraper started
    assert app.scraper_runner.is_running("arxiv")
```

### Snapshot Testing

Use Textual's snapshot testing for visual regression:

```python
async def test_dashboard_snapshot(snap_compare):
    """Dashboard renders correctly"""
    assert await snap_compare("dashboard.svg")
```

### Manual Testing Checklist

- [ ] All screens navigable via keyboard
- [ ] Progress bars update smoothly
- [ ] Logs scroll properly with large files
- [ ] Config validation shows helpful errors
- [ ] Works in different terminal sizes (80x24, 120x40, 200x60)
- [ ] Dark/light theme support
- [ ] Handles rapid scraper state changes
- [ ] Graceful handling of config file errors

---

## Risks & Mitigations

### Risk 1: Performance with Large Datasets

**Risk:** TUI becomes sluggish with 10,000+ log lines or items

**Mitigation:**
- Implement virtual scrolling (only render visible rows)
- Pagination for large lists
- Background loading with loading indicators
- Database queries with LIMIT/OFFSET

### Risk 2: Terminal Compatibility

**Risk:** TUI doesn't work in all terminals (Windows CMD, older terminals)

**Mitigation:**
- Test on Windows Terminal, iTerm2, GNOME Terminal, kitty
- Graceful degradation (disable features if unsupported)
- Keep CLI mode for compatibility
- Document minimum terminal requirements

### Risk 3: Complexity Creep

**Risk:** TUI becomes overly complex, hard to maintain

**Mitigation:**
- Strict adherence to Textual best practices
- Comprehensive unit tests for widgets
- Regular code reviews
- Keep business logic separate from UI logic
- Reuse existing backend (database, retry logic, etc.)

### Risk 4: Learning Curve

**Risk:** Users find TUI confusing

**Mitigation:**
- In-app help system
- Tooltips and hints
- Logical, consistent navigation
- Video tutorials/GIFs in documentation
- Beta testing with real users

### Risk 5: Breaking Changes

**Risk:** TUI requires breaking changes to existing code

**Mitigation:**
- Maintain backward compatibility with config format
- Keep CLI mode operational
- Create TUI as separate module (no refactoring of core logic)
- Gradual migration path

---

## Success Criteria

### Must Have (MVP)

- [ ] Dashboard with real-time scraper status
- [ ] Run scrapers individually or all at once
- [ ] View logs with filtering
- [ ] Edit configuration for all scrapers
- [ ] Save config changes to YAML
- [ ] All existing functionality available via TUI

### Should Have (v2.1)

- [ ] Scheduler management UI
- [ ] History/analytics screen
- [ ] Export functionality (logs, data)
- [ ] Help system
- [ ] Keyboard shortcuts

### Nice to Have (v2.2+)

- [ ] Custom themes
- [ ] Plugin management (add/remove scrapers visually)
- [ ] Notification system (desktop notifications for errors)
- [ ] Remote monitoring (TUI server mode)
- [ ] Search across collected content

---

## Documentation Requirements

### User Documentation

1. **Installation Guide**: TUI-specific dependencies
2. **Quick Start Tutorial**: 5-minute walkthrough
3. **Screen Reference**: What each screen does
4. **Keyboard Shortcuts**: Full list with mnemonics
5. **Troubleshooting**: Common issues and fixes

### Developer Documentation

1. **Architecture Overview**: How TUI integrates with existing code
2. **Widget Catalog**: Reusable components
3. **Adding Screens**: How to create new screens
4. **Testing Guide**: How to write TUI tests
5. **Performance Best Practices**: Virtual scrolling, async patterns

---

## Timeline & Milestones

| Milestone | Target Date | Deliverables |
|-----------|-------------|--------------|
| Phase 1: Foundation | Week 2 | Navigable TUI shell |
| Phase 2: Read Integration | Week 4 | Display real data |
| Phase 3: Interactive Controls | Week 6 | Run scrapers from TUI |
| Phase 4: Config Management | Week 8 | Edit configs via TUI |
| Phase 5: Scheduling | Week 10 | Schedule management |
| Phase 6: Polish & Release | Week 12 | v2.0.0 release |

**Total Estimated Timeline:** 12 weeks (3 months)

---

## Open Questions

1. **Desktop Notifications?** Should we integrate with system notifications for errors/completion?
2. **Remote Access?** Should TUI support running on a server and connecting remotely?
3. **Mouse Support?** Clickable UI elements or keyboard-only?
4. **Theme Customization?** Allow users to customize colors/layout?
5. **Multi-User?** Support for multiple users with different configs?

---

## Next Steps

1. **User Feedback**: Share mockups with potential users
2. **Proof of Concept**: Build dashboard screen (Phase 1 subset) to validate approach
3. **Dependency Review**: Test Textual in target environments
4. **Resource Allocation**: Assign developer time/effort
5. **Kickoff Meeting**: Review spec, finalize timeline

---

## References

- [Textual Documentation](https://textual.textualize.io/)
- [Textual GitHub Examples](https://github.com/Textualize/textual)
- [Rich Documentation](https://rich.readthedocs.io/) (foundation for Textual)
- [TUI Design Patterns](https://textual.textualize.io/guide/)
- Current codebase: `research_digest.py`, `scheduler_utils.py`, `config_models.py`
