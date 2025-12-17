#!/usr/bin/env python3
"""
ArXiv Scraper Plugin for the Research Digest Toolkit.
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta, timezone

import database
import utils
from .base import ScraperBase

try:
    import arxiv
    ARXIV_AVAILABLE = True
except ImportError:
    ARXIV_AVAILABLE = False

# --- Helper Functions ---

def _format_paper(paper: arxiv.Result) -> str:
    """Formats a single paper into a markdown string."""
    title = paper.title.replace('"', '“')
    authors = ', '.join(author.name for author in paper.authors)
    
    md_content = f"""---
type: arxiv
title: "{title}"
authors: [{authors}]
published: {paper.published.strftime('%Y-%m-%d')}
updated: {paper.updated.strftime('%Y-%m-%d')}
url: {paper.entry_id}
pdf_url: {paper.pdf_url}
tags: [arxiv, paper, {', '.join(paper.categories)}]
---

# {title}

**Authors:** {authors}
**Published:** {paper.published.strftime('%Y-%m-%d')}
**Primary Category:** {paper.primary_category}

**Link:** <{paper.entry_id}>
**PDF:** <{paper.pdf_url}>

---

## Abstract

{paper.summary.strip()}
"""
    return md_content

# --- Scraper Plugin Class ---

class ArxivScraper(ScraperBase):
    """
    Scrapes ArXiv for recent papers matching configured search queries.
    """
    def __init__(self, verbose: bool = True):
        super().__init__(verbose)
        self.name = "Arxiv"

    def run(self, config: dict, output_dir: Path):
        """
        Processes ArXiv search queries based on the provided configuration.

        Args:
            config: The scraper-specific configuration dictionary.
            output_dir: The base directory Path object for raw output.
        """
        if not ARXIV_AVAILABLE:
            if self.verbose:
                print("  - Skipping ArXiv scraper: 'arxiv' library not installed. Run 'pip install arxiv'.")
            return

        if self.verbose:
            print("🔬 Scraping ArXiv...")

        queries = config.get('search_queries', [])
        days_back = config.get('days_back', 30)
        max_results_per_query = config.get('max_results', 25)
        
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_back)

        for query in queries:
            if self.verbose:
                print(f"  -> Searching for: '{query}'")
            
            try:
                search = arxiv.Search(
                    query=query,
                    max_results=max_results_per_query,
                    sort_by=arxiv.SortCriterion.SubmittedDate
                )
                
                results = list(search.results())

                for paper in results:
                    # The API returns timezone-aware datetime objects
                    paper_date = paper.published

                    if paper_date < cutoff_date:
                        # Since results are sorted by date, we can stop once we hit old papers
                        if self.verbose:
                            print("    - Reached end of time window for this query.")
                        break

                    unique_id = paper.entry_id
                    if database.item_exists('arxiv', unique_id):
                        if self.verbose:
                            print(f"    - Skipping (already processed): {paper.title[:70]}")
                        continue

                    if self.verbose:
                        print(f"    -> Processing paper: {paper.title[:70]}")

                    content = _format_paper(paper)
                    filename = utils.generate_filename('arxiv', paper.title, unique_id)
                    filepath = output_dir / self.name.lower() / filename
                    
                    utils.save_document(filepath, content, self.verbose)
                    database.add_item('arxiv', unique_id)

            except Exception as e:
                if self.verbose:
                    print(f"    ✗ Error processing ArXiv query '{query}': {e}", file=sys.stderr)
                continue
