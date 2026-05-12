#!/usr/bin/env python3
"""Update prompt modal screen for RDT TUI.

Shown when a newer version is detected on GitHub. Offers the user a choice
to update now or skip.
"""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Static


class UpdatePrompt(ModalScreen[bool]):
    """Modal asking the user whether to upgrade to a new version."""

    BINDINGS = [("escape", "skip", "Skip")]

    def __init__(
        self,
        *,
        local_version: str,
        remote_version: str,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.local_version = local_version
        self.remote_version = remote_version

    def compose(self) -> ComposeResult:
        with Vertical(id="update-dialog"):
            yield Static(
                f"Update Available:  v{self.local_version}  →  v{self.remote_version}",
                id="update-title",
            )
            yield Static(
                "A new version of Research Digest Toolkit is available.",
                id="update-description",
            )
            with Horizontal(id="update-buttons"):
                yield Button("Update Now", id="update-now", variant="primary")
                yield Button("Skip", id="update-skip", variant="default")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button clicks."""
        if event.button.id == "update-now":
            self._run_update()
        elif event.button.id == "update-skip":
            self.action_skip()

    def action_skip(self) -> None:
        """Dismiss the modal without updating."""
        self.dismiss(False)

    def _run_update(self) -> None:
        """Execute the update in a worker thread and show the result."""
        status = self.query_one("#update-description", Static)
        status.update("Updating… please wait.")
        self.query_one("#update-now", Button).disabled = True
        self.query_one("#update-skip", Button).disabled = True

        self.run_worker(self._do_update, thread=True)

    async def _do_update(self) -> None:
        """Worker that calls UpdateService.perform_update."""
        from rdt.tui.services.update_service import UpdateService

        service = UpdateService()
        outcome = service.perform_update()

        status = self.query_one("#update-description", Static)
        if outcome.success:
            self.call_from_thread(
                status.update,
                f"✅ Updated via {outcome.method}! Restart RDT to use the new version.",
            )
        else:
            self.call_from_thread(
                status.update,
                f"❌ Update failed: {outcome.error}",
            )
        # Re-enable skip so the user can close the modal
        self.call_from_thread(
            setattr, self.query_one("#update-skip", Button), "disabled", False
        )
