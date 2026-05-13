#!/usr/bin/env python3
"""Dashboard screen for Research Digest TUI."""

from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.screen import Screen
from textual.widgets import Footer, Header, Static, Button

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
        yield Horizontal(
            Static("Active Scrapers", classes="section-header"),
            Button("Run All Now", id="run-all-dashboard", variant="primary"),
            classes="dashboard-action-bar"
        )
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
                scraper_name=s["name"],
                config_key=s["config_key"],
                status="disabled" if not s["enabled"] else "idle",
                progress=0.0,
                item_count=item_counts.get(s["db_source"], 0),
            )
            for s in scraper_configs
        ]
        if cards:
            await grid.mount(*cards)

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Route button presses to configure, run, toggle actions."""
        btn_id = event.button.id or ""

        if btn_id == "run-all-dashboard":
            self.app.notify("Starting full research digest pipeline...")
            # Run the full pipeline sequentially (target_scraper=None)
            self.run_worker(
                lambda: self.app.runner_service.run_scraper(
                    None, # None means run all sequentially
                    lambda l: None,
                    lambda s: self.app.call_from_thread(self.app.notify, f"Full digest finished: {s}")
                ),
                thread=True
            )
            return

        if btn_id.endswith("-run"):
            key = btn_id[:-4]
            scraper_info = next(
                (
                    s
                    for s in self.app.config_service.get_scraper_configs()
                    if s["config_key"] == key
                ),
                None,
            )
            if scraper_info:
                from .scraper_management import ScraperOutputModal
                self.app.push_screen(ScraperOutputModal(key, scraper_info["name"]))
            return

        if btn_id.endswith("-configure"):
            key = btn_id[:-10]
            from .configuration import Configuration
            self.app.push_screen(Configuration(initial_scraper=key))
            return

        if btn_id.endswith("-toggle"):
            key = btn_id[:-7]
            scraper_cfg = self.app.config_service.get_scraper_config(key)
            if scraper_cfg is None:
                return
            current_enabled = getattr(scraper_cfg, "enabled", False)
            self.app.config_service.set_scraper_enabled(key, not current_enabled)
            # Re-mount dashboard scrapers to update UI fully or update card
            card = event.button.parent.parent # ScraperCard
            card.watch_status("disabled" if current_enabled else "idle")
