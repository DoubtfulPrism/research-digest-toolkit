#!/usr/bin/env python3
"""
RSS Scraper Plugin for the Research Digest Toolkit.
"""

import sys
import re
from pathlib import Path
from datetime import datetime, timedelta

import database
import utils

try:
    import feedparser
    FEEDPARSER_AVAILABLE = True
except ImportError:
    FEEDPARSER_AVAILABLE = False

from .base import ScraperBase

# --- Helper Functions (from the original rss_reader.py) ---

def _fetch_feed(feed_url: str, timeout: int = 10) -> dict:
    """Fetches and parses an RSS/Atom feed."""
    if not FEEDPARSER_AVAILABLE:
        raise ImportError("feedparser library is required. Please run 'pip install feedparser'")
    
    feed = feedparser.parse(feed_url)
    if feed.bozo and not (hasattr(feed, 'entries') and feed.entries):
        raise ValueError(f"Failed to parse feed: {feed_url}")
    return feed

def _filter_entries_by_date(entries: list, days_back: int) -> list:
    """Filters feed entries by publication date."""
    cutoff_date = datetime.now() - timedelta(days=days_back)
    filtered = []
    for entry in entries:
        pub_date = None
        if hasattr(entry, 'published_parsed') and entry.published_parsed:
            pub_date = datetime(*entry.published_parsed[:6])
        elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
            pub_date = datetime(*entry.updated_parsed[:6])
        
        if pub_date is None or pub_date >= cutoff_date:
            filtered.append(entry)
    return filtered

def _format_entry(entry: dict, feed_title: str, tags: list) -> str:
    """Formats a single feed entry into a markdown string."""
    title = entry.get('title', 'Untitled')
    link = entry.get('link', '')
    author = entry.get('author', feed_title or 'Unknown')

    pub_date = 'Unknown'
    if hasattr(entry, 'published_parsed') and entry.published_parsed:
        pub_date = datetime(*entry.published_parsed[:6]).strftime('%Y-%m-%d')

    content = ''
    if hasattr(entry, 'content') and entry.content:
        content = entry.content[0].get('value', '')
    elif hasattr(entry, 'summary'):
        content = entry.summary
    
    content = re.sub(r'<[^>]+>', '', content) # Basic HTML cleaning

    # Build markdown output
    md_content = f"""---
type: rss
title: "{title.replace('"', '“')}"
author: "{author.replace('"', '“')}"
source: "{feed_title.replace('"', '“')}"
published: {pub_date}
link: {link}
tags: [rss, {', '.join(tags) if tags else ''}]
---

# {title}

**Source:** {feed_title or 'RSS Feed'}
**Published:** {pub_date}
**Link:** <{link}>

---

{content.strip()}
"""
    return md_content

# --- Scraper Plugin Class ---

class RSSScraper(ScraperBase):
    """
    Scrapes content from a list of RSS feeds.
    """
    def __init__(self, verbose: bool = True):
        super().__init__(verbose)
        self.name = "RSS"

    def run(self, config: dict, output_dir: Path):
        """
        Processes RSS feeds based on the provided configuration.

        Args:
            config: The scraper-specific configuration dictionary.
            output_dir: The base directory Path object for raw output.
        """
        if not FEEDPARSER_AVAILABLE:
            if self.verbose:
                print("  - Skipping RSS scraper: 'feedparser' not installed.")
            return

        if self.verbose:
            print("📰 Scraping RSS Feeds...")

        feeds = config.get('feeds', [])
        days_back = config.get('days_back', 7)
        
        for feed_config in feeds:
            url = feed_config.get('url')
            name = feed_config.get('name', '')
            tags = feed_config.get('tags', [])

            if not url:
                continue

            if self.verbose:
                print(f"  -> Fetching feed: {name or url}")

            try:
                feed = _fetch_feed(url)
                feed_title = name or feed.feed.get('title', 'Unknown Feed')
                
                recent_entries = _filter_entries_by_date(feed.entries, days_back)
                if self.verbose:
                    print(f"     Found {len(recent_entries)} recent entries.")

                for entry in recent_entries:
                    link = entry.get('link', '')
                    if not link:
                        continue

                    if database.item_exists('rss', link):
                        if self.verbose:
                            print(f"    - Skipping (already processed): {entry.get('title', 'Untitled')[:60]}")
                        continue
                    
                    # Process new entry
                    title = entry.get('title', 'Untitled')
                    content = _format_entry(entry, feed_title, tags)
                    filename = utils.generate_filename('rss', title, link)
                    filepath = output_dir / self.name.lower() / filename
                    
                    utils.save_document(filepath, content, self.verbose)
                    database.add_item('rss', link)

            except Exception as e:
                if self.verbose:
                    print(f"    ✗ Error processing feed {url}: {e}", file=sys.stderr)
                continue
