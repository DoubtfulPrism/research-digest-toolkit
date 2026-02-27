#!/usr/bin/env python3
"""Integration tests for TUI screen navigation."""

import pytest

pytest.importorskip("textual")
pytest.importorskip("pytest_asyncio")

from research_digest_tui import ResearchDigestApp  # noqa: E402
from research_digest_tui.widgets import ScraperCard  # noqa: E402


@pytest.mark.tui
async def test_dashboard_composes_four_scraper_cards():
    """Dashboard composes exactly 4 ScraperCard widgets (one per scraper)."""
    app = ResearchDigestApp()
    async with app.run_test() as _:
        cards = app.query(ScraperCard)
        assert len(cards) == 4


@pytest.mark.tui
async def test_scraper_card_compose_yields_required_widgets():
    """ScraperCard composes header, progress bar, and action buttons."""
    app = ResearchDigestApp()
    async with app.run_test() as _:
        progress_bars = app.query("ScraperCard ProgressBar")
        buttons = app.query("ScraperCard Button")
        assert len(progress_bars) == 4  # one per card
        assert len(buttons) == 12  # 3 buttons × 4 cards


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
        await pilot.press(key)
        assert app.screen.__class__.__name__ == screen_name
