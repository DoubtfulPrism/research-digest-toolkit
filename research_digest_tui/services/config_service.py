#!/usr/bin/env python3
"""ConfigService — loads research_config.yaml and provides typed access."""

from pathlib import Path

import yaml

from config_models import ResearchDigestConfig

# Maps YAML config keys → database source names
SOURCE_NAME_MAPPING: dict[str, str] = {
    "hackernews": "hn",
    "rss": "rss",
    "reddit": "reddit",
    "arxiv": "arxiv",
}

# Display names for each scraper
DISPLAY_NAMES: dict[str, str] = {
    "hackernews": "HackerNews",
    "rss": "RSS",
    "reddit": "Reddit",
    "arxiv": "ArXiv",
}


def _build_config_summary(key: str, scraper_config) -> str:
    """Build a human-readable summary string for a scraper config."""
    if key == "hackernews":
        topics = getattr(scraper_config, "search_topics", [])
        count = len(topics)
        return f"Topics: {count} configured | Min Points: {getattr(scraper_config, 'min_points', 50)}"
    if key == "rss":
        feeds = getattr(scraper_config, "feeds", [])
        return f"Feeds: {len(feeds)} configured | Days Back: {getattr(scraper_config, 'days_back', 7)}"
    if key == "reddit":
        subs = getattr(scraper_config, "subreddits", [])
        names = ", ".join(getattr(s, "name", str(s)) for s in subs[:3])
        suffix = "..." if len(subs) > 3 else ""
        return f"Subreddits: {names}{suffix}" if names else "No subreddits configured"
    if key == "arxiv":
        queries = getattr(scraper_config, "search_queries", [])
        return f"Queries: {len(queries)} configured | Days Back: {getattr(scraper_config, 'days_back', 30)}"
    return "No config summary available"


class ConfigService:
    """Loads research_config.yaml and provides typed access to configuration."""

    def __init__(self, config_path: Path) -> None:
        self._config_path = config_path
        self._config: ResearchDigestConfig | None = None

    def get_config(self) -> ResearchDigestConfig:
        """Return the validated config, loading it if needed."""
        if self._config is None:
            self._config = self._load()
        return self._config

    def _load(self) -> ResearchDigestConfig:
        """Load and validate the YAML config file."""
        if not self._config_path.exists():
            return ResearchDigestConfig()
        try:
            with open(self._config_path, encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
            return ResearchDigestConfig(**data)
        except Exception:
            return ResearchDigestConfig()

    def get_scraper_configs(self) -> list[dict]:
        """Return list of scraper info dicts with name, enabled, config_summary."""
        config = self.get_config()
        scrapers = config.scrapers
        result = []
        for key in ("hackernews", "rss", "reddit", "arxiv"):
            scraper_cfg = getattr(scrapers, key, None)
            if scraper_cfg is None:
                continue
            result.append(
                {
                    "name": DISPLAY_NAMES[key],
                    "config_key": key,
                    "db_source": SOURCE_NAME_MAPPING[key],
                    "enabled": getattr(scraper_cfg, "enabled", False),
                    "config_summary": _build_config_summary(key, scraper_cfg),
                }
            )
        return result

    def get_source_name_mapping(self) -> dict[str, str]:
        """Return mapping from config key → database source name."""
        return dict(SOURCE_NAME_MAPPING)
