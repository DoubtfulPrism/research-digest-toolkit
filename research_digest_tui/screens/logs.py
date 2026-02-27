#!/usr/bin/env python3
"""Logs screen (placeholder) for Research Digest TUI."""

from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Static


class Logs(Screen):
    """Logs screen placeholder (Phase 3 implementation)."""

    def __init__(self) -> None:
        super().__init__(id="logs-screen")

    def compose(self) -> ComposeResult:
        """Compose the logs placeholder layout."""
        yield Header()

        yield Static("Logs", classes="screen-title")

        with Container(classes="placeholder-container"):
            yield Static(
                "📋  Log Viewer",
                classes="placeholder-heading",
            )
            yield Static(
                "Log viewing will be available in Phase 3.",
                classes="placeholder-message",
            )
            yield Static("")

            yield Static("Filter by level:", classes="section-label")
            with Horizontal(classes="log-filter-row"):
                yield Button("INFO", disabled=True)
                yield Button("WARN", disabled=True)
                yield Button("ERROR", disabled=True)

            yield Static("")
            yield Static(
                "[ No logs yet — run a scraper to see output here ]",
                classes="log-area-placeholder",
            )

        yield Footer()
