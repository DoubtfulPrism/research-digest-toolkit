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

_SECTION_KEYS = [
    "global",
    "hackernews",
    "rss",
    "reddit",
    "arxiv",
    "processing",
    "formats",
    "report",
    "topics",
]
_SECTION_LABELS = {
    "global": "Global Settings",
    "hackernews": "HackerNews",
    "rss": "RSS Feeds",
    "reddit": "Reddit",
    "arxiv": "ArXiv",
    "processing": "Processing",
    "formats": "Output Formats",
    "report": "Reporting",
    "topics": "Auto-Tagging Topics",
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
            # Left panel: section selector
            with Container(id="config-left"):
                yield Static("Sections", classes="panel-heading")
                with ListView(id="section-list"):
                    for key in _SECTION_KEYS:
                        yield ListItem(Static(_SECTION_LABELS[key]), id=f"item-{key}")

            # Right panel: dynamic forms
            with VerticalScroll(id="config-right"):
                # Global settings
                with Container(id="global-form", classes="hidden"):
                    yield Static("Global Settings", classes="section-heading")
                    yield Static("Days Back:", classes="field-label")
                    yield Input(id="global-days-back", placeholder="7")
                    yield Static("Output Directory:", classes="field-label")
                    with Horizontal(classes="dir-picker-row"):
                        yield Input(id="global-output-dir", placeholder="research_digest")
                        yield Button("Browse", id="browse-output-dir")
                    yield Static("Obsidian Vault Path:", classes="field-label")
                    yield Input(id="global-obsidian-vault", placeholder="/path/to/vault")
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

                # Scraper-specific form
                with Container(id="scraper-form", classes="hidden"):
                    yield Static(
                        "", id="selected-scraper-title", classes="section-heading"
                    )
                    yield Checkbox("Enabled", id="scraper-enabled")
                    yield Static("Days Back Override:", classes="field-label")
                    yield Input(id="scraper-days-back", placeholder="7")

                    # HN-specific fields
                    with Container(id="hn-fields", classes="hidden"):
                        yield Static("Min Points:", classes="field-label")
                        yield Input(id="scraper-min-points", placeholder="50")
                        yield Static("Min Comments:", classes="field-label")
                        yield Input(id="scraper-min-comments", placeholder="20")
                        yield Static(
                            "Search Topics (comma-separated):", classes="field-label"
                        )
                        yield Input(
                            id="hn-search-topics", placeholder="python, machine learning"
                        )

                    # ArXiv-specific fields
                    with Container(id="arxiv-fields", classes="hidden"):
                        yield Static("Max Results:", classes="field-label")
                        yield Input(id="scraper-max-results", placeholder="25")
                        yield Static(
                            "Search Queries (one per line):", classes="field-label"
                        )
                        yield Input(
                            id="arxiv-search-queries",
                            placeholder='"AI" OR "LLM"\n"edtech"',
                        )

                    # Reddit-specific fields
                    with Container(id="reddit-fields", classes="hidden"):
                        yield Static("Time Filter:", classes="field-label")
                        yield Input(id="reddit-time-filter", placeholder="week")
                        yield Static(
                            "Subreddits (comma-separated):", classes="field-label"
                        )
                        yield Input(
                            id="reddit-subreddits",
                            placeholder="MachineLearning, Python",
                        )

                    yield Static("", id="error-scraper", classes="error-msg hidden")
                    with Horizontal(classes="form-actions"):
                        yield Button("Save", id="save-scraper")
                        yield Button("Cancel", id="cancel-scraper", variant="default")

                # RSS Feeds section
                with Container(id="feeds-section", classes="hidden"):
                    yield Static("RSS Feeds", classes="section-heading")
                    yield Container(id="feeds-list")
                    yield Button("Add Feed", id="add-feed-btn")
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

                # Processing section
                with Container(id="processing-form", classes="hidden"):
                    yield Static("Processing Options", classes="section-heading")
                    yield Checkbox("Convert Documents", id="proc-convert")
                    yield Checkbox("Auto Tag", id="proc-autotag")
                    yield Checkbox("Format for Obsidian", id="proc-obsidian")
                    yield Checkbox("Split Large Files", id="proc-split")
                    yield Static("Max File Size (chars):", classes="field-label")
                    yield Input(id="proc-max-size", placeholder="400000")
                    yield Button("Save Processing Settings", id="save-processing")

                # Formats section
                with Container(id="formats-form", classes="hidden"):
                    yield Static("Output Formats", classes="section-heading")
                    yield Checkbox("Obsidian (.md)", id="format-obsidian")
                    yield Checkbox("Markdown (.md)", id="format-markdown")
                    yield Checkbox("Plain Text (.txt)", id="format-text")
                    yield Button("Save Formats", id="save-formats")

                # Report section
                with Container(id="report-form", classes="hidden"):
                    yield Static("Reporting", classes="section-heading")
                    yield Checkbox("Generate Summary", id="report-summary")
                    yield Checkbox("Email Report", id="report-email-enabled")
                    yield Static("Email Address:", classes="field-label")
                    yield Input(id="report-email-address", placeholder="you@example.com")
                    yield Button("Save Report Settings", id="save-report")

                # Topics section
                with Container(id="topics-section", classes="hidden"):
                    yield Static("Auto-Tagging Topics", classes="section-heading")
                    yield Static(
                        "Configure keyword lists that trigger specific tags in Obsidian.",
                        classes="field-hint",
                    )
                    yield Container(id="topics-list")
                    yield Button("Add New Topic", id="add-topic-btn")
                    with Container(id="add-topic-form", classes="hidden"):
                        yield Static("Add New Topic", classes="subsection-heading")
                        yield Static("Topic Name (Tag):", classes="field-label")
                        yield Input(id="topic-name", placeholder="software_leadership")
                        yield Static(
                            "Keywords (comma-separated):", classes="field-label"
                        )
                        yield Input(
                            id="topic-keywords",
                            placeholder="engineering culture, team lead",
                        )
                        with Horizontal(classes="form-actions"):
                            yield Button("Save Topic", id="save-topic")
                            yield Button("Cancel Topic", id="cancel-topic")

        with Horizontal(classes="bottom-actions"):
            yield Button("Back", id="back")
        yield Footer()

    async def on_mount(self) -> None:
        """Initialise the screen, defaulting to Global Settings."""
        if self._initial_scraper:
            await self._select_section(self._initial_scraper)
        else:
            await self._select_section("global")

    async def _select_section(self, key: str) -> None:
        list_view = self.query_one("#section-list", ListView)
        for i, item in enumerate(list_view.children):
            if item.id == f"item-{key}":
                list_view.index = i
                break
        self._show_section_form(key)

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Route section selection to the appropriate form display."""
        item_id = event.item.id or ""
        if item_id.startswith("item-"):
            key = item_id[5:]
            self._show_section_form(key)

    def _show_section_form(self, key: str) -> None:
        self._selected_key = key
        # Hide all forms first
        for form_id in [
            "#global-form",
            "#scraper-form",
            "#feeds-section",
            "#processing-form",
            "#formats-form",
            "#report-form",
            "#topics-section",
        ]:
            self.query_one(form_id).add_class("hidden")

        if key == "global":
            self.query_one("#global-form").remove_class("hidden")
            self._load_global_settings()
        elif key in ["hackernews", "reddit", "arxiv"]:
            self.query_one("#scraper-form").remove_class("hidden")
            self._show_scraper_form(key)
        elif key == "rss":
            self.query_one("#feeds-section").remove_class("hidden")
            self._refresh_feeds_list()
        elif key == "processing":
            self.query_one("#processing-form").remove_class("hidden")
            self._load_processing_settings()
        elif key == "formats":
            self.query_one("#formats-form").remove_class("hidden")
            self._load_formats_settings()
        elif key == "report":
            self.query_one("#report-form").remove_class("hidden")
            self._load_report_settings()
        elif key == "topics":
            self.query_one("#topics-section").remove_class("hidden")
            self._refresh_topics_list()

    def _load_global_settings(self) -> None:
        config = self.app.config_service.config
        self.query_one("#global-days-back", Input).value = str(config.days_back)
        self.query_one("#global-output-dir", Input).value = (
            config.output.base_dir or "research_digest"
        )
        self.query_one("#global-obsidian-vault", Input).value = (
            config.output.obsidian_vault or ""
        )
        self.query_one("#credential-command", Input).value = (
            config.credential_command or ""
        )

    def _show_scraper_form(self, key: str) -> None:
        scraper_cfg = self.app.config_service.get_scraper_config(key)
        title = self.query_one("#selected-scraper-title", Static)
        title.update(_SECTION_LABELS.get(key, key))

        self.query_one("#scraper-enabled", Checkbox).value = (
            getattr(scraper_cfg, "enabled", False) if scraper_cfg else False
        )
        self.query_one("#scraper-days-back", Input).value = str(
            getattr(scraper_cfg, "days_back", 7) if scraper_cfg else 7
        )

        # Hide sub-fields
        self.query_one("#hn-fields").add_class("hidden")
        self.query_one("#arxiv-fields").add_class("hidden")
        self.query_one("#reddit-fields").add_class("hidden")

        if key == "hackernews" and scraper_cfg:
            self.query_one("#hn-fields").remove_class("hidden")
            self.query_one("#scraper-min-points", Input).value = str(
                getattr(scraper_cfg, "min_points", 50)
            )
            self.query_one("#scraper-min-comments", Input).value = str(
                getattr(scraper_cfg, "min_comments", 20)
            )
            self.query_one("#hn-search-topics", Input).value = ", ".join(
                getattr(scraper_cfg, "search_topics", [])
            )
        elif key == "arxiv" and scraper_cfg:
            self.query_one("#arxiv-fields").remove_class("hidden")
            self.query_one("#scraper-max-results", Input).value = str(
                getattr(scraper_cfg, "max_results", 25)
            )
            queries = getattr(scraper_cfg, "search_queries", [])
            self.query_one("#arxiv-search-queries", Input).value = "\n".join(queries)
        elif key == "reddit" and scraper_cfg:
            self.query_one("#reddit-fields").remove_class("hidden")
            self.query_one("#reddit-time-filter", Input).value = getattr(
                scraper_cfg, "time_filter", "week"
            )
            subs = getattr(scraper_cfg, "subreddits", [])
            sub_names = [getattr(sub, "name", "") for sub in subs]
            self.query_one("#reddit-subreddits", Input).value = ", ".join(sub_names)

    def _load_processing_settings(self) -> None:
        proc = self.app.config_service.config.processing
        self.query_one("#proc-convert", Checkbox).value = proc.convert_documents
        self.query_one("#proc-autotag", Checkbox).value = proc.auto_tag
        self.query_one("#proc-obsidian", Checkbox).value = proc.format_for_obsidian
        self.query_one("#proc-split", Checkbox).value = proc.split_large_files
        self.query_one("#proc-max-size", Input).value = str(proc.max_file_size)

    def _load_formats_settings(self) -> None:
        fmt = self.app.config_service.config.formats
        self.query_one("#format-obsidian", Checkbox).value = getattr(
            fmt, "obsidian", True
        )
        self.query_one("#format-markdown", Checkbox).value = getattr(
            fmt, "markdown", True
        )
        self.query_one("#format-text", Checkbox).value = getattr(fmt, "plain_text", False)

    def _load_report_settings(self) -> None:
        rep = self.app.config_service.config.report
        self.query_one("#report-summary", Checkbox).value = rep.generate_summary
        self.query_one("#report-email-enabled", Checkbox).value = rep.email_report
        self.query_one("#report-email-address", Input).value = rep.email_address or ""

    def _refresh_topics_list(self) -> None:
        topics_list = self.query_one("#topics-list", Container)
        topics_list.remove_children()
        topics = self.app.config_service.config.topics
        for name, keywords in topics.items():
            row = Horizontal(classes="topic-row")
            topics_list.mount(row)
            row.mount(
                Static(f"[b]{name}[/b]: {', '.join(keywords)}", classes="topic-label"),
                Button("Remove", id=f"remove-topic-{name}", variant="error"),
            )

    def _refresh_feeds_list(self) -> None:
        feeds_list = self.query_one("#feeds-list", Container)
        feeds_list.remove_children()
        scraper_cfg = self.app.config_service.get_scraper_config("rss")
        if not scraper_cfg:
            return
        for i, feed in enumerate(getattr(scraper_cfg, "feeds", [])):
            auth_type = getattr(feed, "auth_type", None)
            prefix = "[LOCK] " if auth_type else ""
            label = f"{prefix}{getattr(feed, 'name', '')} ({getattr(feed, 'url', '')})"
            row = Horizontal(classes="feed-row")
            feeds_list.mount(row)
            row.mount(
                Static(label, classes="feed-label"),
                Button("Remove", id=f"remove-feed-{i}", variant="error"),
            )

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Route button events to specialized save handlers or navigation."""
        btn_id = event.button.id or ""

        if btn_id == "back":
            if len(self.app.screen_stack) > 2:
                self.app.pop_screen()
            else:
                self.app.switch_screen("dashboard")
        elif btn_id == "save-global":
            self._save_global_settings()
        elif btn_id == "save-scraper":
            self._save_scraper_settings()
        elif btn_id == "save-processing":
            self._save_processing_settings()
        elif btn_id == "save-formats":
            self._save_formats_settings()
        elif btn_id == "save-report":
            self._save_report_settings()
        elif btn_id == "add-topic-btn":
            self.query_one("#add-topic-form").remove_class("hidden")
        elif btn_id == "save-topic":
            self._save_topic()
        elif btn_id == "cancel-topic":
            self.query_one("#add-topic-form").add_class("hidden")
        elif btn_id.startswith("remove-topic-"):
            name = btn_id[len("remove-topic-") :]
            self.app.config_service.remove_topic(name)
            self._refresh_topics_list()
        elif btn_id == "browse-output-dir":
            self.app.push_screen(
                DirectoryPicker(
                    start_path=self.query_one("#global-output-dir", Input).value or "."
                ),
                lambda p: setattr(
                    self.query_one("#global-output-dir", Input), "value", p or ""
                )
                if p
                else None,
            )
        elif btn_id == "add-feed-btn":
            self.query_one("#add-feed-form").remove_class("hidden")
        elif btn_id == "save-feed":
            self._save_feed()
        elif btn_id == "cancel-feed":
            self.query_one("#add-feed-form").add_class("hidden")
        elif btn_id.startswith("remove-feed-"):
            idx = int(btn_id[len("remove-feed-") :])
            self.app.config_service.remove_rss_feed(idx)
            self._refresh_feeds_list()

    def _save_global_settings(self) -> None:
        try:
            days = int(self.query_one("#global-days-back", Input).value)
            out_dir = self.query_one("#global-output-dir", Input).value
            vault = self.query_one("#global-obsidian-vault", Input).value or None
            cred = self.query_one("#credential-command", Input).value or None

            raw = self.app.config_service._get_raw()
            raw["days_back"] = days
            if "output" not in raw:
                from ruamel.yaml import CommentedMap
                raw["output"] = CommentedMap()
            raw["output"]["base_dir"] = out_dir
            raw["output"]["obsidian_vault"] = vault
            raw["credential_command"] = cred
            self.app.config_service.save()
            self.app.notify("Global settings saved")
        except Exception as e:
            self.app.notify(f"Save failed: {e}", severity="error")

    def _save_scraper_settings(self) -> None:
        key = self._selected_key
        if not key:
            return
        try:
            enabled = self.query_one("#scraper-enabled", Checkbox).value
            days = int(self.query_one("#scraper-days-back", Input).value)
            self.app.config_service.set_scraper_enabled(key, enabled)
            self.app.config_service.set_scraper_field(key, "days_back", days)

            if key == "hackernews":
                self.app.config_service.set_scraper_field(
                    key,
                    "min_points",
                    int(self.query_one("#scraper-min-points", Input).value),
                )
                self.app.config_service.set_scraper_field(
                    key,
                    "min_comments",
                    int(self.query_one("#scraper-min-comments", Input).value),
                )
                topics = [
                    t.strip()
                    for t in self.query_one("#hn-search-topics", Input).value.split(",")
                    if t.strip()
                ]
                self.app.config_service.set_scraper_field(key, "search_topics", topics)
            elif key == "arxiv":
                self.app.config_service.set_scraper_field(
                    key,
                    "max_results",
                    int(self.query_one("#scraper-max-results", Input).value),
                )
                queries = [
                    q.strip()
                    for q in self.query_one("#arxiv-search-queries", Input).value.split(
                        "\n"
                    )
                    if q.strip()
                ]
                self.app.config_service.set_scraper_field(key, "search_queries", queries)
            elif key == "reddit":
                self.app.config_service.set_scraper_field(
                    key, "time_filter", self.query_one("#reddit-time-filter", Input).value
                )
                sub_names = [
                    s.strip()
                    for s in self.query_one("#reddit-subreddits", Input).value.split(",")
                    if s.strip()
                ]
                # Use the new non-destructive update method
                self.app.config_service.update_reddit_subreddits(sub_names)

            self.app.notify(f"{_SECTION_LABELS[key]} saved")
        except Exception as e:
            self.app.notify(f"Save failed: {e}", severity="error")

    def _save_processing_settings(self) -> None:
        try:
            svc = self.app.config_service
            svc.set_processing_field(
                "convert_documents", self.query_one("#proc-convert", Checkbox).value
            )
            svc.set_processing_field(
                "auto_tag", self.query_one("#proc-autotag", Checkbox).value
            )
            svc.set_processing_field(
                "format_for_obsidian", self.query_one("#proc-obsidian", Checkbox).value
            )
            svc.set_processing_field(
                "split_large_files", self.query_one("#proc-split", Checkbox).value
            )
            svc.set_processing_field(
                "max_file_size", int(self.query_one("#proc-max-size", Input).value)
            )
            self.app.notify("Processing settings saved")
        except Exception as e:
            self.app.notify(f"Save failed: {e}", severity="error")

    def _save_formats_settings(self) -> None:
        try:
            svc = self.app.config_service
            svc.set_format_field(
                "obsidian", self.query_one("#format-obsidian", Checkbox).value
            )
            svc.set_format_field(
                "markdown", self.query_one("#format-markdown", Checkbox).value
            )
            svc.set_format_field(
                "plain_text", self.query_one("#format-text", Checkbox).value
            )
            self.app.notify("Output formats saved")
        except Exception as e:
            self.app.notify(f"Save failed: {e}", severity="error")

    def _save_report_settings(self) -> None:
        try:
            svc = self.app.config_service
            svc.set_report_field(
                "generate_summary", self.query_one("#report-summary", Checkbox).value
            )
            svc.set_report_field(
                "email_report", self.query_one("#report-email-enabled", Checkbox).value
            )
            svc.set_report_field(
                "email_address", self.query_one("#report-email-address", Input).value
            )
            self.app.notify("Report settings saved")
        except Exception as e:
            self.app.notify(f"Save failed: {e}", severity="error")

    def _save_topic(self) -> None:
        name = self.query_one("#topic-name", Input).value.strip()
        keywords_raw = self.query_one("#topic-keywords", Input).value.strip()
        if not name or not keywords_raw:
            self.app.notify("Name and keywords are required", severity="warning")
            return
        keywords = [k.strip() for k in keywords_raw.split(",") if k.strip()]
        self.app.config_service.set_topic(name, keywords)
        self.query_one("#topic-name", Input).value = ""
        self.query_one("#topic-keywords", Input).value = ""
        self.query_one("#add-topic-form").add_class("hidden")
        self._refresh_topics_list()
        self.app.notify(f"Topic '{name}' saved")

    def _save_feed(self) -> None:
        url = self.query_one("#feed-url", Input).value.strip()
        if not url:
            return
        name = self.query_one("#feed-name", Input).value.strip() or None
        tags = [
            t.strip()
            for t in self.query_one("#feed-tags", Input).value.split(",")
            if t.strip()
        ]
        auth = self.query_one("#feed-auth-type", Select).value
        user = self.query_one("#feed-username", Input).value.strip() or None
        pwd = self.query_one("#feed-password-key", Input).value.strip() or None

        self.app.config_service.add_rss_feed(
            url=url,
            name=name,
            tags=tags,
            auth_type=str(auth) if auth else None,
            username=user,
            password_key=pwd,
        )
        self.query_one("#add-feed-form").add_class("hidden")
        self._refresh_feeds_list()
        self.app.notify("RSS feed added")
