#!/usr/bin/env python3
"""
RSS Feed Reader - Monitor and download content from RSS/Atom feeds
"""

import argparse
import sys
import re
from pathlib import Path
from datetime import datetime, timedelta
from urllib.parse import urlparse
import xml.etree.ElementTree as ET

try:
    import feedparser
    FEEDPARSER_AVAILABLE = True
except ImportError:
    FEEDPARSER_AVAILABLE = False
    print("Warning: feedparser not installed. Install with: pip install feedparser", file=sys.stderr)

import requests


DEFAULT_OUTPUT_DIR = "notebooklm_sources_rss"


def fetch_feed(feed_url: str, timeout: int = 10) -> dict:
    """
    Fetch and parse RSS/Atom feed.

    Args:
        feed_url: URL of the RSS/Atom feed
        timeout: Request timeout

    Returns:
        Parsed feed dictionary

    Raises:
        Exception: If feed cannot be fetched or parsed
    """
    if not FEEDPARSER_AVAILABLE:
        raise Exception("feedparser library required. Install with: pip install feedparser")

    feed = feedparser.parse(feed_url)

    if feed.bozo:
        # Feed has errors but might still be usable
        if hasattr(feed, 'entries') and feed.entries:
            return feed
        raise Exception(f"Failed to parse feed: {feed_url}")

    return feed


def filter_entries_by_date(entries: list, days_back: int = 7) -> list:
    """
    Filter feed entries by publication date.

    Args:
        entries: List of feed entries
        days_back: Number of days to look back

    Returns:
        Filtered list of entries
    """
    cutoff_date = datetime.now() - timedelta(days=days_back)
    filtered = []

    for entry in entries:
        # Try to get published date
        pub_date = None

        if hasattr(entry, 'published_parsed') and entry.published_parsed:
            pub_date = datetime(*entry.published_parsed[:6])
        elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
            pub_date = datetime(*entry.updated_parsed[:6])

        # If we can't determine date, include it to be safe
        if pub_date is None or pub_date >= cutoff_date:
            filtered.append(entry)

    return filtered


def format_entry(entry: dict, feed_title: str = "", tags: list = None) -> str:
    """
    Format a feed entry as markdown.

    Args:
        entry: Feed entry dictionary
        feed_title: Title of the feed
        tags: Optional tags to add

    Returns:
        Formatted markdown
    """
    title = entry.get('title', 'Untitled')
    link = entry.get('link', '')
    author = entry.get('author', feed_title or 'Unknown')

    # Get published date
    pub_date = 'Unknown'
    if hasattr(entry, 'published_parsed') and entry.published_parsed:
        pub_date = datetime(*entry.published_parsed[:6]).strftime('%Y-%m-%d')
    elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
        pub_date = datetime(*entry.updated_parsed[:6]).strftime('%Y-%m-%d')

    # Get content/summary
    content = ''
    if hasattr(entry, 'content') and entry.content:
        content = entry.content[0].get('value', '')
    elif hasattr(entry, 'summary'):
        content = entry.summary
    elif hasattr(entry, 'description'):
        content = entry.description

    # Clean HTML from content (basic)
    content = re.sub(r'<[^>]+>', '', content)
    content = content.replace('&nbsp;', ' ')
    content = content.replace('&amp;', '&')
    content = content.replace('&lt;', '<')
    content = content.replace('&gt;', '>')
    content = content.replace('&quot;', '"')

    # Build output
    output = f"""# {title}

**Author:** {author}
**Source:** {feed_title or 'RSS Feed'}
**Published:** {pub_date}
**Link:** {link}
"""

    if tags:
        output += f"**Tags:** {', '.join(tags)}\n"

    output += f"\n---\n\n{content.strip()}\n"

    return output


def generate_filename(entry: dict, feed_name: str = "") -> str:
    """
    Generate filename for feed entry.

    Args:
        entry: Feed entry
        feed_name: Name of feed

    Returns:
        Sanitized filename
    """
    title = entry.get('title', 'untitled')

    # Sanitize title
    title = re.sub(r'[^\w\s-]', '', title)
    title = re.sub(r'[-\s]+', '_', title)
    title = title[:50].strip('_').lower()

    # Get date
    date_str = 'unknown'
    if hasattr(entry, 'published_parsed') and entry.published_parsed:
        date_str = datetime(*entry.published_parsed[:6]).strftime('%Y%m%d')
    elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
        date_str = datetime(*entry.updated_parsed[:6]).strftime('%Y%m%d')

    # Sanitize feed name
    if feed_name:
        feed_name = re.sub(r'[^\w-]', '_', feed_name)[:20]
        return f"rss_{feed_name}_{date_str}_{title}"

    return f"rss_{date_str}_{title}"


