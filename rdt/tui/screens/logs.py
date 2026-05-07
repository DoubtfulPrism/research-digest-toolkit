#!/usr/bin/env python3
"""Content Browser screen for Research Digest TUI."""

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.screen import Screen
from textual.widgets import Button, DataTable, Footer, Header, Static

# Validated source names — only these may be passed to DataService queries
_VALID_SOURCES = {"hn", "rss", "reddit", "arxiv"}


class Logs(Screen):
    """Content Browser — scrollable timeline of all processed items."""

    def __init__(self) -> None:
        super().__init__(id="logs-screen")
        self._current_filter: str | None = None

    def compose(self) -> ComposeResult:
        """Compose the content browser layout."""
        yield Header()
        yield Static("Content Browser", classes="screen-title")
        with Horizontal(classes="filter-row"):
            yield Button("All", id="filter-all", classes="filter-btn")
            yield Button("HN", id="filter-hn", classes="filter-btn")
            yield Button("RSS", id="filter-rss", classes="filter-btn")
            yield Button("Reddit", id="filter-reddit", classes="filter-btn")
            yield Button("ArXiv", id="filter-arxiv", classes="filter-btn")
        yield DataTable(id="content-table")
        yield Footer()

    def on_mount(self) -> None:
        """Initialize the DataTable with columns and load data."""
        table = self.query_one("#content-table", DataTable)
        table.add_columns("Source", "Title", "Date")
        self._load_items()

    def _load_items(self) -> None:
        """Reload the DataTable with items for the current filter."""
        table = self.query_one("#content-table", DataTable)
        table.clear()
        items = self.app.data_service.get_items_timeline(
            source_filter=self._current_filter, limit=200
        )
        for item in items:
            title_or_id = item.get("title") or item.get("unique_id", "")
            if len(str(title_or_id)) > 60:
                title_or_id = str(title_or_id)[:57] + "..."
            date = str(item.get("processed_at", ""))[:10]
            table.add_row(item["source"], title_or_id, date)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle source filter button presses."""
        btn_id = event.button.id
        if btn_id == "filter-all":
            self._current_filter = None
        elif btn_id and btn_id.startswith("filter-"):
            source = btn_id[len("filter-") :]
            if source in _VALID_SOURCES:
                self._current_filter = source
            else:
                return
        else:
            return
        self._load_items()
