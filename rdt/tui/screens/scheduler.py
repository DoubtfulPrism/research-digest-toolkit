#!/usr/bin/env python3
"""Scheduler screen for Research Digest TUI."""

from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Input, Static


class Scheduler(Screen):
    """Scheduler screen — configure and enable scheduled runs."""

    def __init__(self) -> None:
        super().__init__(id="scheduler-screen")

    def compose(self) -> ComposeResult:
        """Build the scheduler screen layout."""
        yield Header()
        yield Static("Scheduler", classes="screen-title")

        with Container(id="scheduler-container"):
            yield Static("Schedule Manager", classes="section-heading")

            with Horizontal(id="status-row"):
                yield Static("Status: ", classes="field-label")
                yield Static("DISABLED", id="schedule-status")
                yield Button("Toggle", id="toggle-schedule")

            yield Static("Schedule String:", classes="field-label")
            yield Input(
                id="schedule-input",
                placeholder="every day at 06:00",
            )
            yield Static("", id="validation-msg", classes="validation-ok")

            yield Static(
                "Examples:",
                classes="field-label",
            )
            with Horizontal(id="example-buttons"):
                yield Button("every 4 hours", id="ex-4h")
                yield Button("every day at 06:00", id="ex-daily")
                yield Button("every monday at 09:00", id="ex-weekly")

            with Horizontal(id="scheduler-actions"):
                yield Button("Save", id="save-schedule", disabled=True)
                yield Button("Back", id="back")

        yield Footer()

    def on_mount(self) -> None:
        """Load current schedule state on mount."""
        self._reload_state()

    def _reload_state(self) -> None:
        svc = self.app.scheduler_service
        enabled = svc.get_schedule_enabled()
        schedule_str = svc.get_schedule_string() or ""

        status = self.query_one("#schedule-status", Static)
        status.update("ENABLED" if enabled else "DISABLED")
        status.set_class(enabled, "status-enabled")
        status.set_class(not enabled, "status-disabled")

        inp = self.query_one("#schedule-input", Input)
        inp.value = schedule_str

        # Validate current value
        if schedule_str:
            valid, msg = svc.validate(schedule_str)
            self._show_validation(valid, msg if not valid else "✓ Valid")
            self.query_one("#save-schedule", Button).disabled = not valid
        else:
            self.query_one("#validation-msg", Static).update("")
            self.query_one("#save-schedule", Button).disabled = True

    def _show_validation(self, valid: bool, msg: str) -> None:
        label = self.query_one("#validation-msg", Static)
        label.update(msg)
        label.set_class(valid, "validation-ok")
        label.set_class(not valid, "validation-error")

    def on_input_changed(self, event: Input.Changed) -> None:
        """Validate schedule input as user types."""
        if event.input.id == "schedule-input":
            val = event.value.strip()
            if not val:
                self._show_validation(True, "")
                self.query_one("#save-schedule", Button).disabled = True
                return
            valid, msg = self.app.scheduler_service.validate(val)
            self._show_validation(valid, "✓ Valid" if valid else msg)
            self.query_one("#save-schedule", Button).disabled = not valid

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses for save, back, toggle, and examples."""
        btn_id = event.button.id or ""

        if btn_id == "back":
            self.app.switch_screen("dashboard")

        elif btn_id == "save-schedule":
            val = self.query_one("#schedule-input", Input).value.strip()
            try:
                self.app.scheduler_service.set_schedule(val)
                self.app.notify("Schedule saved")
                self._reload_state()
            except Exception as e:
                self._show_validation(False, str(e))

        elif btn_id == "toggle-schedule":
            current = self.app.scheduler_service.get_schedule_enabled()
            self.app.scheduler_service.set_enabled(not current)
            self._reload_state()

        elif btn_id.startswith("ex-"):
            examples = {
                "ex-4h": "every 4 hours",
                "ex-daily": "every day at 06:00",
                "ex-weekly": "every monday at 09:00",
            }
            self.query_one("#schedule-input", Input).value = examples.get(btn_id, "")