def process_feed(feed_url: str, output_dir: str, feed_name: str = "",
                tags: list = None, days_back: int = 7,
                format_type: str = 'markdown', verbose: bool = True) -> list:
    """
    Process a single RSS feed.

    Args:
        feed_url: URL of RSS feed
        output_dir: Output directory
        feed_name: Optional name for the feed
        tags: Optional tags
        days_back: Days to look back
        format_type: Output format
        verbose: Whether to print progress

    Returns:
        List of saved file paths
    """
    if verbose:
        print(f"Fetching feed: {feed_url}")

    # Fetch feed
    feed = fetch_feed(feed_url)

    feed_title = feed_name or feed.feed.get('title', 'Unknown Feed')

    if verbose:
        print(f"  Feed: {feed_title}")
        print(f"  Total entries: {len(feed.entries)}")

    # Filter by date
    recent_entries = filter_entries_by_date(feed.entries, days_back)

    if verbose:
        print(f"  Recent entries (last {days_back} days): {len(recent_entries)}")

    if not recent_entries:
        return []

    # Process entries
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    saved_files = []

    for entry in recent_entries:
        # Format entry
        formatted = format_entry(entry, feed_title, tags)

        # Generate filename
        filename = generate_filename(entry, feed_name)
        ext = '.md' if format_type == 'markdown' else '.txt'
        filepath = output_dir / f"{filename}{ext}"

        # Save
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(formatted)

        saved_files.append(str(filepath))

        if verbose:
            print(f"    ✓ {entry.get('title', 'Untitled')[:60]}")

    return saved_files


def main():
    """Main entry point for CLI usage."""
    parser = argparse.ArgumentParser(
        description='Monitor and download content from RSS/Atom feeds',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Single feed
  %(prog)s https://blog.example.com/feed

  # With custom name and tags
  %(prog)s https://blog.example.com/feed --name "Example Blog" --tags tech leadership

  # Only last 3 days
  %(prog)s https://blog.example.com/feed --days 3

  # Multiple feeds from file
  %(prog)s -f feeds.txt

  # Obsidian format
  %(prog)s https://blog.example.com/feed --format obsidian

Feed File Format:
  url|name|tags
  https://example.com/feed|Example Blog|tech,leadership
  https://another.com/rss|Another Blog|innovation
        """
    )

    parser.add_argument(
        'feed_url',
        nargs='?',
        help='RSS/Atom feed URL'
    )

    parser.add_argument(
        '-f', '--file',
        help='File with feed URLs (format: url|name|tags per line)'
    )

    parser.add_argument(
        '-o', '--output-dir',
        default=DEFAULT_OUTPUT_DIR,
        help=f'Output directory (default: {DEFAULT_OUTPUT_DIR})'
    )

    parser.add_argument(
        '--name',
        help='Name for the feed (used in filenames)'
    )

    parser.add_argument(
        '--tags',
        nargs='+',
        help='Tags to add to entries'
    )

    parser.add_argument(
        '--days',
        type=int,
        default=7,
        help='Days to look back (default: 7)'
    )

    parser.add_argument(
        '--format',
        choices=['markdown', 'text', 'obsidian'],
        default='markdown',
        help='Output format (default: markdown)'
    )

    parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        help='Quiet mode'
    )

    args = parser.parse_args()

    if not FEEDPARSER_AVAILABLE:
        print("Error: feedparser library required", file=sys.stderr)
        print("Install with: pip install feedparser", file=sys.stderr)
        sys.exit(1)

    verbose = not args.quiet

    # Collect feeds to process
    feeds = []

    if args.file:
        # Read from file
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue

                    # Parse format: url|name|tags
                    parts = line.split('|')
                    url = parts[0].strip()
                    name = parts[1].strip() if len(parts) > 1 else ''
                    tags = parts[2].strip().split(',') if len(parts) > 2 else []
                    tags = [t.strip() for t in tags if t.strip()]

                    feeds.append((url, name, tags))

        except IOError as e:
            print(f"Error reading file: {e}", file=sys.stderr)
            sys.exit(1)

    elif args.feed_url:
        feeds.append((args.feed_url, args.name or '', args.tags or []))

    else:
        parser.print_help()
        print("\nError: Provide a feed URL or file with -f", file=sys.stderr)
        sys.exit(1)

    # Process feeds
    if verbose:
        print(f"Processing {len(feeds)} feed(s)...\n")

    total_entries = 0

    for feed_url, feed_name, tags in feeds:
        try:
            saved = process_feed(
                feed_url, args.output_dir, feed_name,
                tags, args.days, args.format, verbose
            )
            total_entries += len(saved)

            if verbose:
                print()

        except Exception as e:
            print(f"  ✗ Error processing {feed_url}: {e}", file=sys.stderr)
            continue

    # Summary
    if verbose:
        print(f"{'='*60}")
        print(f"Total entries saved: {total_entries}")
        print(f"Output directory: {args.output_dir}")
        print(f"{'='*60}")


if __name__ == '__main__':
    main()
