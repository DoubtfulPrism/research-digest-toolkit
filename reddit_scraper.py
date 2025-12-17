#!/usr/bin/env python3
"""
Reddit Scraper - Download top posts from subreddits
Uses Reddit's JSON API (no authentication required for public content).
"""

import argparse
import sys
import re
import time
from pathlib import Path
from datetime import datetime, timedelta
import requests


DEFAULT_OUTPUT_DIR = "notebooklm_sources_reddit"


def fetch_subreddit(subreddit: str, time_filter: str = 'week',
                   limit: int = 25, sort: str = 'top') -> list:
    """
    Fetch posts from a subreddit using Reddit's JSON API.

    Args:
        subreddit: Subreddit name (without r/)
        time_filter: Time filter (hour, day, week, month, year, all)
        limit: Number of posts to fetch
        sort: Sort method (hot, new, top, rising)

    Returns:
        List of post dictionaries
    """
    url = f"https://www.reddit.com/r/{subreddit}/{sort}.json"

    params = {
        'limit': limit,
        't': time_filter
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) research_tool/1.0'
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()

        data = response.json()

        if 'data' in data and 'children' in data['data']:
            return [child['data'] for child in data['data']['children']]

        return []

    except Exception as e:
        raise Exception(f"Failed to fetch r/{subreddit}: {e}")


def fetch_comments(post_id: str, subreddit: str, limit: int = 100) -> list:
    """
    Fetch comments for a post.

    Args:
        post_id: Reddit post ID
        subreddit: Subreddit name
        limit: Number of comments to fetch

    Returns:
        List of comment dictionaries
    """
    url = f"https://www.reddit.com/r/{subreddit}/comments/{post_id}.json"

    params = {'limit': limit}

    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) research_tool/1.0'
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()

        data = response.json()

        # Comments are in the second element of the array
        if len(data) > 1 and 'data' in data[1] and 'children' in data[1]['data']:
            return extract_comments_recursive(data[1]['data']['children'])

        return []

    except Exception as e:
        print(f"Warning: Failed to fetch comments: {e}", file=sys.stderr)
        return []


def extract_comments_recursive(children: list, depth: int = 0, max_depth: int = 3) -> list:
    """
    Recursively extract comments from Reddit's nested structure.

    Args:
        children: List of comment children
        depth: Current depth
        max_depth: Maximum depth to traverse

    Returns:
        Flat list of comments with depth info
    """
    if depth >= max_depth:
        return []

    comments = []

    for child in children:
        if child['kind'] != 't1':  # Not a comment
            continue

        comment_data = child['data']

        # Skip deleted/removed comments
        if comment_data.get('body') in ['[deleted]', '[removed]']:
            continue

        comment = {
            'author': comment_data.get('author', '[deleted]'),
            'body': comment_data.get('body', ''),
            'score': comment_data.get('score', 0),
            'depth': depth,
            'created': comment_data.get('created_utc', 0)
        }

        comments.append(comment)

        # Get replies
        if 'replies' in comment_data and comment_data['replies']:
            if isinstance(comment_data['replies'], dict):
                replies_data = comment_data['replies'].get('data', {})
                if 'children' in replies_data:
                    nested = extract_comments_recursive(
                        replies_data['children'],
                        depth + 1,
                        max_depth
                    )
                    comments.extend(nested)

    return comments


