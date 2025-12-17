#!/usr/bin/env python3
"""
HackerNews Scraper - Download HN stories and discussions
Uses the official HN Firebase API and Algolia search API.
"""

import argparse
import sys
import re
import time
from pathlib import Path
from datetime import datetime, timedelta
import requests
from urllib.parse import urlparse


# HN API endpoints
HN_API_BASE = "https://hacker-news.firebaseio.com/v0"
HN_ALGOLIA_SEARCH = "https://hn.algolia.com/api/v1"

DEFAULT_OUTPUT_DIR = "notebooklm_sources_hn"


class HNClient:
    """Client for HackerNews API."""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        })

    def get_item(self, item_id: int) -> dict:
        """Get item (story, comment, etc.) by ID."""
        url = f"{HN_API_BASE}/item/{item_id}.json"
        response = self.session.get(url, timeout=10)
        response.raise_for_status()
        return response.json()

    def get_top_stories(self, limit: int = 30) -> list:
        """Get top story IDs."""
        url = f"{HN_API_BASE}/topstories.json"
        response = self.session.get(url, timeout=10)
        response.raise_for_status()
        return response.json()[:limit]

    def get_best_stories(self, limit: int = 30) -> list:
        """Get best story IDs."""
        url = f"{HN_API_BASE}/beststories.json"
        response = self.session.get(url, timeout=10)
        response.raise_for_status()
        return response.json()[:limit]

    def search_stories(self, query: str, tags: str = "story",
                      num_results: int = 30, min_points: int = None) -> list:
        """
        Search HN using Algolia API.

        Args:
            query: Search query
            tags: story, comment, poll, etc.
            num_results: Number of results
            min_points: Minimum score

        Returns:
            List of story IDs
        """
        params = {
            'query': query,
            'tags': tags,
            'hitsPerPage': num_results
        }

        if min_points:
            params['numericFilters'] = f'points>={min_points}'

        url = f"{HN_ALGOLIA_SEARCH}/search"
        response = self.session.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        return [hit['objectID'] for hit in data.get('hits', [])]


def extract_hn_id(url: str) -> int:
    """
    Extract HN item ID from URL.

    Args:
        url: HN URL

    Returns:
        Item ID

    Raises:
        ValueError: If ID cannot be extracted
    """
    match = re.search(r'id=(\d+)', url)
    if match:
        return int(match.group(1))

    # Try to parse as direct ID
    if url.isdigit():
        return int(url)

    raise ValueError(f"Could not extract HN item ID from: {url}")


def fetch_story_with_comments(client: HNClient, story_id: int,
                              max_depth: int = 3, verbose: bool = True) -> dict:
    """
    Fetch a story and its comments recursively.

    Args:
        client: HN API client
        story_id: Story ID
        max_depth: Maximum comment depth to fetch
        verbose: Whether to print progress

    Returns:
        Dictionary with story and nested comments
    """
    if verbose:
        print(f"Fetching story {story_id}...")

    story = client.get_item(story_id)

    if not story:
        raise Exception(f"Story {story_id} not found")

    # Fetch comments recursively
    if story.get('kids'):
        if verbose:
            print(f"  Fetching {len(story['kids'])} top-level comments...")
        story['comments'] = fetch_comments_recursive(
            client, story['kids'], max_depth, 0, verbose
        )
    else:
        story['comments'] = []

    return story


def fetch_comments_recursive(client: HNClient, comment_ids: list,
                            max_depth: int, current_depth: int,
                            verbose: bool = True) -> list:
    """
    Recursively fetch comments.

    Args:
        client: HN API client
        comment_ids: List of comment IDs
        max_depth: Maximum depth
        current_depth: Current recursion depth
        verbose: Whether to print progress

    Returns:
        List of comment dictionaries with nested replies
    """
    if current_depth >= max_depth:
        return []

    comments = []

    for comment_id in comment_ids:
        try:
            comment = client.get_item(comment_id)

            if not comment or comment.get('deleted') or comment.get('dead'):
                continue

            # Fetch nested replies
            if comment.get('kids'):
                comment['replies'] = fetch_comments_recursive(
                    client, comment['kids'], max_depth, current_depth + 1, verbose
                )
            else:
                comment['replies'] = []

            comments.append(comment)

        except Exception as e:
            if verbose:
                print(f"    Warning: Failed to fetch comment {comment_id}: {e}",
                      file=sys.stderr)
            continue

    return comments


