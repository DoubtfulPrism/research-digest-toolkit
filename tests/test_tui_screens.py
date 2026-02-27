#!/usr/bin/env python3
"""Unit tests for TUI screens."""

import pytest

pytest.importorskip("textual")

from research_digest_tui import ResearchDigestApp  # noqa: E402
from research_digest_tui.screens import (  # noqa: E402
    Configuration,
    Dashboard,
    History,
    Logs,
    Scheduler,
    ScraperManagement,
)


@pytest.mark.unit
@pytest.mark.parametrize(
    "screen_class",
    [Dashboard, ScraperManagement, Configuration, Logs, History, Scheduler],
)
def test_screen_can_instantiate(screen_class):
    """Test each screen can be instantiated and has a compose method."""
    screen = screen_class()
    assert screen is not None
    assert callable(screen.compose)


@pytest.mark.unit
def test_app_creation():
    """Test ResearchDigestApp can be instantiated."""
    app = ResearchDigestApp()
    assert app.TITLE == "Research Digest Toolkit"
    assert app.SUB_TITLE == "Automated Research Aggregation"


@pytest.mark.unit
def test_app_has_all_six_screens_registered():
    """Test ResearchDigestApp has all 6 screens registered."""
    app = ResearchDigestApp()
    assert "dashboard" in app.SCREENS
    assert "scraper_management" in app.SCREENS
    assert "configuration" in app.SCREENS
    assert "logs" in app.SCREENS
    assert "history" in app.SCREENS
    assert "scheduler" in app.SCREENS


@pytest.mark.unit
def test_app_has_keyboard_bindings():
    """Test ResearchDigestApp has all 6 screen keyboard bindings plus quit."""
    app = ResearchDigestApp()
    binding_keys = [b.key for b in app.BINDINGS]

    assert "q" in binding_keys
    assert "d" in binding_keys
    assert "s" in binding_keys
    assert "c" in binding_keys
    assert "l" in binding_keys
    assert "h" in binding_keys
    assert "u" in binding_keys