def format_post(post: dict, include_comments: bool = True,
               comments: list = None, format_type: str = 'markdown',
               tags: list = None) -> str:
    """
    Format a Reddit post as markdown.

    Args:
        post: Post dictionary
        include_comments: Whether to include comments
        comments: List of comments
        format_type: Output format
        tags: Optional tags

    Returns:
        Formatted content
    """
    title = post.get('title', 'Untitled')
    author = post.get('author', '[deleted]')
    subreddit = post.get('subreddit', 'unknown')
    score = post.get('score', 0)
    num_comments = post.get('num_comments', 0)
    url = f"https://www.reddit.com{post.get('permalink', '')}"
    created = datetime.fromtimestamp(post.get('created_utc', 0))

    selftext = post.get('selftext', '')
    post_url = post.get('url', '')

    # Build output
    if format_type == 'obsidian':
        output = f"""---
type: reddit
subreddit: {subreddit}
author: {author}
score: {score}
comments: {num_comments}
date: {created.strftime('%Y-%m-%d')}
url: {url}
tags: [reddit, {subreddit}"""

        if tags:
            output += f", {', '.join(tags)}"

        output += """]
---

"""

    else:
        output = ""

    output += f"""# {title}

**Subreddit:** r/{subreddit}
**Posted by:** u/{author}
**Score:** {score} points
**Comments:** {num_comments}
**Date:** {created.strftime('%Y-%m-%d %H:%M')}
**Link:** {url}
"""

    # Add external URL if different
    if post_url and post_url != url:
        output += f"**External Link:** {post_url}\n"

    # Add self text
    if selftext:
        output += f"\n---\n\n{selftext}\n"

    # Add comments
    if include_comments and comments:
        output += f"\n---\n\n## Comments ({len(comments)})\n\n"
        output += format_comments(comments, format_type)

    return output


def format_comments(comments: list, format_type: str = 'markdown') -> str:
    """
    Format comments hierarchically.

    Args:
        comments: List of comment dictionaries
        format_type: Output format

    Returns:
        Formatted comments
    """
    output = ""

    for comment in comments:
        indent = "  " * comment['depth']
        author = comment['author']
        body = comment['body']
        score = comment['score']

        if format_type == 'obsidian' or format_type == 'markdown':
            output += f"{indent}**{author}** ({score} points):\n"
            output += f"{indent}> {body.replace(chr(10), chr(10) + indent + '> ')}\n\n"
        else:
            output += f"{indent}[{author}] ({score} points):\n"
            output += f"{indent}{body}\n\n"

    return output


def generate_filename(post: dict, subreddit: str) -> str:
    """
    Generate filename for post.

    Args:
        post: Post dictionary
        subreddit: Subreddit name

    Returns:
        Sanitized filename
    """
    title = post.get('title', 'untitled')
    post_id = post.get('id', 'unknown')

    # Sanitize title
    title = re.sub(r'[^\w\s-]', '', title)
    title = re.sub(r'[-\s]+', '_', title)
    title = title[:50].strip('_').lower()

    return f"reddit_{subreddit}_{post_id}_{title}"


def process_subreddit(subreddit: str, output_dir: str, time_filter: str = 'week',
                     limit: int = 25, min_upvotes: int = 0,
                     include_comments: bool = True, max_comments: int = 50,
                     format_type: str = 'markdown', tags: list = None,
                     verbose: bool = True) -> list:
    """
    Process a subreddit and save posts.

    Args:
        subreddit: Subreddit name
        output_dir: Output directory
        time_filter: Time filter (week, month, etc.)
        limit: Number of posts to fetch
        min_upvotes: Minimum upvotes threshold
        include_comments: Whether to include comments
        max_comments: Maximum comments to include
        format_type: Output format
        tags: Optional tags
        verbose: Whether to print progress

    Returns:
        List of saved file paths
    """
    if verbose:
        print(f"Fetching r/{subreddit}...")

    # Fetch posts
    posts = fetch_subreddit(subreddit, time_filter, limit)

    # Filter by upvotes
    if min_upvotes > 0:
        posts = [p for p in posts if p.get('score', 0) >= min_upvotes]

    if verbose:
        print(f"  Found {len(posts)} posts (min {min_upvotes} upvotes)")

    if not posts:
        return []

    # Process posts
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    saved_files = []

    for i, post in enumerate(posts, 1):
        try:
            if verbose:
                print(f"  [{i}/{len(posts)}] {post.get('title', 'Untitled')[:60]}...")

            # Fetch comments if requested
            comments = []
            if include_comments:
                comments = fetch_comments(post['id'], subreddit, max_comments)
                # Sort by score
                comments.sort(key=lambda c: c['score'], reverse=True)

            # Format post
            formatted = format_post(post, include_comments, comments, format_type, tags)

            # Generate filename
            filename = generate_filename(post, subreddit)
            ext = '.md' if format_type in ['markdown', 'obsidian'] else '.txt'
            filepath = output_dir / f"{filename}{ext}"

            # Save
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(formatted)

            saved_files.append(str(filepath))

            if verbose:
                print(f"    ✓ Saved ({post.get('score', 0)} pts, {len(comments)} comments)")

            # Rate limiting
            time.sleep(1)

        except Exception as e:
            print(f"    ✗ Error: {e}", file=sys.stderr)
            continue

    return saved_files


