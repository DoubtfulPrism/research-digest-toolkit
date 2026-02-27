#!/usr/bin/env python3
"""Scraper Management screen for Research Digest TUI."""

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, VerticalScroll
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Static


class ScraperManagement(Screen):
    """Scraper Management screen showing all scrapers with detailed controls."""

    def compose(self) -> ComposeResult:
        """Compose the scraper management layout.

        Returns:
            Textual widgets for the scraper management screen.
        """
        yield Header()

        yield Static("Scraper Management", classes="screen-title")

        with VerticalScroll():
            with Container(classes="scraper-row"):
                yield Static("HackerNews", classes="scraper-name")
                yield Static(
                    "Topics: AI, Platform Engineering | Min Points: 50",
                    classes="scraper-config",
                )
                yield Static("Last Run: Never", classes="scraper-last-run")
                with Horizontal(classes="scraper-actions"):
                    yield Button("Configure", id="hn-configure", disabled=True)
                    yield Button("Run Now", id="hn-run", disabled=True)
                    yield Button("View Logs", id="hn-logs", disabled=True)
                    yield Button("Disable", id="hn-disable", disabled=True)

            with Container(classes="scraper-row"):
                yield Static("RSS", classes="scraper-name")
                yield Static(
                    "Feeds: 8 sources | Days Back: 7", classes="scraper-config"
                )
                yield Static("Last Run: Never", classes="scraper-last-run")
                with Horizontal(classes="scraper-actions"):
                    yield Button("Configure", id="rss-configure", disabled=True)
                    yield Button("Run Now", id="rss-run", disabled=True)
                    yield Button("View Logs", id="rss-logs", disabled=True)
                    yield Button("Disable", id="rss-disable", disabled=True)

            with Container(classes="scraper-row"):
                yield Static("Reddit", classes="scraper-name")
                yield Static(
                    "Subreddits: ExperiencedDevs, programming | Min Upvotes: 100",
                    classes="scraper-config",
                )
                yield Static("Last Run: Never", classes="scraper-last-run")
                with Horizontal(classes="scraper-actions"):
                    yield Button("Configure", id="reddit-configure", disabled=True)
                    yield Button("Run Now", id="reddit-run", disabled=True)
                    yield Button("View Logs", id="reddit-logs", disabled=True)
                    yield Button("Disable", id="reddit-disable", disabled=True)

            with Container(classes="scraper-row"):
                yield Static("ArXiv", classes="scraper-name")
                yield Static(
                    "Categories: cs.AI, cs.LG | Max Results: 50",
                    classes="scraper-config",
                )
                yield Static("Last Run: Never", classes="scraper-last-run")
                with Horizontal(classes="scraper-actions"):
                    yield Button("Configure", id="arxiv-configure", disabled=True)
                    yield Button("Run Now", id="arxiv-run", disabled=True)
                    yield Button("View Logs", id="arxiv-logs", disabled=True)
                    yield Button("Disable", id="arxiv-disable", disabled=True)

        with Horizontal(classes="bottom-actions"):
            yield Button("Add New Scraper", id="add-scraper", disabled=True)
            yield Button("Run All", id="run-all", disabled=True)
            yield Button("Back", id="back")

        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses.

        Args:
            event: The button press event
        """
        if event.button.id == "back":
            self.app.switch_screen("dashboard")
