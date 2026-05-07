#!/usr/bin/env python3
"""Scraper Card widget for displaying individual scraper status."""

from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.reactive import reactive
from textual.widgets import Button, ProgressBar, Static


class ScraperCard(Container):
    """Widget displaying a single scraper's status.

    Args:
        scraper_name: Scraper name (e.g., "HackerNews", "RSS", "Reddit", "ArXiv")
        status: Current status ("running", "idle", "disabled")
        progress: Progress percentage (0.0 to 1.0)
        item_count: Number of items collected
    """

    DEFAULT_CSS = """
    ScraperCard {
        height: auto;
        border: solid $primary;
        padding: 1;
        margin: 1;
    }

    ScraperCard .card-header {
        text-style: bold;
        margin-bottom: 1;
    }

    ScraperCard .status-running {
        color: green;
    }

    ScraperCard .status-idle {
        color: $text-muted;
    }

    ScraperCard .status-disabled {
        color: red;
    }

    ScraperCard .button-row {
        height: auto;
        margin-top: 1;
    }

    ScraperCard Button {
        margin-right: 1;
    }
    """

    # Reactive properties for live updates (used in future phases)
    status: reactive[str] = reactive("idle")
    progress: reactive[float] = reactive(0.0)
    item_count: reactive[int] = reactive(0)

    def __init__(
        self,
        scraper_name: str,
        config_key: str,
        status: str = "idle",
        progress: float = 0.0,
        item_count: int = 0,
    ):
        """Initialize the scraper card.

        Args:
            scraper_name: Scraper name
            status: Current status
            progress: Progress percentage (0.0 to 1.0)
            item_count: Number of items collected
        """
        super().__init__()
        self.scraper_name = scraper_name  # Use scraper_name instead of name
        self.config_key = config_key
        self.status = status
        self.progress = progress
        self.item_count = item_count

    def compose(self) -> ComposeResult:
        """Compose the card layout.

        Returns:
            Textual widgets for the card.
        """
        # Header with scraper name and status
        status_class = f"status-{self.status}"
        yield Static(
            f"{self.scraper_name} - [{status_class}]{self.status.title()}[/]",
            classes="card-header",
        )

        # Progress bar
        yield ProgressBar(total=100, show_eta=False)

        # Item count
        yield Static(f"Items Collected: {self.item_count}")

        # Action buttons (placeholders for Phase 1)
        with Horizontal(classes="button-row"):
            yield Button("Configure", id=f"{self.config_key}-configure")
            yield Button("Run Now", id=f"{self.config_key}-run")
            # Toggle button label based on status
            toggle_label = "Enable" if self.status == "disabled" else "Disable"
            yield Button(toggle_label, id=f"{self.config_key}-toggle")

    def watch_status(self, new_status: str) -> None:
        """Update header and toggle button when status changes.

        Args:
            new_status: The new status value ("running", "idle", "disabled")
        """
        if not self.is_mounted:
            return
        status_class = f"status-{new_status}"
        header = self.query_one(".card-header", Static)
        header.update(f"{self.scraper_name} - [{status_class}]{new_status.title()}[/]")
        toggle_label = "Enable" if new_status == "disabled" else "Disable"
        self.query_one(f"#{self.config_key}-toggle", Button).label = (
            toggle_label
        )

    def watch_progress(self, new_progress: float) -> None:
        """Update progress bar when progress changes.

        Args:
            new_progress: The new progress value (0.0 to 1.0)
        """
        if not self.is_mounted:
            return
        self.query_one(ProgressBar).progress = new_progress * 100
