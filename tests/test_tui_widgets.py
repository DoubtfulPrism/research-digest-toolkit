#!/usr/bin/env python3
"""Unit tests for TUI widgets."""

import pytest

pytest.importorskip("textual")

from textual.app import App, ComposeResult  # noqa: E402
from textual.widgets import ProgressBar, Static  # noqa: E402

from rdt.tui.widgets import ScraperCard  # noqa: E402


class _CardApp(App):
    """Minimal test app that mounts a single ScraperCard."""

    def __init__(self, status: str = "idle", progress: float = 0.0) -> None:
        super().__init__()
        self._initial_status = status
        self._initial_progress = progress

    def compose(self) -> ComposeResult:
        yield ScraperCard(
            "TestScraper", "testscraper", status=self._initial_status, progress=self._initial_progress
        )


@pytest.mark.unit
def test_scraper_card_creation():
    """Test ScraperCard widget can be instantiated."""
    card = ScraperCard("HackerNews", "hackernews", status="idle", progress=0.0, item_count=0)
    assert card.scraper_name == "HackerNews"
    assert card.status == "idle"
    assert card.progress == 0.0
    assert card.item_count == 0


@pytest.mark.unit
def test_scraper_card_reactive_properties():
    """Test ScraperCard reactive properties update correctly."""
    card = ScraperCard("RSS", "rss", status="idle", progress=0.5, item_count=10)

    assert card.status == "idle"
    assert card.progress == 0.5
    assert card.item_count == 10

    card.status = "running"
    assert card.status == "running"

    card.progress = 0.75
    assert card.progress == 0.75

    card.item_count = 25
    assert card.item_count == 25


@pytest.mark.unit
def test_scraper_card_with_different_statuses():
    """Test ScraperCard handles different status values."""
    statuses = ["idle", "running", "disabled"]

    for status in statuses:
        card = ScraperCard("ArXiv", "arxiv", status=status, progress=0.0, item_count=0)
        assert card.status == status


# ─── watch_status and watch_progress (TDD) ───────────────────────────────────


@pytest.mark.tui
async def test_watch_status_updates_header_to_running():
    """watch_status updates the card header text when status becomes 'running'."""
    app = _CardApp(status="idle")
    async with app.run_test() as pilot:
        card = app.query_one(ScraperCard)
        card.status = "running"
        await pilot.pause()
        header = card.query_one(".card-header", Static)
        assert "Running" in str(header.content)


@pytest.mark.tui
async def test_watch_status_updates_header_to_idle():
    """watch_status updates the card header text when status becomes 'idle'."""
    app = _CardApp(status="running")
    async with app.run_test() as pilot:
        card = app.query_one(ScraperCard)
        card.status = "idle"
        await pilot.pause()
        header = card.query_one(".card-header", Static)
        assert "Idle" in str(header.content)


@pytest.mark.tui
async def test_watch_status_disabled_sets_toggle_to_enable():
    """watch_status sets toggle button label to 'Enable' when status is 'disabled'."""
    from textual.widgets import Button

    app = _CardApp(status="idle")
    async with app.run_test() as pilot:
        card = app.query_one(ScraperCard)
        card.status = "disabled"
        await pilot.pause()
        toggle = card.query_one("#testscraper-toggle", Button)
        assert str(toggle.label) == "Enable"


@pytest.mark.tui
async def test_watch_status_running_sets_toggle_to_disable():
    """watch_status sets toggle button label to 'Disable' when status is not 'disabled'."""
    from textual.widgets import Button

    app = _CardApp(status="disabled")
    async with app.run_test() as pilot:
        card = app.query_one(ScraperCard)
        card.status = "running"
        await pilot.pause()
        toggle = card.query_one("#testscraper-toggle", Button)
        assert str(toggle.label) == "Disable"


@pytest.mark.tui
async def test_watch_progress_updates_progress_bar():
    """watch_progress updates the ProgressBar progress value."""
    app = _CardApp(progress=0.0)
    async with app.run_test() as pilot:
        card = app.query_one(ScraperCard)
        card.progress = 0.75
        await pilot.pause()
        bar = card.query_one(ProgressBar)
        assert bar.progress == 75.0  # 0.75 * 100
