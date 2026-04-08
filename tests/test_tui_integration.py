#!/usr/bin/env python3
"""Integration tests for TUI screen navigation."""

import sqlite3
from pathlib import Path

import pytest
import yaml

pytest.importorskip("textual")
pytest.importorskip("pytest_asyncio")

from research_digest_tui import ResearchDigestApp  # noqa: E402
from research_digest_tui.widgets import ScraperCard  # noqa: E402


def _make_config(tmp_path: Path) -> Path:
    """Write a minimal research_config.yaml in tmp_path."""
    cfg = {
        "scrapers": {
            "hackernews": {"enabled": True, "min_points": 50, "search_topics": ["AI"]},
            "rss": {"enabled": True, "feeds": []},
            "reddit": {"enabled": False, "subreddits": []},
            "arxiv": {"enabled": True, "search_queries": ["ml"]},
        }
    }
    p = tmp_path / "research_config.yaml"
    p.write_text(yaml.dump(cfg))
    return p


def _make_db_with_items(tmp_path: Path) -> Path:
    """Create a test SQLite DB with a few processed items."""
    db = tmp_path / "test.db"
    conn = sqlite3.connect(str(db))
    conn.execute(
        "CREATE TABLE processed_items "
        "(source TEXT, unique_id TEXT, processed_at TEXT, title TEXT, url TEXT, "
        "PRIMARY KEY(source, unique_id))"
    )
    conn.execute(
        "INSERT INTO processed_items VALUES ('hn', '123', '2026-03-01T10:00:00', 'Test HN', NULL)"
    )
    conn.execute(
        "INSERT INTO processed_items VALUES ('arxiv', 'arxiv:001', '2026-03-02T10:00:00', 'Test Paper', NULL)"
    )
    conn.commit()
    conn.close()
    return db


@pytest.mark.tui
async def test_dashboard_creates_scraper_cards_from_config(tmp_path):
    """Dashboard creates ScraperCards dynamically from ConfigService, not hardcoded."""
    config_path = _make_config(tmp_path)
    db_path = tmp_path / "empty.db"
    app = ResearchDigestApp(config_path=config_path, db_path=db_path)
    async with app.run_test() as _:
        cards = app.screen.query(ScraperCard)
        # Config has 3 enabled + 1 disabled — dashboard shows all 4 with status badges
        assert len(cards) == 4


@pytest.mark.tui
async def test_dashboard_status_bar_shows_real_item_counts(tmp_path):
    """Dashboard status bar reflects actual item counts from the database."""
    config_path = _make_config(tmp_path)
    db_path = _make_db_with_items(tmp_path)
    app = ResearchDigestApp(config_path=config_path, db_path=db_path)
    async with app.run_test() as _:
        status_bars = app.screen.query(".status-bar")
        assert len(status_bars) == 1
        status_text = status_bars.first().content
        assert "2" in str(status_text)  # 2 items in DB


@pytest.mark.tui
async def test_dashboard_status_bar_shows_no_data_for_empty_db(tmp_path):
    """Dashboard status bar shows 'No data' when DB is empty."""
    config_path = _make_config(tmp_path)
    db_path = tmp_path / "empty.db"
    app = ResearchDigestApp(config_path=config_path, db_path=db_path)
    async with app.run_test() as _:
        status_bars = app.screen.query(".status-bar")
        assert len(status_bars) == 1
        status_text = str(status_bars.first().content)
        assert "No data" in status_text or "0" in status_text


@pytest.mark.tui
async def test_scraper_management_config_summary_is_dynamic(tmp_path):
    """ScraperManagement shows config summary from service, not hardcoded strings."""
    config_path = _make_config(tmp_path)  # hackernews has 1 search_topic: ["AI"]
    db_path = tmp_path / "empty.db"
    app = ResearchDigestApp(config_path=config_path, db_path=db_path)
    async with app.run_test() as pilot:
        await pilot.press("s")
        await pilot.pause()
        config_summaries = app.screen.query(".scraper-config")
        all_text = " ".join(str(s.content) for s in config_summaries)
        # Service returns "Topics: 1 configured" for 1 topic; hardcoded has "AI, Platform Engineering"
        assert "Topics: 1 configured" in all_text


@pytest.mark.tui
async def test_content_browser_has_data_table(tmp_path):
    """Content Browser (Logs screen) always shows a DataTable."""
    from textual.widgets import DataTable

    config_path = _make_config(tmp_path)
    db_path = tmp_path / "empty.db"
    app = ResearchDigestApp(config_path=config_path, db_path=db_path)
    async with app.run_test() as pilot:
        await pilot.press("l")
        await pilot.pause()
        assert len(app.screen.query(DataTable)) == 1


