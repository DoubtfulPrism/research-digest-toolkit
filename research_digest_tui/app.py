#!/usr/bin/env python3
"""Main TUI application for Research Digest Toolkit."""

from pathlib import Path

from textual.app import App
from textual.binding import Binding

from .screens import (
    Configuration,
    Dashboard,
    History,
    Logs,
    Scheduler,
    ScraperManagement,
)


class ResearchDigestApp(App):
    """Main Textual application for Research Digest."""

    TITLE = "Research Digest Toolkit"
    SUB_TITLE = "Automated Research Aggregation"

    CSS_PATH = [
        Path(__file__).parent / "app.tcss",
        Path(__file__).parent / "screens" / "dashboard.tcss",
        Path(__file__).parent / "screens" / "scraper_management.tcss",
        Path(__file__).parent / "screens" / "configuration.tcss",
        Path(__file__).parent / "screens" / "logs.tcss",
        Path(__file__).parent / "screens" / "history.tcss",
        Path(__file__).parent / "screens" / "scheduler.tcss",
    ]

    BINDINGS = [
        Binding("q", "quit", "Quit", priority=True),
        Binding("d", "show_dashboard", "Dashboard"),
        Binding("s", "show_scrapers", "Scrapers"),
        Binding("c", "show_config", "Config"),
        Binding("l", "show_logs", "Logs"),
        Binding("h", "show_history", "History"),
        Binding("u", "show_scheduler", "Scheduler"),
    ]

    SCREENS = {
        "dashboard": Dashboard,
        "scraper_management": ScraperManagement,
        "configuration": Configuration,
        "logs": Logs,
        "history": History,
        "scheduler": Scheduler,
    }

    def on_mount(self) -> None:
        """Mount the app and push the dashboard screen."""
        self.push_screen("dashboard")

    def action_show_dashboard(self) -> None:
        """Navigate to Dashboard screen."""
        self.switch_screen("dashboard")

    def action_show_scrapers(self) -> None:
        """Navigate to Scraper Management screen."""
        self.switch_screen("scraper_management")

    def action_show_config(self) -> None:
        """Navigate to Configuration screen."""
        self.switch_screen("configuration")

    def action_show_logs(self) -> None:
        """Navigate to Logs screen."""
        self.switch_screen("logs")

    def action_show_history(self) -> None:
        """Navigate to History/Analytics screen."""
        self.switch_screen("history")

    def action_show_scheduler(self) -> None:
        """Navigate to Scheduler screen."""
        self.switch_screen("scheduler")


if __name__ == "__main__":
    app = ResearchDigestApp()
    app.run()
