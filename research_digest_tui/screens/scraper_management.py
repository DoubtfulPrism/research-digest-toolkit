#!/usr/bin/env python3
"""Scraper Management screen for Research Digest TUI."""

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, VerticalScroll
from textual.screen import ModalScreen, Screen
from textual.widgets import Button, Footer, Header, RichLog, Static


class ScraperOutputModal(ModalScreen):
    """Modal overlay showing live output while a scraper runs."""

    DEFAULT_CSS = """
    ScraperOutputModal {
        align: center middle;
    }
    ScraperOutputModal > Container {
        width: 80%;
        height: 80%;
        background: $surface;
        border: thick $primary;
        padding: 1;
    }
    ScraperOutputModal #modal-title {
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
    }
    ScraperOutputModal RichLog {
        height: 1fr;
        border: solid $panel;
        margin-bottom: 1;
    }
    ScraperOutputModal Button {
        margin-top: 1;
    }
    """

    def __init__(self, scraper_key: str, scraper_name: str) -> None:
        super().__init__()
        self._scraper_key = scraper_key
        self._scraper_name = scraper_name

    def compose(self) -> ComposeResult:
        """Build the modal layout with output log and close button."""
        with Container():
            yield Static(f"Running {self._scraper_name}...", id="modal-title")
            yield RichLog(id="output-log", markup=False, highlight=False)
            yield Button("Close", id="close-modal", disabled=True)

    def on_mount(self) -> None:
        """Start the scraper worker thread on mount."""
        self.run_worker(self._run_scraper, thread=True)

    def _run_scraper(self) -> None:
        log = self.query_one("#output-log", RichLog)

        def on_line(line: str) -> None:
            self.app.call_from_thread(log.write, line)

        def on_complete(success: bool) -> None:
            def update_ui() -> None:
                self.query_one("#close-modal", Button).disabled = False
                msg = "Done ✓" if success else "Failed ✗"
                self.query_one("#modal-title", Static).update(
                    f"{self._scraper_name} — {msg}"
                )

            self.app.call_from_thread(update_ui)

        self.app.runner_service.run_scraper(self._scraper_key, on_line, on_complete)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Dismiss the modal when the close button is pressed."""
        if event.button.id == "close-modal":
            self.dismiss()


class ScraperManagement(Screen):
    """Scraper Management screen showing all scrapers with detailed controls."""

    def compose(self) -> ComposeResult:
        """Build the scraper management screen layout."""
        yield Header()
        yield Static("Scraper Management", classes="screen-title")
        with VerticalScroll():
            yield Container(id="scrapers-list")
        with Horizontal(classes="bottom-actions"):
            yield Button("Add New Scraper", id="add-scraper", disabled=True)
            yield Button("Run All", id="run-all", disabled=True)
            yield Button("Back", id="back")
        yield Footer()

    async def on_mount(self) -> None:
        """Populate scraper rows on screen mount."""
        await self._populate_scrapers()

    async def _populate_scrapers(self) -> None:
        scraper_configs = self.app.config_service.get_scraper_configs()
        item_counts = self.app.data_service.get_item_counts_by_source()
        last_runs = self.app.data_service.get_last_run_per_source()

        scrapers_list = self.query_one("#scrapers-list", Container)
        for scraper in scraper_configs:
            key = scraper["config_key"]
            db_source = scraper["db_source"]
            enabled = scraper["enabled"]
            badge = "[ENABLED]" if enabled else "[DISABLED]"
            count = item_counts.get(db_source, 0)
            last_run_raw = last_runs.get(db_source, "Never")
            last_run = last_run_raw[:10] if last_run_raw != "Never" else "Never"

            row = Container(classes="scraper-row")
            await scrapers_list.mount(row)
            await row.mount(
                Static(f"{scraper['name']} {badge}", classes="scraper-name"),
                Static(scraper["config_summary"], classes="scraper-config"),
                Static(
                    f"Last Run: {last_run} | Items: {count}",
                    classes="scraper-last-run",
                ),
            )
            actions = Horizontal(classes="scraper-actions")
            await row.mount(actions)
            toggle_label = "Disable" if enabled else "Enable"
            await actions.mount(
                Button("Configure", id=f"{key}-configure"),
                Button("Run Now", id=f"{key}-run"),
                Button("View Logs", id=f"{key}-logs", disabled=True),
                Button(toggle_label, id=f"{key}-toggle"),
            )

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Route button presses to configure, run, toggle, or back actions."""
        btn_id = event.button.id or ""

        if btn_id == "back":
            self.app.switch_screen("dashboard")
            return

        if btn_id.endswith("-run"):
            key = btn_id[:-4]
            scraper_info = next(
                (
                    s
                    for s in self.app.config_service.get_scraper_configs()
                    if s["config_key"] == key
                ),
                None,
            )
            if scraper_info:
                self.app.push_screen(ScraperOutputModal(key, scraper_info["name"]))
            return

        if btn_id.endswith("-configure"):
            key = btn_id[:-10]
            from .configuration import Configuration

            self.app.push_screen(Configuration(initial_scraper=key))
            return

        if btn_id.endswith("-toggle"):
            key = btn_id[:-7]
            await self._handle_toggle(key)

    async def _handle_toggle(self, key: str) -> None:
        scraper_cfg = self.app.config_service.get_scraper_config(key)
        if scraper_cfg is None:
            return
        current_enabled = getattr(scraper_cfg, "enabled", False)
        self.app.config_service.set_scraper_enabled(key, not current_enabled)
        scrapers_list = self.query_one("#scrapers-list", Container)
        await scrapers_list.remove_children()
        await self._populate_scrapers()