def format_story(story: dict, format_type: str = 'markdown',
                min_comment_score: int = 0) -> str:
    """
    Format a story with comments.

    Args:
        story: Story dictionary
        format_type: Output format (markdown, text, obsidian)
        min_comment_score: Minimum score for comments to include

    Returns:
        Formatted content
    """
    # Extract metadata
    title = story.get('title', 'Untitled')
    url = story.get('url', '')
    hn_url = f"https://news.ycombinator.com/item?id={story['id']}"
    by = story.get('by', 'unknown')
    score = story.get('score', 0)
    time_posted = datetime.fromtimestamp(story.get('time', 0))
    comment_count = story.get('descendants', 0)
    text = story.get('text', '')

    # Format based on type
    if format_type == 'obsidian':
        output = f"""---
type: hackernews
title: {title}
author: {by}
score: {score}
comments: {comment_count}
date: {time_posted.strftime('%Y-%m-%d')}
url: {url}
hn_url: {hn_url}
tags: [hackernews, discussion]
---

# {title}

**Posted by:** {by}
**Score:** {score} points
**Comments:** {comment_count}
**Date:** {time_posted.strftime('%Y-%m-%d %H:%M')}
"""
    else:
        output = f"""# {title}

**Posted by:** {by}
**Score:** {score} points
**Comments:** {comment_count}
**Date:** {time_posted.strftime('%Y-%m-%d %H:%M')}
"""

    # Add URL if external link
    if url:
        output += f"**Link:** {url}\n"

    output += f"**HN Discussion:** {hn_url}\n\n"

    # Add story text if it's a self-post
    if text:
        output += "---\n\n"
        output += f"{clean_html(text)}\n\n"

    # Add comments
    if story.get('comments'):
        output += "---\n\n## Discussion\n\n"
        output += format_comments(story['comments'], 0, min_comment_score, format_type)

    return output


def format_comments(comments: list, depth: int, min_score: int,
                   format_type: str = 'markdown') -> str:
    """
    Format comments hierarchically.

    Args:
        comments: List of comment dictionaries
        depth: Current nesting depth
        min_score: Minimum score threshold
        format_type: Output format

    Returns:
        Formatted comments
    """
    output = ""
    indent = "  " * depth

    for comment in comments:
        score = comment.get('score', 0)

        # Skip low-scored comments
        if score < min_score:
            continue

        by = comment.get('by', 'unknown')
        text = comment.get('text', '')

        if not text:
            continue

        # Format comment
        if format_type == 'obsidian' or format_type == 'markdown':
            output += f"{indent}**{by}** ({score} points):\n"
            output += f"{indent}> {clean_html(text).replace(chr(10), chr(10) + indent + '> ')}\n\n"
        else:
            output += f"{indent}[{by}] ({score} points):\n"
            output += f"{indent}{clean_html(text)}\n\n"

        # Add nested replies
        if comment.get('replies'):
            output += format_comments(comment['replies'], depth + 1, min_score, format_type)

    return output


def clean_html(html_text: str) -> str:
    """
    Clean HTML from HN text (basic cleaning).

    Args:
        html_text: HTML text

    Returns:
        Cleaned text
    """
    if not html_text:
        return ""

    # Basic HTML entity decoding and tag removal
    text = html_text.replace('&#x27;', "'")
    text = text.replace('&quot;', '"')
    text = text.replace('&gt;', '>')
    text = text.replace('&lt;', '<')
    text = text.replace('&amp;', '&')

    # Remove <p> tags but keep line breaks
    text = text.replace('<p>', '\n\n')
    text = text.replace('</p>', '')

    # Handle links
    text = re.sub(r'<a href="([^"]+)"[^>]*>([^<]+)</a>', r'[\2](\1)', text)

    # Remove other tags
    text = re.sub(r'<[^>]+>', '', text)

    # Clean up whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)

    return text.strip()


def generate_filename(story: dict) -> str:
    """
    Generate filename for story.

    Args:
        story: Story dictionary

    Returns:
        Sanitized filename
    """
    title = story.get('title', 'untitled')
    story_id = story.get('id', 'unknown')

    # Sanitize title
    title = re.sub(r'[^\w\s-]', '', title)
    title = re.sub(r'[-\s]+', '_', title)
    title = title[:50].strip('_')

    return f"hn_{story_id}_{title.lower()}"


def process_story(client: HNClient, story_id: int, output_dir: str,
                 format_type: str = 'markdown', max_depth: int = 3,
                 min_comment_score: int = 0, verbose: bool = True) -> str:
    """
    Process a single HN story.

    Args:
        client: HN API client
        story_id: Story ID
        output_dir: Output directory
        format_type: Output format
        max_depth: Maximum comment depth
        min_comment_score: Minimum comment score
        verbose: Whether to print progress

    Returns:
        Path to saved file
    """
    # Fetch story with comments
    story = fetch_story_with_comments(client, story_id, max_depth, verbose)

    # Format output
    formatted = format_story(story, format_type, min_comment_score)

    # Generate filename
    filename = generate_filename(story)
    ext = '.md' if format_type in ['markdown', 'obsidian'] else '.txt'

    # Save file
    output_path = Path(output_dir) / f"{filename}{ext}"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(formatted)

    if verbose:
        comment_count = story.get('descendants', 0)
        print(f"  ✓ Saved: {story.get('title', 'Untitled')[:60]}...")
        print(f"    {comment_count} comments → {output_path}")

    return str(output_path)