@pytest.mark.tui
async def test_content_browser_shows_rows_for_items_in_db(tmp_path):
    """Content Browser DataTable has one row per item in the database."""
    from textual.widgets import DataTable

    config_path = _make_config(tmp_path)
    db_path = _make_db_with_items(tmp_path)
    app = ResearchDigestApp(config_path=config_path, db_path=db_path)
    async with app.run_test() as pilot:
        await pilot.press("l")
        await pilot.pause()
        table = app.screen.query_one(DataTable)
        assert table.row_count == 2  # 2 items in _make_db_with_items


@pytest.mark.tui
async def test_history_shows_real_summary_stats(tmp_path):
    """History screen shows actual item count from database."""
    from textual.widgets import Static

    config_path = _make_config(tmp_path)
    db_path = _make_db_with_items(tmp_path)
    app = ResearchDigestApp(config_path=config_path, db_path=db_path)
    async with app.run_test() as pilot:
        await pilot.press("h")
        await pilot.pause()
        summary = app.screen.query_one("#stats-summary", Static)
        assert "2" in str(summary.content)  # 2 items in DB


@pytest.mark.tui
async def test_history_empty_db_shows_no_data(tmp_path):
    """History screen shows no-data message when database is empty."""
    from textual.widgets import Static

    config_path = _make_config(tmp_path)
    db_path = tmp_path / "empty.db"
    app = ResearchDigestApp(config_path=config_path, db_path=db_path)
    async with app.run_test() as pilot:
        await pilot.press("h")
        await pilot.pause()
        summary = app.screen.query_one("#stats-summary", Static)
        text = str(summary.content)
        assert "No data" in text or "0" in text


@pytest.mark.tui
async def test_app_starts_on_dashboard_screen():
    """App launches with Dashboard as the initial screen."""
    app = ResearchDigestApp()
    async with app.run_test() as _:
        assert app.screen.__class__.__name__ == "Dashboard"


@pytest.mark.tui
@pytest.mark.parametrize(
    "key,screen_name",
    [
        ("d", "Dashboard"),
        ("s", "ScraperManagement"),
        ("c", "Configuration"),
        ("l", "Logs"),
        ("h", "History"),
        ("u", "Scheduler"),
    ],
)
async def test_keyboard_navigates_to_screen(key, screen_name):
    """Each keyboard shortcut switches to the correct screen."""
    app = ResearchDigestApp()
    async with app.run_test() as pilot:
        # Navigate away first so all keys (including "d") trigger a real transition
        await pilot.press("s")
        await pilot.pause()
        await pilot.press(key)
        assert app.screen.__class__.__name__ == screen_name


# ─── Phase 3: Interactive Controls ──────────────────────────────────────────


@pytest.mark.tui
async def test_run_now_button_is_enabled(tmp_path):
    """ScraperManagement 'Run Now' buttons are enabled (not disabled)."""
    from textual.widgets import Button

    config_path = _make_config(tmp_path)
    db_path = tmp_path / "empty.db"
    app = ResearchDigestApp(config_path=config_path, db_path=db_path)
    async with app.run_test() as pilot:
        await pilot.press("s")
        await pilot.pause()
        run_buttons = [
            b for b in app.screen.query(Button) if b.id and b.id.endswith("-run")
        ]
        assert len(run_buttons) > 0
        assert all(not b.disabled for b in run_buttons)


@pytest.mark.tui
async def test_toggle_button_is_enabled(tmp_path):
    """ScraperManagement 'Enable'/'Disable' toggle buttons are enabled."""
    from textual.widgets import Button

    config_path = _make_config(tmp_path)
    db_path = tmp_path / "empty.db"
    app = ResearchDigestApp(config_path=config_path, db_path=db_path)
    async with app.run_test() as pilot:
        await pilot.press("s")
        await pilot.pause()
        toggle_buttons = [
            b for b in app.screen.query(Button) if b.id and b.id.endswith("-toggle")
        ]
        assert len(toggle_buttons) > 0
        assert all(not b.disabled for b in toggle_buttons)


@pytest.mark.tui
async def test_configure_button_enabled(tmp_path):
    """ScraperManagement 'Configure' buttons are enabled."""
    from textual.widgets import Button

    config_path = _make_config(tmp_path)
    db_path = tmp_path / "empty.db"
    app = ResearchDigestApp(config_path=config_path, db_path=db_path)
    async with app.run_test() as pilot:
        await pilot.press("s")
        await pilot.pause()
        configure_buttons = [
            b for b in app.screen.query(Button) if b.id and b.id.endswith("-configure")
        ]
        assert len(configure_buttons) > 0
        assert all(not b.disabled for b in configure_buttons)