def main():
    """Main entry point for CLI usage."""
    parser = argparse.ArgumentParser(
        description='Download top posts from Reddit subreddits',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Top posts from last week
  %(prog)s ExperiencedDevs

  # Top 50 posts with minimum 100 upvotes
  %(prog)s ExperiencedDevs --limit 50 --min-upvotes 100

  # Multiple subreddits
  %(prog)s ExperiencedDevs cscareerquestions productivity

  # Include comments, Obsidian format
  %(prog)s ObsidianMD --comments --format obsidian

  # Last month, no comments
  %(prog)s productivity --time month --no-comments

Time Filters:
  hour, day, week, month, year, all
        """
    )

    parser.add_argument(
        'subreddits',
        nargs='+',
        help='Subreddit name(s) (without r/)'
    )

    parser.add_argument(
        '-o', '--output-dir',
        default=DEFAULT_OUTPUT_DIR,
        help=f'Output directory (default: {DEFAULT_OUTPUT_DIR})'
    )

    parser.add_argument(
        '--time',
        choices=['hour', 'day', 'week', 'month', 'year', 'all'],
        default='week',
        help='Time filter (default: week)'
    )

    parser.add_argument(
        '--limit',
        type=int,
        default=25,
        help='Number of posts to fetch (default: 25)'
    )

    parser.add_argument(
        '--min-upvotes',
        type=int,
        default=0,
        help='Minimum upvotes (default: 0)'
    )

    parser.add_argument(
        '--comments',
        action='store_true',
        help='Include comments'
    )

    parser.add_argument(
        '--no-comments',
        action='store_true',
        help='Exclude comments (default)'
    )

    parser.add_argument(
        '--max-comments',
        type=int,
        default=50,
        help='Maximum comments per post (default: 50)'
    )

    parser.add_argument(
        '--format',
        choices=['markdown', 'text', 'obsidian'],
        default='markdown',
        help='Output format (default: markdown)'
    )

    parser.add_argument(
        '--tags',
        nargs='+',
        help='Tags to add (for Obsidian format)'
    )

    parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        help='Quiet mode'
    )

    args = parser.parse_args()

    verbose = not args.quiet
    include_comments = args.comments and not args.no_comments

    # Process subreddits
    if verbose:
        print(f"Processing {len(args.subreddits)} subreddit(s)...\n")

    total_posts = 0

    for subreddit in args.subreddits:
        try:
            saved = process_subreddit(
                subreddit, args.output_dir, args.time,
                args.limit, args.min_upvotes, include_comments,
                args.max_comments, args.format, args.tags, verbose
            )

            total_posts += len(saved)

            if verbose:
                print()

        except Exception as e:
            print(f"✗ Error processing r/{subreddit}: {e}\n", file=sys.stderr)
            continue

    # Summary
    if verbose:
        print(f"{'='*60}")
        print(f"Total posts saved: {total_posts}")
        print(f"Output directory: {args.output_dir}")
        print(f"{'='*60}")


if __name__ == '__main__':
    main()
