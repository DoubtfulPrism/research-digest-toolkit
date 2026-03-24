#!/usr/bin/env python3
"""Dashboard screen for Research Digest TUI."""

from textual.app import ComposeResult
from textual.containers import Container
from textual.screen import Screen
from textual.widgets import Footer, Header, Static

from ..widgets import ScraperCard


class Dashboard(Screen):
    """Main dashboard screen showing scraper status overview."""

    def compose(self) -> ComposeResult:
        """Compose the dashboard layout with placeholder containers.

        Returns:
            Textual widgets for the dashboard.
        """
        yield Header()
        yield Static("", classes="status-bar")
        yield Static("Active Scrapers", classes="section-header")
        with Container(classes="scrapers-grid", id="scrapers-grid"):
            pass
        yield Static("Recent Activity", classes="section-header")
        with Container(classes="activity-log"):
            yield Static("No recent activity", classes="muted")
        yield Footer()

    async def on_mount(self) -> None:
        """Populate dashboard with real data from services."""
        scraper_configs = self.app.config_service.get_scraper_configs()
        item_counts = self.app.data_service.get_item_counts_by_source()
        summary_stats = self.app.data_service.get_summary_stats()

        # Update status bar with real totals
        status_bar = self.query_one(".status-bar", Static)
        total = summary_stats["total_items"]
        if total == 0:
            status_text = (
                "Status: Idle  |  Items Collected: 0  |  No data collected yet"
            )
        else:
            date_range = summary_stats["date_range"]
            source_count = summary_stats["source_count"]
            status_text = f"Items Collected: {total} | Sources: {source_count} | Data: {date_range}"
        status_bar.update(status_text)

        # Mount ScraperCards for enabled scrapers only
        grid = self.query_one("#scrapers-grid", Container)
        cards = [
            ScraperCard(
                s["name"],
                status="disabled" if not s["enabled"] else "idle",
                progress=0.0,
                item_count=item_counts.get(s["db_source"], 0),
            )
            for s in scraper_configs
        ]
        if cards:
            await grid.mount(*cards)
