#!/usr/bin/env python3
"""History/Analytics screen for Research Digest TUI."""

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Static


class History(Screen):
    """History/Analytics screen — summary stats and source distribution."""

    def __init__(self) -> None:
        super().__init__(id="history-screen")
        self._current_days: int | None = None  # None = All Time

    def compose(self) -> ComposeResult:
        """Compose the history/analytics layout."""
        yield Header()
        yield Static("History & Analytics", classes="screen-title")
        with Horizontal(classes="time-range-row"):
            yield Button("7 Days", id="filter-7d")
            yield Button("30 Days", id="filter-30d")
            yield Button("All Time", id="filter-all")
        yield Static("", id="stats-summary", classes="stats-summary")
        yield Static("Source Distribution", classes="section-header")
        yield Static("", id="source-distribution", classes="distribution-table")
        yield Static("Daily Counts", classes="section-header")
        yield Static("", id="daily-counts", classes="daily-table")
        yield Footer()

    def on_mount(self) -> None:
        """Load analytics data from services."""
        self._reload()

    def _reload(self) -> None:
        """Re-query services and refresh all analytics widgets."""
        stats = self.app.data_service.get_summary_stats(days=self._current_days)
        distribution = self.app.data_service.get_source_distribution(
            days=self._current_days
        )
        daily = self.app.data_service.get_daily_counts(days=self._current_days or 30)

        # Summary stats
        summary = self.query_one("#stats-summary", Static)
        total = stats["total_items"]
        if total == 0:
            summary.update("No data collected yet — run a scraper to populate")
        else:
            most_active = distribution[0]["source"] if distribution else "—"
            summary.update(
                f"Total Items: {total} | Avg/Day: {stats['avg_per_day']} | "
                f"Most Active: {most_active} | Range: {stats['date_range']}"
            )

        # Source distribution table
        dist = self.query_one("#source-distribution", Static)
        if distribution:
            lines = [
                f"{r['source']:<12} {r['count']:>6}  ({r['percentage']:.1f}%)"
                for r in distribution
            ]
            dist.update("\n".join(lines))
        else:
            dist.update("No data")

        # Daily counts
        daily_widget = self.query_one("#daily-counts", Static)
        if daily:
            lines = [f"{r['date']}  {r['count']}" for r in daily]
            daily_widget.update("\n".join(lines))
        else:
            daily_widget.update("No data")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle time range filter button presses."""
        btn_id = event.button.id
        if btn_id == "filter-7d":
            self._current_days = 7
        elif btn_id == "filter-30d":
            self._current_days = 30
        elif btn_id == "filter-all":
            self._current_days = None
        else:
            return
        self._reload()
