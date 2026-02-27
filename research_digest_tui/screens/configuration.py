#!/usr/bin/env python3
"""Configuration screen (placeholder) for Research Digest TUI."""

from pathlib import Path

from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Static


class Configuration(Screen):
    """Configuration screen placeholder (Phase 4 implementation)."""

    def compose(self) -> ComposeResult:
        """Compose the configuration placeholder layout.

        Returns:
            Textual widgets for the configuration screen.
        """
        yield Header()

        yield Static("Configuration", classes="screen-title")

        with Container(classes="placeholder-container"):
            yield Static(
                "⚙️  Configuration Editor",
                classes="placeholder-heading",
            )
            yield Static(
                "Configuration editing will be available in Phase 4.",
                classes="placeholder-message",
            )
            yield Static("")
            yield Static(
                f"Current config file: {Path.cwd() / 'research_config.yaml'}",
                classes="config-path",
            )
            yield Static("")

            yield Static("Scrapers:", classes="section-label")
            with Horizontal(classes="scraper-tabs"):
                yield Button("HackerNews", disabled=True)
                yield Button("RSS", disabled=True)
                yield Button("Reddit", disabled=True)
                yield Button("ArXiv", disabled=True)

        with Horizontal(classes="bottom-actions"):
            yield Button("Back", id="back")

        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses.

        Args:
            event: The button press event
        """
        if event.button.id == "back":
            self.app.switch_screen("dashboard")
