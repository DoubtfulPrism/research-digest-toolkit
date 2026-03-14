#!/usr/bin/env python3
"""Reddit Scraper Plugin for the Research Digest Toolkit."""

import time
from datetime import datetime
from pathlib import Path

import httpx
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential

import database
import utils
from config_models import RedditConfig
from http_client import get_sync_client
from rich_utils import print_error, print_info, print_section

from .base import ScraperBase

# --- Helper Functions ---


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception(
        lambda e: isinstance(e, (httpx.RequestError, httpx.HTTPStatusError))
    ),
    reraise=True,
)
def _fetch_subreddit(
    client: httpx.Client, subreddit: str, time_filter: str, limit: int
) -> list:
    """Fetches posts from a subreddit's JSON API."""
    url = f"https://www.reddit.com/r/{subreddit}/top.json"
    params = {"limit": limit, "t": time_filter}
    headers = {"User-Agent": "Mozilla/5.0 Research Digest Scraper"}

    response = client.get(url, params=params, headers=headers, timeout=15)
    response.raise_for_status()
    data = response.json()
    return [child["data"] for child in data.get("data", {}).get("children", [])]


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception(
        lambda e: isinstance(e, (httpx.RequestError, httpx.HTTPStatusError))
    ),
    reraise=True,
)
def _fetch_comments(
    client: httpx.Client, post_id: str, subreddit: str, limit: int
) -> list:
    """Fetches comments for a given post."""
    url = f"https://www.reddit.com/r/{subreddit}/comments/{post_id}.json"
    params = {"limit": limit, "depth": 3}
    headers = {"User-Agent": "Mozilla/5.0 Research Digest Scraper"}

    response = client.get(url, params=params, headers=headers, timeout=15)
    response.raise_for_status()
    data = response.json()

    if len(data) > 1 and "data" in data[1] and "children" in data[1]["data"]:
        return _extract_comments_recursive(data[1]["data"]["children"])
    return []


def _extract_comments_recursive(children: list, depth: int = 0) -> list:
    """Recursively extracts and flattens comments from the Reddit API structure."""
    comments = []
    for child in children:
        if child["kind"] != "t1":
            continue

        comment_data = child["data"]
        if comment_data.get("body") in ["[deleted]", "[removed]"]:
            continue

        comments.append(
            {
                "author": comment_data.get("author", "[deleted]"),
                "body": comment_data.get("body", ""),
                "score": comment_data.get("score", 0),
                "depth": depth,
            }
        )

        if "replies" in comment_data and isinstance(comment_data.get("replies"), dict):
            replies_data = comment_data["replies"].get("data", {})
            if "children" in replies_data:
                comments.extend(
                    _extract_comments_recursive(replies_data["children"], depth + 1)
                )
    return comments


def _format_post(post: dict, comments: list, tags: list) -> str:
    """Formats a post and its comments into a markdown string."""
    title = post.get("title", "Untitled")
    subreddit = post.get("subreddit", "unknown")
    permalink = f"https://www.reddit.com{post.get('permalink', '')}"

    md_content = f"""---
type: reddit
title: \"{title.replace('"', '"')}\"
subreddit: {subreddit}
author: \"{post.get('author', '[deleted]')}\"
score: {post.get('score', 0)}
comments: {post.get('num_comments', 0)}
date: {datetime.fromtimestamp(post.get('created_utc', 0)).strftime('%Y-%m-%d')}
url: {permalink}
tags: [reddit, {subreddit}{', ' if tags else ''}{', '.join(tags) if tags else ''}]
---

# {title}

**Subreddit:** r/{subreddit}
**Posted by:** u/{post.get('author', '[deleted]')}
**Score:** {post.get('score', 0)} points
**Link:** <{permalink}>
"""
    if post.get("selftext"):
        md_content += f"\n---\n\n{post.get('selftext')}\n"

    if comments:
        md_content += "\n---\n\n## Comments\n\n"
        for comment in comments:
            indent = "  " * comment["depth"]
            md_content += (
                f"{indent}**{comment['author']}** ({comment['score']} points):\n"
            )
            md_content += f"{indent}> {comment['body'].replace(chr(10), chr(10) + indent + '> ')}\n\n"

    return md_content


# --- Scraper Plugin Class ---


class RedditScraper(ScraperBase):
    """Scrapes top posts from a list of subreddits."""

    def __init__(self, verbose: bool = True):
        super().__init__(verbose)
        self.name = "Reddit"
        self.client = get_sync_client()

    def run(self, config: RedditConfig, output_dir: Path):
        """Processes subreddits based on the provided configuration.

        Args:
            config: The scraper-specific Pydantic configuration model.
            output_dir: The base directory Path object for raw output.
        """
        print_section("💬 Scraping Reddit", self.verbose)

        subreddits = config.subreddits
        time_filter = config.time_filter

        for sub_config in subreddits:
            subreddit = sub_config.name
            min_upvotes = sub_config.min_upvotes
            tags = sub_config.tags

            if not subreddit:
                continue

            print_info(
                f"Fetching r/{subreddit} (min {min_upvotes} upvotes)", self.verbose
            )

            try:
                posts = _fetch_subreddit(self.client, subreddit, time_filter, limit=50)

                for post in posts:
                    post_id = post.get("id")
                    if not post_id or post.get("score", 0) < min_upvotes:
                        continue

                    if database.item_exists("reddit", post_id):
                        print_info(
                            f"Skipping (already processed): {post.get('title', 'Untitled')[:60]}",
                            self.verbose,
                        )
                        continue

                    print_info(
                        f"Processing post: {post.get('title', 'Untitled')[:60]}",
                        self.verbose,
                    )

                    comments = _fetch_comments(
                        self.client, post_id, subreddit, limit=50
                    )
                    comments.sort(key=lambda c: c["score"], reverse=True)

                    content = _format_post(post, comments, tags)
                    filename = utils.generate_filename(
                        "reddit", post.get("title", ""), post_id
                    )
                    filepath = output_dir / self.name.lower() / filename

                    utils.save_document(filepath, content, self.verbose)
                    database.add_item(
                        "reddit",
                        post_id,
                        title=post.get("title"),
                        url=f"https://www.reddit.com{post.get('permalink', '')}",
                    )
                    time.sleep(1)  # Rate limit to be polite

            except Exception as e:
                print_error(
                    f"Error processing subreddit r/{subreddit}: {e}", self.verbose
                )
                continue
