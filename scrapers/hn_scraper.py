#!/usr/bin/env python3
"""
HackerNews Scraper Plugin for the Research Digest Toolkit.
"""

import sys
import re
import time
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

import requests
import database
import utils
from .base import ScraperBase

# --- Constants and HNClient Class ---

HN_API_BASE = "https://hacker-news.firebaseio.com/v0"
HN_ALGOLIA_SEARCH = "https://hn.algolia.com/api/v1"
MAX_WORKERS = 10

class _HNClient:
    """Internal client for HackerNews APIs."""
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'Mozilla/5.0 Research Digest Scraper'})

    def get_item(self, item_id: int) -> dict:
        """Gets a single item by ID from the Firebase API."""
        try:
            url = f"{HN_API_BASE}/item/{item_id}.json"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            return None

    def search_stories(self, query: str, min_points: int) -> list:
        """Searches for stories using the Algolia API."""
        params = {
            'query': query,
            'tags': 'story',
            'hitsPerPage': 50, # Fetch more to ensure we get enough after filtering
            'numericFilters': f'points>={min_points}'
        }
        url = f"{HN_ALGOLIA_SEARCH}/search"
        response = self.session.get(url, params=params, timeout=15)
        response.raise_for_status()
        return [hit['objectID'] for hit in response.json().get('hits', [])]

# --- Helper Functions ---

def _fetch_comments_recursive(client: _HNClient, comment_ids: list, max_depth: int, current_depth: int) -> list:
    """Recursively fetches comments concurrently."""
    if current_depth >= max_depth or not comment_ids:
        return []
    
    comments = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        fetched_comments = list(executor.map(client.get_item, comment_ids))

    for comment in fetched_comments:
        if not comment or comment.get('deleted') or comment.get('dead'):
            continue
        
        if comment.get('kids'):
            comment['replies'] = _fetch_comments_recursive(client, comment['kids'], max_depth, current_depth + 1)
        else:
            comment['replies'] = []
        comments.append(comment)
    return comments

def _format_comments(comments: list, depth: int) -> str:
    """Formats a list of comments hierarchically."""
    output = ""
    indent = "  " * depth
    for comment in comments:
        by = comment.get('by', 'unknown')
        text = utils.clean_html(comment.get('text', ''))
        if not text:
            continue
        
        output += f"{indent}**{by}** ({comment.get('score', 0)} points):\n"
        output += f"{indent}> {text.replace(chr(10), chr(10) + indent + '> ')}\n\n"
        if comment.get('replies'):
            output += _format_comments(comment['replies'], depth + 1)
    return output

def _format_story(story: dict) -> str:
    """Formats a story and its comments into a markdown string."""
    title = story.get('title', 'Untitled')
    url = story.get('url', '')
    hn_url = f"https://news.ycombinator.com/item?id={story['id']}"
    
    md_content = f"""---
type: hackernews
title: \"{title.replace('"', '“')}\""
author: \"{story.get('by', 'unknown')}\""
score: {story.get('score', 0)}
comments: {story.get('descendants', 0)}
date: {datetime.fromtimestamp(story.get('time', 0)).strftime('%Y-%m-%d')}
url: {url}
hn_url: {hn_url}
tags: [hackernews, discussion]
---

# {title}

**Posted by:** {story.get('by', 'unknown')}
**Score:** {story.get('score', 0)} points
**Comments:** {story.get('descendants', 0)}
**HN Discussion:** <{hn_url}>
"""
    if url:
        md_content += f"**Article Link:** <{url}>\n"
    
    if story.get('text'):
        md_content += f"\n---\n\n{utils.clean_html(story.get('text'))}\n"
        
    if story.get('comments'):
        md_content += f"\n---\n\n## Discussion\n\n"
        md_content += _format_comments(story['comments'], 0)
        
    return md_content

# --- Scraper Plugin Class ---

class HNScraper(ScraperBase):
    """
    Scrapes Hacker News for discussions matching configured topics.
    """
    def __init__(self, verbose: bool = True):
        super().__init__(verbose)
        self.name = "HackerNews"
        self.client = _HNClient()

    def run(self, config: dict, output_dir: Path):
        if self.verbose:
            print("📰 Scraping Hacker News...")

        min_points = config.get('min_points', 50)
        min_comments = config.get('min_comments', 20)
        search_topics = config.get('search_topics', [])
        
        story_ids_to_process = set()

        for topic in search_topics:
            if self.verbose:
                print(f"  -> Searching for topic: '{topic}'")
            try:
                story_ids = self.client.search_stories(topic, min_points)
                story_ids_to_process.update(story_ids)
            except Exception as e:
                if self.verbose:
                    print(f"     ✗ Error searching for '{topic}': {e}", file=sys.stderr)
        
        if self.verbose:
            print(f"  Found {len(story_ids_to_process)} potential stories. Filtering...")

        for story_id in story_ids_to_process:
            try:
                if database.item_exists('hn', str(story_id)):
                    if self.verbose:
                        print(f"  - Skipping (already processed): Story {story_id}")
                    continue

                story = self.client.get_item(story_id)
                if not story or story.get('descendants', 0) < min_comments:
                    continue

                if self.verbose:
                    print(f"  -> Processing story: {story.get('title', '')[:70]}")

                if story.get('kids'):
                    story['comments'] = _fetch_comments_recursive(self.client, story['kids'], max_depth=3, current_depth=0)
                else:
                    story['comments'] = []
                
                content = _format_story(story)
                filename = utils.generate_filename('hn', story.get('title', ''), story_id)
                filepath = output_dir / self.name.lower() / filename
                
                utils.save_document(filepath, content, self.verbose)
                database.add_item('hn', str(story_id))
                time.sleep(1) # Rate limit to be polite

            except Exception as e:
                if self.verbose:
                    print(f"     ✗ Error processing story {story_id}: {e}", file=sys.stderr)
                continue