def main():
    """Main entry point for CLI usage."""
    parser = argparse.ArgumentParser(
        description='Download HackerNews stories and discussions',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Get top 10 stories
  %(prog)s --top 10

  # Get specific discussion
  %(prog)s https://news.ycombinator.com/item?id=39815976
  %(prog)s 39815976

  # Search for topics
  %(prog)s --search "platform engineering" --min-points 100

  # Filter by comment count
  %(prog)s --top 30 --min-comments 50

  # Obsidian format with deep comment threading
  %(prog)s --top 20 --format obsidian --depth 5

  # Only include high-quality comments
  %(prog)s 39815976 --min-comment-score 10

Story Sources:
  - Use --top for current top stories
  - Use --best for best stories
  - Use --search for keyword search
  - Use URL or ID for specific discussion
        """
    )

    parser.add_argument(
        'item',
        nargs='?',
        help='HN URL or item ID'
    )

    parser.add_argument(
        '--top',
        type=int,
        metavar='N',
        help='Get top N stories'
    )

    parser.add_argument(
        '--best',
        type=int,
        metavar='N',
        help='Get best N stories'
    )

    parser.add_argument(
        '--search',
        help='Search HN for stories matching query'
    )

    parser.add_argument(
        '-o', '--output-dir',
        default=DEFAULT_OUTPUT_DIR,
        help=f'Output directory (default: {DEFAULT_OUTPUT_DIR})'
    )

    parser.add_argument(
        '--format',
        choices=['markdown', 'text', 'obsidian'],
        default='markdown',
        help='Output format (default: markdown)'
    )

    parser.add_argument(
        '--depth',
        type=int,
        default=3,
        help='Maximum comment depth (default: 3)'
    )

    parser.add_argument(
        '--min-comments',
        type=int,
        default=0,
        help='Minimum number of comments (default: 0)'
    )

    parser.add_argument(
        '--min-points',
        type=int,
        help='Minimum story points/score'
    )

    parser.add_argument(
        '--min-comment-score',
        type=int,
        default=0,
        help='Minimum score for comments to include (default: 0)'
    )

    parser.add_argument(
        '--delay',
        type=int,
        default=1,
        help='Delay between requests in seconds (default: 1)'
    )

    parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        help='Quiet mode - minimal output'
    )

    args = parser.parse_args()

    verbose = not args.quiet
    client = HNClient()

    # Determine what to fetch
    story_ids = []

    if args.item:
        # Single item
        try:
            story_id = extract_hn_id(args.item)
            story_ids = [story_id]
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    elif args.top:
        if verbose:
            print(f"Fetching top {args.top} stories...")
        story_ids = client.get_top_stories(args.top)

    elif args.best:
        if verbose:
            print(f"Fetching best {args.best} stories...")
        story_ids = client.get_best_stories(args.best)

    elif args.search:
        if verbose:
            print(f"Searching for: {args.search}")
        story_ids = client.search_stories(
            args.search,
            num_results=30,
            min_points=args.min_points
        )
        if verbose:
            print(f"Found {len(story_ids)} results")

    else:
        parser.print_help()
        print("\nError: Specify --top, --best, --search, or provide a story URL/ID",
              file=sys.stderr)
        sys.exit(1)

    # Filter by comment count if specified
    if args.min_comments > 0:
        if verbose:
            print(f"Filtering by minimum {args.min_comments} comments...")

        filtered_ids = []
        for sid in story_ids:
            story = client.get_item(sid)
            if story and story.get('descendants', 0) >= args.min_comments:
                filtered_ids.append(sid)

        story_ids = filtered_ids

        if verbose:
            print(f"  {len(story_ids)} stories match criteria")

    if not story_ids:
        print("No stories to process")
        return

    # Process stories
    if verbose:
        print(f"\nProcessing {len(story_ids)} story(ies)...")
        print(f"Output directory: {args.output_dir}")
        print(f"Format: {args.format}, Max depth: {args.depth}\n")

    success_count = 0

    for i, story_id in enumerate(story_ids, 1):
        try:
            if verbose:
                print(f"\n[{i}/{len(story_ids)}]")

            process_story(
                client, story_id, args.output_dir,
                args.format, args.depth, args.min_comment_score, verbose
            )

            success_count += 1

            # Rate limiting
            if i < len(story_ids) and args.delay > 0:
                time.sleep(args.delay)

        except Exception as e:
            print(f"  ✗ Error processing story {story_id}: {e}", file=sys.stderr)
            continue

    # Summary
    if verbose:
        print(f"\n{'='*60}")
        print(f"Completed: {success_count}/{len(story_ids)} stories saved")
        print(f"{'='*60}")


if __name__ == '__main__':
    main()
