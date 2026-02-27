#!/usr/bin/env python3
"""Unit tests for TUI widgets."""

import pytest

pytest.importorskip("textual")

from research_digest_tui.widgets import ScraperCard  # noqa: E402


@pytest.mark.unit
def test_scraper_card_creation():
    """Test ScraperCard widget can be instantiated."""
    card = ScraperCard("HackerNews", status="idle", progress=0.0, item_count=0)
    assert card.scraper_name == "HackerNews"
    assert card.status == "idle"
    assert card.progress == 0.0
    assert card.item_count == 0


@pytest.mark.unit
def test_scraper_card_reactive_properties():
    """Test ScraperCard reactive properties update correctly."""
    card = ScraperCard("RSS", status="idle", progress=0.5, item_count=10)

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
        card = ScraperCard("ArXiv", status=status, progress=0.0, item_count=0)
        assert card.status == status
