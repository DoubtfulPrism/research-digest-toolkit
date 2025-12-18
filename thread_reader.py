#!/usr/bin/env python3
"""
Twitter/X Thread Reader - Download and format Twitter threads
Uses Nitter (privacy-focused Twitter front-end) to avoid API costs.
"""

import argparse
import re
import sys
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup

# Nitter instances (fallback list - some may be down)
NITTER_INSTANCES = [
    "nitter.net",
    "nitter.poast.org",
    "nitter.privacydev.net",
    "nitter.freedit.eu",
    "nitter.darkness.services",
]

DEFAULT_OUTPUT_DIR = "notebooklm_sources_threads"


def extract_tweet_id(url: str) -> tuple:
    """
    Extract username and tweet ID from Twitter/X URL.

    Args:
        url: Twitter/X URL

    Returns:
        Tuple of (username, tweet_id)

    Raises:
        ValueError: If URL cannot be parsed
    """
    # Handle various Twitter URL formats
    patterns = [
        r"(?:twitter\.com|x\.com)/([^/]+)/status/(\d+)",
        r"(?:twitter\.com|x\.com)/i/web/status/(\d+)",
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            if len(match.groups()) == 2:
                return match.group(1), match.group(2)
            else:
                return None, match.group(1)

    raise ValueError(f"Could not parse Twitter URL: {url}")


def try_nitter_instance(
    instance: str, username: str, tweet_id: str, timeout: int = 10
) -> tuple:
    """
    Try to fetch thread from a Nitter instance.

    Args:
        instance: Nitter instance domain
        username: Twitter username
        tweet_id: Tweet ID
        timeout: Request timeout in seconds

    Returns:
        Tuple of (success: bool, html_content or error_message)
    """
    try:
        if username:
            url = f"https://{instance}/{username}/status/{tweet_id}"
        else:
            url = f"https://{instance}/i/web/status/{tweet_id}"

        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()

        return True, response.text

    except requests.exceptions.Timeout:
        return False, f"Timeout connecting to {instance}"
    except requests.exceptions.RequestException as e:
        return False, f"Error with {instance}: {str(e)}"


def fetch_thread(twitter_url: str, verbose: bool = True) -> str:
    """
    Fetch thread content using Nitter instances.

    Args:
        twitter_url: Twitter/X URL
        verbose: Whether to print progress

    Returns:
        HTML content of the thread

    Raises:
        Exception: If all Nitter instances fail
    """
    username, tweet_id = extract_tweet_id(twitter_url)

    if verbose:
        print(f"Fetching thread: {tweet_id}")
        print("Trying Nitter instances...")

    for instance in NITTER_INSTANCES:
        if verbose:
            print(f"  Trying {instance}...", end=" ")

        success, result = try_nitter_instance(instance, username, tweet_id)

        if success:
            if verbose:
                print("✓")
            return result
        else:
            if verbose:
                print(f"✗ ({result})")

    raise Exception(
        "All Nitter instances failed. Nitter may be experiencing issues.\n"
        "Alternative: Use https://threadreaderapp.com to unroll the thread,\n"
        "then paste the content into a file manually."
    )


def parse_thread(html_content: str) -> dict:
    """
    Parse thread from Nitter HTML.

    Args:
        html_content: HTML from Nitter

    Returns:
        Dictionary with thread metadata and tweets
    """
    soup = BeautifulSoup(html_content, "html.parser")

    # Extract thread info
    thread_data = {"author": None, "author_handle": None, "date": None, "tweets": []}

    # Get author info from main tweet
    main_tweet = soup.find("div", class_="main-tweet")
    if main_tweet:
        username_elem = main_tweet.find("a", class_="username")
        if username_elem:
            thread_data["author_handle"] = username_elem.text.strip()

        fullname_elem = main_tweet.find("a", class_="fullname")
        if fullname_elem:
            thread_data["author"] = fullname_elem.text.strip()

        date_elem = main_tweet.find("span", class_="tweet-date")
        if date_elem:
            date_link = date_elem.find("a")
            if date_link and date_link.get("title"):
                thread_data["date"] = date_link["title"]

    # Get all tweets in thread
    timeline = soup.find("div", class_="timeline")
    if timeline:
        tweets = timeline.find_all("div", class_="timeline-item")

        for tweet in tweets:
            tweet_content = tweet.find("div", class_="tweet-content")
            if tweet_content:
                # Extract text
                text = tweet_content.get_text(separator=" ", strip=True)

                # Clean up text
                text = re.sub(r"\s+", " ", text).strip()

                if text:
                    thread_data["tweets"].append(text)

    return thread_data


def format_thread(thread_data: dict, format_type: str = "markdown") -> str:
    """
    Format thread data for output.

    Args:
        thread_data: Parsed thread data
        format_type: Output format (markdown, text, obsidian)

    Returns:
        Formatted thread content
    """
    if format_type == "obsidian":
        output = f"""---
type: twitter-thread
author: {thread_data['author'] or 'Unknown'}
handle: {thread_data['author_handle'] or 'Unknown'}
date: {thread_data['date'] or 'Unknown'}
tags: [twitter, thread]
---

# Thread by {thread_data['author'] or thread_data['author_handle']}

**Author:** {thread_data['author']} ({thread_data['author_handle']})
**Date:** {thread_data['date']}

---

"""
    elif format_type == "markdown":
        output = f"""# Twitter Thread

**Author:** {thread_data['author']} ({thread_data['author_handle']})
**Date:** {thread_data['date']}

---

"""
    else:  # text
        output = f"""Twitter Thread
Author: {thread_data['author']} ({thread_data['author_handle']})
Date: {thread_data['date']}

---

"""

    # Add tweets
    for i, tweet in enumerate(thread_data["tweets"], 1):
        if format_type in ["markdown", "obsidian"]:
            output += f"{i}. {tweet}\n\n"
        else:
            output += f"[{i}] {tweet}\n\n"

    # Add metadata footer
    output += f"\n---\n\nTotal tweets: {len(thread_data['tweets'])}\n"

    return output


def generate_filename(thread_data: dict, tweet_id: str) -> str:
    """
    Generate a filename for the thread.

    Args:
        thread_data: Parsed thread data
        tweet_id: Tweet ID

    Returns:
        Sanitized filename
    """
    author = thread_data["author_handle"] or "unknown"
    author = author.replace("@", "").replace("/", "_")

    # Try to extract date
    date_str = "unknown"
    if thread_data["date"]:
        try:
            # Try to parse date
            date_str = thread_data["date"][:10].replace("/", "-")
        except (IndexError, AttributeError, TypeError):
            pass

    # Create filename
    filename = f"thread_{author}_{date_str}_{tweet_id}"

    # Sanitize
    filename = re.sub(r"[^\w\-_.]", "_", filename)

    return filename


def process_thread(
    url: str, output_dir: str, format_type: str = "markdown", verbose: bool = True
) -> str:
    """
    Process a single thread URL.

    Args:
        url: Twitter/X URL
        output_dir: Output directory
        format_type: Output format
        verbose: Whether to print progress

    Returns:
        Path to saved file

    Raises:
        Exception: If processing fails
    """
    # Fetch thread
    html_content = fetch_thread(url, verbose)

    # Parse thread
    if verbose:
        print("Parsing thread...")
    thread_data = parse_thread(html_content)

    if not thread_data["tweets"]:
        raise Exception(
            "No tweets found in thread. URL may not be a thread or Nitter parsing failed."
        )

    # Format output
    formatted = format_thread(thread_data, format_type)

    # Generate filename
    _, tweet_id = extract_tweet_id(url)
    filename = generate_filename(thread_data, tweet_id)

    # Determine extension
    ext = ".md" if format_type in ["markdown", "obsidian"] else ".txt"
    output_path = Path(output_dir) / f"{filename}{ext}"

    # Save file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(formatted)

    if verbose:
        tweet_count = len(thread_data["tweets"])
        print(f"  ✓ Saved {tweet_count} tweets to: {output_path}")

    return str(output_path)


def main():
    """Main entry point for CLI usage."""
    parser = argparse.ArgumentParser(
        description="Download and format Twitter/X threads (uses Nitter, no API needed)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s https://twitter.com/user/status/123456789
  %(prog)s https://x.com/user/status/123456789 --format obsidian
  %(prog)s -f threads.txt --batch
  %(prog)s https://twitter.com/user/status/123 -o custom_name.md

Notes:
  - Uses Nitter instances (no Twitter API required)
  - If Nitter is down, use threadreaderapp.com as fallback
  - For best results, use URLs of the first tweet in a thread
  - Rate limiting: Add --delay between batch requests

Alternative if Nitter is down:
  1. Visit https://threadreaderapp.com
  2. Paste the thread URL
  3. Copy the unrolled text
  4. Save manually
        """,
    )

    parser.add_argument("url", nargs="?", help="Twitter/X thread URL")

    parser.add_argument("-f", "--file", help="File with thread URLs (one per line)")

    parser.add_argument(
        "-o",
        "--output",
        help="Output file (for single thread) or directory (for batch)",
    )

    parser.add_argument(
        "-d",
        "--output-dir",
        default=DEFAULT_OUTPUT_DIR,
        help=f"Output directory (default: {DEFAULT_OUTPUT_DIR})",
    )

    parser.add_argument(
        "--format",
        choices=["markdown", "text", "obsidian"],
        default="markdown",
        help="Output format (default: markdown)",
    )

    parser.add_argument(
        "--delay",
        type=int,
        default=2,
        help="Delay between requests in batch mode (seconds, default: 2)",
    )

    parser.add_argument(
        "-q", "--quiet", action="store_true", help="Quiet mode - minimal output"
    )

    args = parser.parse_args()

    # Collect URLs
    urls = []

    if args.file:
        try:
            with open(args.file, "r", encoding="utf-8") as f:
                urls = [
                    line.strip()
                    for line in f
                    if line.strip() and not line.startswith("#")
                ]
        except IOError as e:
            print(f"Error reading file '{args.file}': {e}", file=sys.stderr)
            sys.exit(1)
    elif args.url:
        urls = [args.url]
    else:
        parser.print_help()
        print(
            "\nError: No URL provided. Use a URL or specify a file with -f",
            file=sys.stderr,
        )
        sys.exit(1)

    # Determine output directory
    output_dir = args.output if args.output and len(urls) > 1 else args.output_dir

    verbose = not args.quiet

    # Process threads
    success_count = 0
    total = len(urls)

    if verbose and total > 1:
        print(f"Processing {total} thread(s)...")
        print(f"Output directory: {output_dir}")
        print(f"Format: {args.format}\n")

    for i, url in enumerate(urls, 1):
        try:
            if verbose and total > 1:
                print(f"\n[{i}/{total}] {url}")

            # Single thread with custom output
            if total == 1 and args.output:
                html_content = fetch_thread(url, verbose)
                thread_data = parse_thread(html_content)
                formatted = format_thread(thread_data, args.format)

                with open(args.output, "w", encoding="utf-8") as f:
                    f.write(formatted)

                if verbose:
                    print(f"✓ Saved to: {args.output}")
            else:
                # Batch mode
                process_thread(url, output_dir, args.format, verbose)

            success_count += 1

            # Rate limiting for batch
            if i < total and args.delay > 0:
                time.sleep(args.delay)

        except Exception as e:
            print(f"  ✗ Error processing {url}: {e}", file=sys.stderr)
            continue

    # Summary
    if verbose and total > 1:
        print(f"\n{'='*60}")
        print(f"Completed: {success_count}/{total} threads saved")
        print(f"{'='*60}")


if __name__ == "__main__":
    main()
