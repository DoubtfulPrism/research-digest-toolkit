#!/usr/bin/env python3
"""Pydantic models for configuration validation."""

from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel, Field, HttpUrl, validator


class OutputConfig(BaseModel):
    """Configuration for output settings."""

    base_dir: str = "research_digest"
    use_date_folders: bool = True
    obsidian_vault: Optional[str] = None


class ProcessingConfig(BaseModel):
    """Configuration for processing options."""

    convert_documents: bool = True
    auto_tag: bool = True
    format_for_obsidian: bool = True
    split_large_files: bool = True
    max_file_size: int = 400000


class ReportConfig(BaseModel):
    """Configuration for the final report."""

    generate_summary: bool = True
    email_report: bool = False
    email_address: Optional[str] = None


class BaseScraperConfig(BaseModel):
    """Base configuration for all scrapers."""

    enabled: bool = False


class HNConfig(BaseScraperConfig):
    """Configuration for the HackerNews scraper."""

    min_points: int = 50
    min_comments: int = 20
    search_topics: List[str] = []


class RSSFeed(BaseModel):
    """Configuration for a single RSS feed."""

    url: HttpUrl
    name: Optional[str] = None
    tags: List[str] = []

    def model_post_init(self, __context):
        """Set name to URL if not provided."""
        if self.name is None:
            self.name = str(self.url)


class RSSConfig(BaseScraperConfig):
    """Configuration for the RSS scraper."""

    days_back: int = 7
    feeds: List[RSSFeed] = []


class RedditSubreddit(BaseModel):
    """Configuration for a single subreddit."""

    name: str
    min_upvotes: int = 50
    tags: List[str] = []


class RedditConfig(BaseScraperConfig):
    """Configuration for the Reddit scraper."""

    time_filter: str = "week"
    subreddits: List[RedditSubreddit] = []


class ArxivConfig(BaseScraperConfig):
    """Configuration for the ArXiv scraper."""

    search_queries: List[str] = []
    days_back: int = 30
    max_results: int = 25


class ScrapersConfig(BaseModel):
    """Container for all scraper configurations."""
    model_config = {"extra": "allow"}

    hackernews: HNConfig = Field(default_factory=HNConfig)
    rss: RSSConfig = Field(default_factory=RSSConfig)
    reddit: RedditConfig = Field(default_factory=RedditConfig)
    arxiv: ArxivConfig = Field(default_factory=ArxivConfig)


class ResearchDigestConfig(BaseModel):
    """Root configuration model for the application."""

    days_back: int = 7
    output: OutputConfig = Field(default_factory=OutputConfig)
    scrapers: ScrapersConfig = Field(default_factory=ScrapersConfig)
    topics: dict = {}
    processing: ProcessingConfig = Field(default_factory=ProcessingConfig)
    formats: dict = {}
    report: ReportConfig = Field(default_factory=ReportConfig)
    config_path: Optional[str] = "research_config.yaml"

    @validator("output")
    def validate_output(cls, v):
        """Ensure the output directory is valid."""
        if v.obsidian_vault:
            path = Path(v.obsidian_vault)
            if not path.exists() or not path.is_dir():
                raise ValueError(f"Obsidian vault path does not exist or is not a directory: {path}")
        return v