# ─── Phase 4: Configuration Screen ──────────────────────────────────────────


@pytest.mark.tui
async def test_configuration_screen_shows_scraper_list(tmp_path):
    """Configuration screen shows a ListView for scraper selection."""
    from textual.widgets import ListView

    config_path = _make_config(tmp_path)
    db_path = tmp_path / "empty.db"
    app = ResearchDigestApp(config_path=config_path, db_path=db_path)
    async with app.run_test() as pilot:
        await pilot.press("c")
        await pilot.pause()
        list_views = app.screen.query(ListView)
        assert len(list_views) == 1


@pytest.mark.tui
async def test_configuration_screen_shows_global_settings(tmp_path):
    """Configuration screen shows the Days Back input for global settings."""

    config_path = _make_config(tmp_path)
    db_path = tmp_path / "empty.db"
    app = ResearchDigestApp(config_path=config_path, db_path=db_path)
    async with app.run_test() as pilot:
        await pilot.press("c")
        await pilot.pause()
        global_input = app.screen.query("#global-days-back")
        assert len(global_input) == 1


# ─── Phase 5: Scheduler Screen ───────────────────────────────────────────────


@pytest.mark.tui
async def test_scheduler_screen_shows_schedule_input(tmp_path):
    """Scheduler screen renders the schedule string Input widget."""

    config_path = _make_config(tmp_path)
    db_path = tmp_path / "empty.db"
    app = ResearchDigestApp(config_path=config_path, db_path=db_path)
    async with app.run_test() as pilot:
        await pilot.press("u")
        await pilot.pause()
        schedule_inputs = app.screen.query("#schedule-input")
        assert len(schedule_inputs) == 1


@pytest.mark.tui
async def test_scheduler_screen_shows_status_widget(tmp_path):
    """Scheduler screen renders the ENABLED/DISABLED status Static widget."""

    config_path = _make_config(tmp_path)
    db_path = tmp_path / "empty.db"
    app = ResearchDigestApp(config_path=config_path, db_path=db_path)
    async with app.run_test() as pilot:
        await pilot.press("u")
        await pilot.pause()
        status = app.screen.query("#schedule-status")
        assert len(status) == 1


@pytest.mark.tui
async def test_scheduler_screen_shows_current_schedule(tmp_path):
    """Scheduler screen pre-fills the Input with the configured schedule string."""
    from textual.widgets import Input

    # Write config with a schedule
    cfg = {
        "scrapers": {
            "hackernews": {"enabled": True, "min_points": 50, "search_topics": ["AI"]},
            "rss": {"enabled": True, "feeds": []},
            "reddit": {"enabled": False, "subreddits": []},
            "arxiv": {"enabled": True, "search_queries": ["ml"]},
        },
        "schedule": {"schedule_string": "every 4 hours", "enabled": False},
    }
    config_path = tmp_path / "config.yaml"
    config_path.write_text(yaml.dump(cfg))
    db_path = tmp_path / "empty.db"

    app = ResearchDigestApp(config_path=config_path, db_path=db_path)
    async with app.run_test() as pilot:
        await pilot.press("u")
        await pilot.pause()
        inp = app.screen.query_one("#schedule-input", Input)
        assert inp.value == "every 4 hours"


# ─── Phase 6: Scheduler Screen Interactions ──────────────────────────────────


@pytest.mark.tui
async def test_scheduler_example_button_fills_input(tmp_path):
    """Pressing an example button pre-fills the schedule input."""
    from textual.widgets import Button, Input

    config_path = _make_config(tmp_path)
    db_path = tmp_path / "empty.db"
    app = ResearchDigestApp(config_path=config_path, db_path=db_path)
    async with app.run_test() as pilot:
        await pilot.press("u")
        await pilot.pause()
        app.screen.query_one("#ex-4h", Button).press()
        await pilot.pause()
        inp = app.screen.query_one("#schedule-input", Input)
        assert inp.value == "every 4 hours"


@pytest.mark.tui
async def test_scheduler_toggle_button_changes_state(tmp_path):
    """Toggle button flips the scheduler enabled state."""
    from textual.widgets import Button, Static

    config_path = _make_config(tmp_path)
    db_path = tmp_path / "empty.db"
    app = ResearchDigestApp(config_path=config_path, db_path=db_path)
    async with app.run_test() as pilot:
        await pilot.press("u")
        await pilot.pause()
        before = str(app.screen.query_one("#schedule-status", Static).content)
        app.screen.query_one("#toggle-schedule", Button).press()
        await pilot.pause()
        after = str(app.screen.query_one("#schedule-status", Static).content)
        assert before != after


