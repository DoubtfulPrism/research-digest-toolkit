#!/usr/bin/env python3
"""ArXiv Scraper Plugin for the Research Digest Toolkit."""

from datetime import datetime, timedelta, timezone
from pathlib import Path

from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential

import database
import utils
from config_models import ArxivConfig
from rich_utils import print_error, print_info, print_section, print_warning

from .base import ScraperBase

try:
    import arxiv

    ARXIV_AVAILABLE = True
except ImportError:
    ARXIV_AVAILABLE = False

# --- Helper Functions ---


def _format_paper(paper: arxiv.Result) -> str:
    """Formats a single paper into a markdown string."""
    title = paper.title.replace('"', "“")
    authors = ", ".join(author.name for author in paper.authors)

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
    """Scrapes ArXiv for recent papers matching configured search queries."""

    def __init__(self, verbose: bool = True):
        super().__init__(verbose)
        self.name = "Arxiv"

    def run(self, config: ArxivConfig, output_dir: Path):
        """Processes ArXiv search queries based on the provided configuration.

        Args:
            config: The scraper-specific Pydantic configuration model.
            output_dir: The base directory Path object for raw output.
        """
        if not ARXIV_AVAILABLE:
            print_warning(
                "Skipping ArXiv scraper: 'arxiv' library not installed. Run 'pip install arxiv'.",
                self.verbose,
            )
            return

        print_section("🔬 Scraping ArXiv", self.verbose)

        queries = config.search_queries
        days_back = config.days_back
        max_results_per_query = config.max_results

        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_back)

        for query in queries:
            print_info(f"Searching for: '{query}'", self.verbose)

            try:

                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=1, max=10),
                    retry=retry_if_exception(
                        lambda e: isinstance(
                            e,
                            (
                                arxiv.arxiv.UnexpectedEmptyPageError,
                                arxiv.arxiv.HTTPError,
                            ),
                        )
                    ),
                    reraise=True,
                )
                def _search_arxiv():
                    search = arxiv.Search(
                        query=query,
                        max_results=max_results_per_query,
                        sort_by=arxiv.SortCriterion.SubmittedDate,
                    )
                    return list(search.results())

                results = _search_arxiv()

                for paper in results:
                    # The API returns timezone-aware datetime objects
                    paper_date = paper.published

                    if paper_date < cutoff_date:
                        # Since results are sorted by date, we can stop once we hit old papers
                        print_info(
                            "Reached end of time window for this query.", self.verbose
                        )
                        break

                    unique_id = paper.entry_id
                    if database.item_exists("arxiv", unique_id):
                        print_info(
                            f"Skipping (already processed): {paper.title[:70]}",
                            self.verbose,
                        )
                        continue

                    print_info(f"Processing paper: {paper.title[:70]}", self.verbose)

                    content = _format_paper(paper)
                    filename = utils.generate_filename("arxiv", paper.title, unique_id)
                    filepath = output_dir / self.name.lower() / filename

                    utils.save_document(filepath, content, self.verbose)
                    database.add_item(
                        "arxiv",
                        unique_id,
                        title=paper.title,
                        url=unique_id,
                    )

            except Exception as e:
                print_error(
                    f"Error processing ArXiv query '{query}': {e}", self.verbose
                )
                continue
