#!/usr/bin/env python3
"""RSS Scraper Plugin for the Research Digest Toolkit."""

import re
from datetime import datetime, timedelta
from pathlib import Path

import httpx
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential

from rdt.shared import database
from rdt.shared import utils
from rdt.shared.config_models import RSSConfig
from rdt.shared.http_client import get_sync_client, make_bearer_auth
from rdt.shared.rich_utils import print_error, print_info, print_section, print_warning

try:
    import feedparser

    FEEDPARSER_AVAILABLE = True
except ImportError:
    FEEDPARSER_AVAILABLE = False

from .base import ScraperBase

# --- Helper Functions (from the original rss_reader.py) ---


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception(
        lambda e: isinstance(e, (httpx.RequestError, httpx.HTTPStatusError))
    ),
    reraise=True,
)
def _fetch_feed(client: httpx.Client, feed_url: str, timeout: int = 10) -> dict:
    """Fetches and parses an RSS/Atom feed."""
    if not FEEDPARSER_AVAILABLE:
        raise ImportError(
            "feedparser library is required. Please run 'pip install feedparser'"
        )

    response = client.get(feed_url, timeout=timeout)
    response.raise_for_status()
    feed = feedparser.parse(response.content)
    if feed.bozo and not (hasattr(feed, "entries") and feed.entries):
        raise ValueError(f"Failed to parse feed: {feed_url}")
    return feed


def _filter_entries_by_date(entries: list, days_back: int) -> list:
    """Filters feed entries by publication date."""
    cutoff_date = datetime.now() - timedelta(days=days_back)
    filtered = []
    for entry in entries:
        pub_date = None
        # Handle feedparser's published_parsed (time.struct_time or None)
        try:
            struct_time = getattr(entry, "published_parsed", None)
            if struct_time:
                # Ensure it's subscriptable and has at least 6 elements
                pub_date = datetime(*struct_time[:6])
            else:
                struct_time = getattr(entry, "updated_parsed", None)
                if struct_time:
                    pub_date = datetime(*struct_time[:6])
        except (TypeError, ValueError, IndexError):
            # Fallback for invalid or missing dates: include them to be safe
            pass

        if pub_date is None or pub_date >= cutoff_date:
            filtered.append(entry)
    return filtered


def _format_entry(entry: dict, feed_title: str, tags: list) -> str:
    """Formats a single feed entry into a markdown string."""
    title = entry.get("title", "Untitled")
    link = entry.get("link", "")
    author = entry.get("author", feed_title or "Unknown")

    pub_date = "Unknown"
    struct_time = getattr(entry, "published_parsed", None) or getattr(entry, "updated_parsed", None)
    if struct_time:
        try:
            pub_date = datetime(*struct_time[:6]).strftime("%Y-%m-%d")
        except (TypeError, ValueError, IndexError):
            pass

    content = ""
    # Safely check for content list
    entry_content = getattr(entry, "content", None)
    if entry_content and isinstance(entry_content, list) and len(entry_content) > 0:
        try:
            content = entry_content[0].get("value", "")
        except (AttributeError, TypeError):
            pass
    
    if not content:
        content = getattr(entry, "summary", "")

    content = re.sub(r"<[^>]+>", "", str(content))  # Basic HTML cleaning

    # Escape straight quotes in YAML string values
    safe_title = title.replace('"', "\u201c").replace('"', "\u201d")
    safe_author = author.replace('"', "\u201c").replace('"', "\u201d")
    safe_feed_title = feed_title.replace('"', "\u201c").replace('"', "\u201d")

    # Build markdown output
    md_content = f"""---
type: rss
title: "{safe_title}"
author: "{safe_author}"
source: "{safe_feed_title}"
published: {pub_date}
link: {link}
tags: [rss, {", ".join(tags) if tags else ""}]
---

# {title}

**Source:** {feed_title or "RSS Feed"}
**Published:** {pub_date}
**Link:** <{link}>

---

{content.strip()}
"""
    return md_content


# --- Scraper Plugin Class ---


class RSSScraper(ScraperBase):
    """Scrapes content from a list of RSS feeds."""

    def __init__(self, verbose: bool = True):
        super().__init__(verbose)
        self.name = "RSS"
        self.client = get_sync_client()

    def run(self, config: RSSConfig, output_dir: Path, credential_service=None):
        """Processes RSS feeds based on the provided configuration.

        Args:
            config: The scraper-specific Pydantic configuration model.
            output_dir: The base directory Path object for raw output.
            credential_service: Optional CredentialService for authenticated feeds.
        """
        if not FEEDPARSER_AVAILABLE:
            print_warning(
                "Skipping RSS scraper: 'feedparser' not installed.", self.verbose
            )
            return

        print_section("📰 Scraping RSS Feeds", self.verbose)

        feeds = config.feeds
        days_back = config.days_back

        errors = []
        for feed_config in feeds:
            url = str(feed_config.url)
            name = feed_config.name
            tags = feed_config.tags
            auth_type = getattr(feed_config, "auth_type", None)
            password_key = getattr(feed_config, "password_key", None)
            username = getattr(feed_config, "username", None)

            if not url:
                continue

            print_info(f"Fetching feed: {name or url}", self.verbose)

            # Build per-feed client (authenticated if configured)
            if auth_type and password_key:
                if credential_service is None or not credential_service.is_available():
                    print_warning(
                        f"Skipping feed '{name or url}': no credential service configured",
                        self.verbose,
                    )
                    continue
                credential = credential_service.get_credential(password_key)
                if credential is None:
                    print_warning(
                        f"Skipping feed '{name or url}': credential unavailable "
                        f"for key '{password_key}'",
                        self.verbose,
                    )
                    continue
                if auth_type == "basic":
                    feed_auth = httpx.BasicAuth(username or "", credential)
                    feed_client = get_sync_client(use_cache=False, auth=feed_auth)
                elif auth_type == "bearer":
                    feed_client = get_sync_client(
                        use_cache=False, auth=make_bearer_auth(credential)
                    )
                else:
                    feed_client = self.client
            else:
                feed_client = self.client

            try:
                feed = _fetch_feed(feed_client, url)
                feed_title = name or feed.feed.get("title", "Unknown Feed")

                recent_entries = _filter_entries_by_date(feed.entries, days_back)
                print_info(f"Found {len(recent_entries)} recent entries.", self.verbose)

                for entry in recent_entries:
                    link = entry.get("link", "")
                    if not link:
                        continue

                    if database.item_exists("rss", link):
                        print_info(
                            f"Skipping (already processed): {entry.get('title', 'Untitled')[:60]}",
                            self.verbose,
                        )
                        continue

                    # Process new entry
                    title = entry.get("title", "Untitled")
                    content = _format_entry(entry, feed_title, tags)
                    filename = utils.generate_filename("rss", title, link)
                    filepath = output_dir / self.name.lower() / filename

                    utils.save_document(filepath, content, self.verbose)
                    database.add_item("rss", link, title=title, url=link)

            except Exception as e:
                err_msg = f"Feed {url}: {e}"
                print_error(f"Error processing feed {url}: {e}", self.verbose)
                errors.append(err_msg)
                continue

        if errors:
            print_error(f"RSS scraper completed with {len(errors)} errors.", self.verbose)
