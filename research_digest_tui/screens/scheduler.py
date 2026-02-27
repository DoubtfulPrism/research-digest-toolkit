#!/usr/bin/env python3
"""Scheduler screen (placeholder) for Research Digest TUI."""

from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Static


class Scheduler(Screen):
    """Scheduler screen placeholder (Phase 5 implementation)."""

    def __init__(self) -> None:
        super().__init__(id="scheduler-screen")

    def compose(self) -> ComposeResult:
        """Compose the scheduler placeholder layout."""
        yield Header()

        yield Static("Scheduler", classes="screen-title")

        with Container(classes="placeholder-container"):
            yield Static(
                "🕐  Schedule Manager",
                classes="placeholder-heading",
            )
            yield Static(
                "Schedule management will be available in Phase 5.",
                classes="placeholder-message",
            )
            yield Static("")

            yield Static("Schedules:", classes="section-label")
            with Container(classes="schedule-list"):
                yield Static(
                    "• Daily Digest: every day at 06:00",
                    classes="schedule-item",
                )
                yield Static(
                    "• Weekly Summary: every Monday at 08:00",
                    classes="schedule-item",
                )

            yield Static("")
            with Horizontal(classes="schedule-actions"):
                yield Button("Add Schedule", disabled=True)

        yield Footer()
