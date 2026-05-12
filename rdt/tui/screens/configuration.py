#!/usr/bin/env python3
"""Configuration screen for Research Digest TUI."""

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, VerticalScroll
from textual.screen import Screen
from textual.widgets import (
    Button,
    Checkbox,
    Footer,
    Header,
    Input,
    ListItem,
    ListView,
    Select,
    Static,
)
from .directory_picker import DirectoryPicker

_SCRAPER_KEYS = ["hackernews", "rss", "reddit", "arxiv"]
_SCRAPER_LABELS = {
    "hackernews": "HackerNews",
    "rss": "RSS Feeds",
    "reddit": "Reddit",
    "arxiv": "ArXiv",
}
_AUTH_OPTIONS = [("None", ""), ("Basic Auth", "basic"), ("Bearer Token", "bearer")]


class Configuration(Screen):
    """Configuration screen — scraper settings and global options."""

    def __init__(self, initial_scraper: str | None = None) -> None:
        super().__init__()
        self._initial_scraper = initial_scraper
        self._selected_key: str | None = None

    def compose(self) -> ComposeResult:
        """Build the configuration screen layout."""
        yield Header()
        yield Static("Configuration", classes="screen-title")

        with Horizontal(id="config-layout"):
            # Left panel: scraper selector
            with Container(id="config-left"):
                yield Static("Scrapers", classes="panel-heading")
                with ListView(id="scraper-list"):
                    for key in _SCRAPER_KEYS:
                        yield ListItem(Static(_SCRAPER_LABELS[key]), id=f"item-{key}")

            # Right panel: global + per-scraper forms
            with VerticalScroll(id="config-right"):
                # Global settings (always visible)
                yield Static("Global Settings", classes="section-heading")
                yield Static("Days Back (global):", classes="field-label")
                yield Input(id="global-days-back", placeholder="7")
                yield Static("Output Directory:", classes="field-label")
                with Horizontal(classes="dir-picker-row"):
                    yield Input(id="global-output-dir", placeholder="research_digest")
                    yield Button("Browse", id="browse-output-dir")
                yield Static("Credential Command:", classes="field-label")
                yield Input(
                    id="credential-command",
                    placeholder="protonpass item get {key}",
                )
                yield Static(
                    "Leave blank to disable. Install Proton Pass CLI from proton.me/pass",
                    classes="field-hint",
                )
                yield Button("Save Global Settings", id="save-global")
                yield Static("", id="error-global", classes="error-msg hidden")

                yield Static("─" * 40, classes="divider")

                # Scraper-specific form (hidden until a scraper is selected)
                with Container(id="scraper-form", classes="hidden"):
                    yield Static(
                        "", id="selected-scraper-title", classes="section-heading"
                    )
                    yield Checkbox("Enabled", id="scraper-enabled")
                    yield Static("Days Back:", classes="field-label")
                    yield Input(id="scraper-days-back", placeholder="7")
                    # HN-specific fields
                    with Container(id="hn-fields", classes="hidden"):
                        yield Static("Min Points:", classes="field-label")
                        yield Input(id="scraper-min-points", placeholder="50")
                        yield Static("Min Comments:", classes="field-label")
                        yield Input(id="scraper-min-comments", placeholder="20")
                        yield Static("Search Topics (comma-separated):", classes="field-label")
                        yield Input(id="hn-search-topics", placeholder="python, machine learning")
                    # ArXiv-specific fields
                    with Container(id="arxiv-fields", classes="hidden"):
                        yield Static("Max Results:", classes="field-label")
                        yield Input(id="scraper-max-results", placeholder="25")
                        yield Static("Search Queries (comma-separated):", classes="field-label")
                        yield Input(id="arxiv-search-queries", placeholder="cs.AI, quant-ph")
                    # Reddit-specific fields
                    with Container(id="reddit-fields", classes="hidden"):
                        yield Static("Time Filter:", classes="field-label")
                        yield Input(id="reddit-time-filter", placeholder="week")
                        yield Static("Subreddits (comma-separated):", classes="field-label")
                        yield Input(id="reddit-subreddits", placeholder="MachineLearning, Python")
                    yield Static("", id="error-scraper", classes="error-msg hidden")
                    with Horizontal(classes="form-actions"):
                        yield Button("Save", id="save-scraper")
                        yield Button("Cancel", id="cancel-scraper", variant="default")

                # RSS Feeds section (hidden until RSS selected)
                with Container(id="feeds-section", classes="hidden"):
                    yield Static("RSS Feeds", classes="section-heading")
                    yield Container(id="feeds-list")
                    yield Button("Add Feed", id="add-feed-btn")
                    # Inline add-feed form (hidden by default)
                    with Container(id="add-feed-form", classes="hidden"):
                        yield Static("Add New Feed", classes="subsection-heading")
                        yield Static("URL (required):", classes="field-label")
                        yield Input(
                            id="feed-url", placeholder="https://example.com/feed.xml"
                        )
                        yield Static("Name:", classes="field-label")
                        yield Input(id="feed-name", placeholder="Feed Name")
                        yield Static("Tags (comma-separated):", classes="field-label")
                        yield Input(id="feed-tags", placeholder="tag1, tag2")
                        yield Static("Auth Type:", classes="field-label")
                        yield Select(_AUTH_OPTIONS, id="feed-auth-type")
                        with Container(id="feed-username-row", classes="hidden"):
                            yield Static("Username:", classes="field-label")
                            yield Input(id="feed-username", placeholder="username")
                        with Container(id="feed-password-row", classes="hidden"):
                            yield Static("Password Key:", classes="field-label")
                            yield Input(
                                id="feed-password-key",
                                placeholder="credential-store-key",
                            )
                        yield Static("", id="error-feed", classes="error-msg hidden")
                        with Horizontal(classes="form-actions"):
                            yield Button("Save Feed", id="save-feed")
                            yield Button("Cancel", id="cancel-feed", variant="default")

        with Horizontal(classes="bottom-actions"):
            yield Button("Back", id="back")
        yield Footer()

    async def on_mount(self) -> None:
        """Load global settings and optionally pre-select a scraper on mount."""
        self._load_global_settings()
        if self._initial_scraper:
            await self._select_scraper(self._initial_scraper)

    def _load_global_settings(self) -> None:
        config = self.app.config_service.config
        self.query_one("#global-days-back", Input).value = str(config.days_back)
        cmd = self.app.config_service.get_credential_command() or ""
        self.query_one("#credential-command", Input).value = cmd
        out_dir = self.app.config_service.get_output_base_dir()
        self.query_one("#global-output-dir", Input).value = out_dir

    async def _select_scraper(self, key: str) -> None:
        list_view = self.query_one("#scraper-list", ListView)
        for i, item in enumerate(list_view.children):
            if item.id == f"item-{key}":
                list_view.index = i
                break
        self._show_scraper_form(key)

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Load the selected scraper's settings into the right panel."""
        item_id = event.item.id or ""
        if item_id.startswith("item-"):
            key = item_id[5:]
            self._selected_key = key
            self._show_scraper_form(key)

    def _show_scraper_form(self, key: str) -> None:
        self._selected_key = key
        form = self.query_one("#scraper-form")
        form.remove_class("hidden")

        scraper_cfg = self.app.config_service.get_scraper_config(key)
        title = self.query_one("#selected-scraper-title", Static)
        title.update(_SCRAPER_LABELS.get(key, key))

        # Populate common fields
        enabled = getattr(scraper_cfg, "enabled", False) if scraper_cfg else False
        self.query_one("#scraper-enabled", Checkbox).value = enabled

        days_back = getattr(scraper_cfg, "days_back", 7) if scraper_cfg else 7
        self.query_one("#scraper-days-back", Input).value = str(days_back)

        # Show/hide scraper-specific fields
        hn_fields = self.query_one("#hn-fields")
        arxiv_fields = self.query_one("#arxiv-fields")
        reddit_fields = self.query_one("#reddit-fields")
        feeds_section = self.query_one("#feeds-section")

        hn_fields.add_class("hidden")
        arxiv_fields.add_class("hidden")
        reddit_fields.add_class("hidden")
        feeds_section.add_class("hidden")

        if key == "hackernews" and scraper_cfg:
            hn_fields.remove_class("hidden")
            self.query_one("#scraper-min-points", Input).value = str(
                getattr(scraper_cfg, "min_points", 50)
            )
            self.query_one("#scraper-min-comments", Input).value = str(
                getattr(scraper_cfg, "min_comments", 20)
            )
            topics = getattr(scraper_cfg, "search_topics", [])
            self.query_one("#hn-search-topics", Input).value = ", ".join(topics)
        elif key == "arxiv" and scraper_cfg:
            arxiv_fields.remove_class("hidden")
            self.query_one("#scraper-max-results", Input).value = str(
                getattr(scraper_cfg, "max_results", 25)
            )
            queries = getattr(scraper_cfg, "search_queries", [])
            self.query_one("#arxiv-search-queries", Input).value = ", ".join(queries)
        elif key == "reddit" and scraper_cfg:
            reddit_fields.remove_class("hidden")
            self.query_one("#reddit-time-filter", Input).value = str(
                getattr(scraper_cfg, "time_filter", "week")
            )
            subs = getattr(scraper_cfg, "subreddits", [])
            sub_names = [getattr(sub, "name", "") for sub in subs] if subs else []
            self.query_one("#reddit-subreddits", Input).value = ", ".join(sub_names)
        elif key == "rss":
            feeds_section.remove_class("hidden")
            self._refresh_feeds_list()

        # Clear error
        self.query_one("#error-scraper", Static).add_class("hidden")

    def _refresh_feeds_list(self) -> None:
        feeds_list = self.query_one("#feeds-list", Container)
        feeds_list.remove_children()
        scraper_cfg = self.app.config_service.get_scraper_config("rss")
        if scraper_cfg is None:
            return
        feeds = getattr(scraper_cfg, "feeds", [])
        for i, feed in enumerate(feeds):
            auth_type = getattr(feed, "auth_type", None)
            prefix = "[LOCK] " if auth_type else ""
            feed_name = getattr(feed, "name", None) or str(getattr(feed, "url", ""))
            feed_url = str(getattr(feed, "url", ""))
            label = f"{prefix}{feed_name} ({feed_url})"
            row = Horizontal(classes="feed-row")
            feeds_list.mount(row)
            row.mount(
                Static(label, classes="feed-label"),
                Button("Remove", id=f"remove-feed-{i}", variant="error"),
            )

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Route button presses to save-global, save-scraper, or back actions."""
        btn_id = event.button.id or ""

        if btn_id == "back":
            # If pushed (from Configure button), pop; otherwise switch
            if len(self.app.screen_stack) > 2:
                self.app.pop_screen()
            else:
                self.app.switch_screen("dashboard")

        elif btn_id == "save-global":
            self._save_global_settings()

        elif btn_id == "browse-output-dir":
            def set_output_dir(path: str | None) -> None:
                if path:
                    self.query_one("#global-output-dir", Input).value = path

            current_path = self.query_one("#global-output-dir", Input).value
            self.app.push_screen(DirectoryPicker(start_path=current_path or "."), set_output_dir)

        elif btn_id == "save-scraper":
            self._save_scraper_settings()

        elif btn_id == "cancel-scraper":
            self.query_one("#scraper-form").add_class("hidden")
            self._selected_key = None

        elif btn_id == "add-feed-btn":
            self.query_one("#add-feed-form").remove_class("hidden")
            self.query_one("#add-feed-btn").disabled = True

        elif btn_id == "save-feed":
            self._save_feed()

        elif btn_id == "cancel-feed":
            self.query_one("#add-feed-form").add_class("hidden")
            self.query_one("#add-feed-btn").disabled = False

        elif btn_id.startswith("remove-feed-"):
            idx = int(btn_id[len("remove-feed-") :])
            self.app.config_service.remove_rss_feed(idx)
            self._refresh_feeds_list()

    def on_select_changed(self, event: Select.Changed) -> None:
        """Show or hide auth credential fields based on the selected auth type."""
        if event.select.id == "feed-auth-type":
            val = str(event.value) if event.value else ""
            username_row = self.query_one("#feed-username-row")
            password_row = self.query_one("#feed-password-row")
            if val == "basic":
                username_row.remove_class("hidden")
                password_row.remove_class("hidden")
            elif val == "bearer":
                username_row.add_class("hidden")
                password_row.remove_class("hidden")
            else:
                username_row.add_class("hidden")
                password_row.add_class("hidden")

    def _save_global_settings(self) -> None:
        error = self.query_one("#error-global", Static)
        error.add_class("hidden")
        try:
            days_back_str = self.query_one("#global-days-back", Input).value.strip()
            if not days_back_str.isdigit():
                error.update("Days Back must be a positive integer")
                error.remove_class("hidden")
                return
            days_back = int(days_back_str)
            cred_cmd = (
                self.query_one("#credential-command", Input).value.strip() or None
            )

            raw = self.app.config_service._get_raw()
            raw["days_back"] = days_back
            self.app.config_service.save()
            self.app.config_service.set_credential_command(cred_cmd)
            
            out_dir = self.query_one("#global-output-dir", Input).value.strip()
            if out_dir:
                self.app.config_service.set_output_base_dir(out_dir)

            self.app.notify("Global settings saved")
        except Exception as e:
            error.update(f"Error: {e}")
            error.remove_class("hidden")

    def _save_scraper_settings(self) -> None:
        key = self._selected_key
        if not key:
            return
        error = self.query_one("#error-scraper", Static)
        error.add_class("hidden")
        try:
            enabled = self.query_one("#scraper-enabled", Checkbox).value
            days_back_str = self.query_one("#scraper-days-back", Input).value.strip()
            if days_back_str and not days_back_str.isdigit():
                error.update("Days Back must be a positive integer")
                error.remove_class("hidden")
                return

            self.app.config_service.set_scraper_enabled(key, enabled)
            if days_back_str:
                self.app.config_service.set_scraper_field(
                    key, "days_back", int(days_back_str)
                )

            if key == "hackernews":
                pts = self.query_one("#scraper-min-points", Input).value.strip()
                comments = self.query_one("#scraper-min-comments", Input).value.strip()
                if pts and pts.isdigit():
                    self.app.config_service.set_scraper_field(
                        key, "min_points", int(pts)
                    )
                if comments and comments.isdigit():
                    self.app.config_service.set_scraper_field(
                        key, "min_comments", int(comments)
                    )
                topics_raw = self.query_one("#hn-search-topics", Input).value.strip()
                topics = [t.strip() for t in topics_raw.split(",") if t.strip()]
                self.app.config_service.set_scraper_field(key, "search_topics", topics)
            elif key == "arxiv":
                max_r = self.query_one("#scraper-max-results", Input).value.strip()
                if max_r and max_r.isdigit():
                    self.app.config_service.set_scraper_field(
                        key, "max_results", int(max_r)
                    )
                queries_raw = self.query_one("#arxiv-search-queries", Input).value.strip()
                queries = [q.strip() for q in queries_raw.split(",") if q.strip()]
                self.app.config_service.set_scraper_field(key, "search_queries", queries)
            elif key == "reddit":
                time_filter = self.query_one("#reddit-time-filter", Input).value.strip()
                if time_filter:
                    self.app.config_service.set_scraper_field(key, "time_filter", time_filter)
                
                subs_raw = self.query_one("#reddit-subreddits", Input).value.strip()
                sub_names = [s.strip() for s in subs_raw.split(",") if s.strip()]
                subs_dicts = [{"name": name, "min_upvotes": 50, "tags": []} for name in sub_names]
                self.app.config_service.set_scraper_field(key, "subreddits", subs_dicts)

            self.app.notify("Saved")
        except Exception as e:
            error.update(f"Error: {e}")
            error.remove_class("hidden")

    def _save_feed(self) -> None:
        error = self.query_one("#error-feed", Static)
        error.add_class("hidden")
        url = self.query_one("#feed-url", Input).value.strip()
        if not url:
            error.update("URL is required")
            error.remove_class("hidden")
            return
        # Basic URL validation
        try:
            import httpx

            httpx.URL(url)
        except Exception:
            error.update("Invalid URL format")
            error.remove_class("hidden")
            return

        name = self.query_one("#feed-name", Input).value.strip() or None
        tags_raw = self.query_one("#feed-tags", Input).value.strip()
        tags = [t.strip() for t in tags_raw.split(",") if t.strip()] if tags_raw else []
        auth_val = self.query_one("#feed-auth-type", Select).value
        auth_type = str(auth_val) if auth_val else None
        username = self.query_one("#feed-username", Input).value.strip() or None
        password_key = self.query_one("#feed-password-key", Input).value.strip() or None

        try:
            self.app.config_service.add_rss_feed(
                url=url,
                name=name,
                tags=tags,
                auth_type=auth_type if auth_type else None,
                username=username,
                password_key=password_key,
            )
            # Reset form
            for input_id in [
                "feed-url",
                "feed-name",
                "feed-tags",
                "feed-username",
                "feed-password-key",
            ]:
                self.query_one(f"#{input_id}", Input).value = ""
            self.query_one("#add-feed-form").add_class("hidden")
            self.query_one("#add-feed-btn").disabled = False
            self._refresh_feeds_list()
            self.app.notify("Feed added")
        except Exception as e:
            error.update(f"Error: {e}")
            error.remove_class("hidden")