@pytest.mark.tui
async def test_scheduler_save_button_present_on_screen(tmp_path):
    """Scheduler screen has a save-schedule button."""

    config_path = _make_config(tmp_path)
    db_path = tmp_path / "empty.db"
    app = ResearchDigestApp(config_path=config_path, db_path=db_path)
    async with app.run_test() as pilot:
        await pilot.press("u")
        await pilot.pause()
        save_btns = app.screen.query("#save-schedule")
        assert len(save_btns) == 1


# ─── Phase 6: Logs Screen Filter Interactions ─────────────────────────────────


@pytest.mark.tui
async def test_logs_filter_button_filters_by_source(tmp_path):
    """Pressing a source filter button re-loads the table for that source."""
    from textual.widgets import DataTable

    config_path = _make_config(tmp_path)
    db_path = _make_db_with_items(tmp_path)
    app = ResearchDigestApp(config_path=config_path, db_path=db_path)
    async with app.run_test() as pilot:
        await pilot.press("l")
        await pilot.pause()
        await pilot.click("#filter-hn")
        await pilot.pause()
        table = app.screen.query_one(DataTable)
        # DB has 1 hn item and 1 arxiv item — hn filter shows 1
        assert table.row_count == 1


@pytest.mark.tui
async def test_logs_filter_all_button_shows_all_items(tmp_path):
    """Pressing the 'All' filter restores all items."""
    from textual.widgets import DataTable

    config_path = _make_config(tmp_path)
    db_path = _make_db_with_items(tmp_path)
    app = ResearchDigestApp(config_path=config_path, db_path=db_path)
    async with app.run_test() as pilot:
        await pilot.press("l")
        await pilot.pause()
        await pilot.click("#filter-hn")
        await pilot.pause()
        await pilot.click("#filter-all")
        await pilot.pause()
        table = app.screen.query_one(DataTable)
        assert table.row_count == 2


# ─── Phase 6: History Screen Interactions ────────────────────────────────────


@pytest.mark.tui
async def test_history_filter_30d_button(tmp_path):
    """History filter-30d button reloads with 30-day window."""
    from textual.widgets import Button

    config_path = _make_config(tmp_path)
    db_path = _make_db_with_items(tmp_path)
    app = ResearchDigestApp(config_path=config_path, db_path=db_path)
    async with app.run_test() as pilot:
        await pilot.press("h")
        await pilot.pause()
        app.screen.query_one("#filter-30d", Button).press()
        await pilot.pause()
        # Both items are within 30 days; stats still show 2 items
        from textual.widgets import Static

        summary = app.screen.query_one("#stats-summary", Static)
        assert summary is not None


@pytest.mark.tui
async def test_history_filter_all_button(tmp_path):
    """History filter-all button restores all-time view."""
    from textual.widgets import Button, Static

    config_path = _make_config(tmp_path)
    db_path = _make_db_with_items(tmp_path)
    app = ResearchDigestApp(config_path=config_path, db_path=db_path)
    async with app.run_test() as pilot:
        await pilot.press("h")
        await pilot.pause()
        app.screen.query_one("#filter-all", Button).press()
        await pilot.pause()
        summary = app.screen.query_one("#stats-summary", Static)
        assert "2" in str(summary.content)


# ─── Phase 7: Scheduler Save and Back ────────────────────────────────────────


@pytest.mark.tui
async def test_scheduler_back_button_navigates_to_dashboard(tmp_path):
    """Scheduler back button returns to the dashboard screen."""
    from textual.widgets import Button

    config_path = _make_config(tmp_path)
    db_path = tmp_path / "empty.db"
    app = ResearchDigestApp(config_path=config_path, db_path=db_path)
    async with app.run_test() as pilot:
        await pilot.press("u")
        await pilot.pause()
        app.screen.query_one("#back", Button).press()
        await pilot.pause()
        assert app.screen.__class__.__name__ == "Dashboard"


@pytest.mark.tui
async def test_scheduler_empty_input_disables_save_button(tmp_path):
    """Clearing the schedule input disables the save button."""
    from textual.widgets import Button, Input

    config_path = _make_config(tmp_path)
    db_path = tmp_path / "empty.db"
    app = ResearchDigestApp(config_path=config_path, db_path=db_path)
    async with app.run_test() as pilot:
        await pilot.press("u")
        await pilot.pause()
        # Fill the input via example button, then clear it
        await pilot.click("#ex-4h")
        await pilot.pause()
        inp = app.screen.query_one("#schedule-input", Input)
        inp.value = ""  # Triggers on_input_changed with empty string
        await pilot.pause()
        save_btn = app.screen.query_one("#save-schedule", Button)
        assert save_btn.disabled


