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
    ConverterScreen,
)
from .services import ConfigService, DataService
from .services.runner_service import RunnerService
from .services.scheduler_service import SchedulerService
from .services.update_service import UpdateService

_DEFAULT_CONFIG_PATH = Path("research_config.yaml")
_DEFAULT_DB_PATH = Path("research_digest_state.db")


class ResearchDigestApp(App):
    """Main Textual application for Research Digest."""

    TITLE = "Research Digest Toolkit"
    SUB_TITLE = "Automated Research Aggregation"

    def __init__(
        self,
        config_path: Path | None = None,
        db_path: Path | None = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.config_service = ConfigService(config_path or _DEFAULT_CONFIG_PATH)
        self.data_service = DataService(db_path or _DEFAULT_DB_PATH)
        self.runner_service = RunnerService(config_path or _DEFAULT_CONFIG_PATH)
        self.scheduler_service = SchedulerService(self.config_service)
        self.update_service = UpdateService()

    CSS_PATH = [
        Path(__file__).parent / "app.tcss",
        Path(__file__).parent / "screens" / "dashboard.tcss",
        Path(__file__).parent / "screens" / "scraper_management.tcss",
        Path(__file__).parent / "screens" / "configuration.tcss",
        Path(__file__).parent / "screens" / "logs.tcss",
        Path(__file__).parent / "screens" / "history.tcss",
        Path(__file__).parent / "screens" / "scheduler.tcss",
        Path(__file__).parent / "screens" / "converter.tcss",
        Path(__file__).parent / "screens" / "update_prompt.tcss",
    ]

    BINDINGS = [
        Binding("q", "quit", "Quit", priority=True),
        Binding("d", "show_dashboard", "Dashboard"),
        Binding("s", "show_scrapers", "Scrapers"),
        Binding("c", "show_config", "Config"),
        Binding("l", "show_logs", "Logs"),
        Binding("h", "show_history", "History"),
        Binding("u", "show_scheduler", "Scheduler"),
        Binding("v", "show_converter", "Convert"),
    ]

    SCREENS = {
        "dashboard": Dashboard,
        "scraper_management": ScraperManagement,
        "configuration": Configuration,
        "logs": Logs,
        "history": History,
        "scheduler": Scheduler,
        "converter": ConverterScreen,
    }

    def on_mount(self) -> None:
        """Mount the app and push the dashboard screen."""
        self.push_screen("dashboard")
        # Non-blocking update check in background
        self.run_worker(self._check_for_update, thread=True)

    def _check_for_update(self) -> None:
        """Background worker: check GitHub for a newer version."""
        if not self.update_service.should_check():
            return
        result = self.update_service.check_for_update()
        self.update_service.record_check()
        if result.available and result.remote_version:
            from .screens.update_prompt import UpdatePrompt

            self.call_from_thread(
                self.push_screen,
                UpdatePrompt(
                    local_version=result.local_version,
                    remote_version=result.remote_version,
                ),
            )

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

    def action_show_converter(self) -> None:
        """Navigate to Converter screen."""
        self.switch_screen("converter")


if __name__ == "__main__":
    app = ResearchDigestApp()
    app.run()
