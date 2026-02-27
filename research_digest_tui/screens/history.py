#!/usr/bin/env python3
"""History/Analytics screen (placeholder) for Research Digest TUI."""

from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Static


class History(Screen):
    """History/Analytics screen placeholder (Phase 2 implementation)."""

    def __init__(self) -> None:
        super().__init__(id="history-screen")

    def compose(self) -> ComposeResult:
        """Compose the history/analytics placeholder layout."""
        yield Header()

        yield Static("History & Analytics", classes="screen-title")

        with Container(classes="placeholder-container"):
            yield Static(
                "📊  History & Analytics",
                classes="placeholder-heading",
            )
            yield Static(
                "History & Analytics will be available in Phase 2.",
                classes="placeholder-message",
            )
            yield Static("")

            yield Static("Time range:", classes="section-label")
            with Horizontal(classes="time-range-row"):
                yield Button("7 Days", disabled=True)
                yield Button("30 Days", disabled=True)
                yield Button("All Time", disabled=True)

            yield Static("")
            yield Static(
                "[ Chart placeholder — Polars analytics coming in Phase 2 ]",
                classes="chart-area-placeholder",
            )

        yield Footer()
