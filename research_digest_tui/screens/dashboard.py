#!/usr/bin/env python3
"""Dashboard screen for Research Digest TUI."""

from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.screen import Screen
from textual.widgets import Footer, Header, Static

from ..widgets import ScraperCard


class Dashboard(Screen):
    """Main dashboard screen showing scraper status overview."""

    def compose(self) -> ComposeResult:
        """Compose the dashboard layout.

        Returns:
            Textual widgets for the dashboard.
        """
        yield Header()

        yield Static(
            "Status: Idle  |  Last Run: Never  |  Items Collected: 0",
            classes="status-bar",
        )

        yield Static("Active Scrapers", classes="section-header")

        with Container(classes="scrapers-grid"):
            with Horizontal():
                yield ScraperCard(
                    "HackerNews", status="idle", progress=0.0, item_count=0
                )
                yield ScraperCard("RSS", status="idle", progress=0.0, item_count=0)

            with Horizontal():
                yield ScraperCard("Reddit", status="idle", progress=0.0, item_count=0)
                yield ScraperCard("ArXiv", status="idle", progress=0.0, item_count=0)

        yield Static("Recent Activity", classes="section-header")
        with Container(classes="activity-log"):
            yield Static("No recent activity", classes="muted")

        yield Footer()