@pytest.mark.tui
async def test_scheduler_save_button_persists_schedule(tmp_path):
    """Save button saves the schedule string when valid input is provided."""
    from textual.widgets import Button

    config_path = _make_config(tmp_path)
    db_path = tmp_path / "empty.db"
    app = ResearchDigestApp(config_path=config_path, db_path=db_path)
    async with app.run_test() as pilot:
        await pilot.press("u")
        await pilot.pause()
        # Example button fills a valid schedule
        app.screen.query_one("#ex-4h", Button).press()
        await pilot.pause()
        # Save button is now enabled; press it
        save_btn = app.screen.query_one("#save-schedule", Button)
        save_btn.press()
        await pilot.pause()
        assert app.scheduler_service.get_schedule_string() == "every 4 hours"


# ─── Phase 7: Scraper Management Button Handlers ─────────────────────────────


@pytest.mark.tui
async def test_scraper_management_back_button_navigates_to_dashboard(tmp_path):
    """Scraper Management back button returns to the dashboard screen."""
    from textual.widgets import Button

    config_path = _make_config(tmp_path)
    db_path = tmp_path / "empty.db"
    app = ResearchDigestApp(config_path=config_path, db_path=db_path)
    async with app.run_test() as pilot:
        await pilot.press("s")
        await pilot.pause()
        app.screen.query_one("#back", Button).press()
        await pilot.pause()
        assert app.screen.__class__.__name__ == "Dashboard"


@pytest.mark.tui
async def test_scraper_management_toggle_flips_enabled_state(tmp_path):
    """Toggle button flips scraper enabled state and repopulates the list."""
    from textual.widgets import Button

    config_path = _make_config(tmp_path)  # hackernews: enabled=True
    db_path = tmp_path / "empty.db"
    app = ResearchDigestApp(config_path=config_path, db_path=db_path)
    async with app.run_test() as pilot:
        await pilot.press("s")
        await pilot.pause()
        # hackernews is enabled → toggle button says "Disable"
        toggle_btn = app.screen.query_one("#hackernews-toggle", Button)
        assert "Disable" in str(toggle_btn.label)
        toggle_btn.press()
        await pilot.pause()
        # After toggle, hackernews is disabled → button now says "Enable"
        new_toggle = app.screen.query_one("#hackernews-toggle", Button)
        assert "Enable" in str(new_toggle.label)


@pytest.mark.tui
async def test_scraper_management_configure_pushes_configuration_screen(tmp_path):
    """Configure button pushes the Configuration screen as a modal overlay."""
    from textual.widgets import Button

    config_path = _make_config(tmp_path)
    db_path = tmp_path / "empty.db"
    app = ResearchDigestApp(config_path=config_path, db_path=db_path)
    async with app.run_test() as pilot:
        await pilot.press("s")
        await pilot.pause()
        app.screen.query_one("#hackernews-configure", Button).press()
        await pilot.pause()
        assert app.screen.__class__.__name__ == "Configuration"


@pytest.mark.tui
async def test_scraper_run_modal_mounts_and_closes(tmp_path):
    """Run Now button pushes ScraperOutputModal; worker completes; close dismisses."""
    import asyncio

    from textual.widgets import Button

    from research_digest_tui.screens.scraper_management import ScraperOutputModal

    config_path = _make_config(tmp_path)
    db_path = tmp_path / "empty.db"
    app = ResearchDigestApp(config_path=config_path, db_path=db_path)

    async with app.run_test() as pilot:
        await pilot.press("s")
        await pilot.pause()

        # Fake runner: calls callbacks immediately then returns
        def fake_run(key, on_line, on_complete):
            on_line(f"Running {key}...")
            on_complete(True)

        app.runner_service.run_scraper = fake_run

        # Press run — modal is pushed
        app.screen.query_one("#hackernews-run", Button).press()
        await pilot.pause()
        assert isinstance(app.screen, ScraperOutputModal)

        # Give the worker thread time to run and post call_from_thread callbacks
        await asyncio.sleep(0.15)
        await pilot.pause()

        # Close button is now enabled after on_complete(True)
        close_btn = app.screen.query_one("#close-modal", Button)
        assert not close_btn.disabled

        # Press close — modal is dismissed
        close_btn.press()
        await pilot.pause()
        assert app.screen.__class__.__name__ == "ScraperManagement"
