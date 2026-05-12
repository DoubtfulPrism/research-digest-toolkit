#!/usr/bin/env python3
"""ConfigService — loads research_config.yaml and provides typed access."""

from pathlib import Path
from typing import Any

import yaml

from research_digest_tui.config_models import ResearchDigestConfig

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


def _build_config_summary(key: str, scraper_config: Any) -> str:
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
    """Loads research_config.yaml and provides typed access to configuration.

    Two parse paths:
    - PyYAML safe_load → Pydantic model (read path, self._config)
    - ruamel.yaml round-trip → CommentedMap (write path, self._raw)

    Both caches are invalidated by reload(). save() writes _raw to disk then
    clears _config so the next .config access re-reads from disk via PyYAML.
    """

    _config: ResearchDigestConfig | None
    _raw: Any  # ruamel CommentedMap | None

    def __init__(self, config_path: Path = Path("research_config.yaml")) -> None:
        self._config_path = Path(config_path)
        self._config = None
        self._raw = None

    @property
    def config(self) -> ResearchDigestConfig:
        """Return the validated config, loading it if needed."""
        if self._config is None:
            self._config = self._load()
        return self._config

    def get_config(self) -> ResearchDigestConfig:
        """Return the validated config (alias for .config property)."""
        return self.config

    def _load(self) -> ResearchDigestConfig:
        """Load and validate the YAML config file via PyYAML + Pydantic."""
        if not self._config_path.exists():
            cfg = ResearchDigestConfig()
            cfg.config_path = str(self._config_path)
            return cfg
        try:
            with open(self._config_path, encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
            cfg = ResearchDigestConfig(**data)
            cfg.config_path = str(self._config_path)
            return cfg
        except Exception:
            cfg = ResearchDigestConfig()
            cfg.config_path = str(self._config_path)
            return cfg

    def _get_raw(self) -> Any:
        """Return the ruamel round-trip document, loading if needed."""
        if self._raw is None:
            self._raw = self._load_raw()
        return self._raw

    def _load_raw(self) -> Any:
        """Load the YAML file as a ruamel CommentedMap (preserves comments)."""
        from ruamel.yaml import YAML, CommentedMap  # type: ignore[import-untyped]

        yaml_rt = YAML(typ="rt")
        yaml_rt.preserve_quotes = True
        if not self._config_path.exists():
            root: Any = CommentedMap()
            root["scrapers"] = CommentedMap()
            return root
        with open(self._config_path, encoding="utf-8") as f:
            result = yaml_rt.load(f)
        if result is None:
            return CommentedMap()
        return result

    def reload(self) -> None:
        """Reload the config from disk (invalidates both Pydantic and raw caches)."""
        self._config = None
        self._raw = None

    def save(self) -> None:
        """Write the round-trip document to disk, then resync the Pydantic cache."""
        from ruamel.yaml import YAML  # type: ignore[import-untyped]

        yaml_rt = YAML(typ="rt")
        yaml_rt.preserve_quotes = True
        raw = self._get_raw()
        with open(self._config_path, "w", encoding="utf-8") as f:
            yaml_rt.dump(raw, f)
        self.reload()

    def set_scraper_enabled(self, key: str, enabled: bool) -> None:
        """Enable or disable a scraper by config key."""
        from ruamel.yaml import CommentedMap  # type: ignore[import-untyped]

        raw = self._get_raw()
        if "scrapers" not in raw:
            raw["scrapers"] = CommentedMap()
        if key not in raw["scrapers"]:
            raw["scrapers"][key] = CommentedMap()
        raw["scrapers"][key]["enabled"] = enabled
        self.save()

    def set_scraper_field(self, key: str, field: str, value: Any) -> None:
        """Set a single field on a scraper's config and save."""
        from ruamel.yaml import CommentedMap  # type: ignore[import-untyped]

        raw = self._get_raw()
        if "scrapers" not in raw:
            raw["scrapers"] = CommentedMap()
        if key not in raw["scrapers"]:
            raw["scrapers"][key] = CommentedMap()
        raw["scrapers"][key][field] = value
        self.save()

    def add_rss_feed(
        self,
        url: str,
        name: str | None = None,
        tags: list[str] | None = None,
        auth_type: str | None = None,
        username: str | None = None,
        password_key: str | None = None,
    ) -> None:
        """Append a new RSS feed entry to the config and save."""
        from ruamel.yaml import CommentedMap  # type: ignore[import-untyped]

        raw = self._get_raw()
        if "scrapers" not in raw:
            raw["scrapers"] = CommentedMap()
        if "rss" not in raw["scrapers"]:
            raw["scrapers"]["rss"] = CommentedMap({"enabled": True})
        if "feeds" not in raw["scrapers"]["rss"]:
            raw["scrapers"]["rss"]["feeds"] = []

        feed: Any = CommentedMap({"url": url})
        if name is not None:
            feed["name"] = name
        if tags:
            feed["tags"] = list(tags)
        if auth_type:
            feed["auth_type"] = auth_type
        if username:
            feed["username"] = username
        if password_key:
            feed["password_key"] = password_key

        raw["scrapers"]["rss"]["feeds"].append(feed)
        self.save()

    def remove_rss_feed(self, index: int) -> None:
        """Remove an RSS feed by list index and save."""
        raw = self._get_raw()
        try:
            feeds = raw["scrapers"]["rss"]["feeds"]
            del feeds[index]
            self.save()
        except (KeyError, IndexError):
            pass

    def set_schedule(self, schedule_str: str | None) -> None:
        """Set the schedule string in the YAML config."""
        from ruamel.yaml import CommentedMap  # type: ignore[import-untyped]

        raw = self._get_raw()
        if "schedule" not in raw:
            raw["schedule"] = CommentedMap()
        raw["schedule"]["schedule_string"] = schedule_str
        self.save()

    def set_schedule_enabled(self, enabled: bool) -> None:
        """Enable or disable the schedule."""
        from ruamel.yaml import CommentedMap  # type: ignore[import-untyped]

        raw = self._get_raw()
        if "schedule" not in raw:
            raw["schedule"] = CommentedMap()
        raw["schedule"]["enabled"] = enabled
        self.save()

    def get_credential_command(self) -> str | None:
        """Return the credential command template, or None if not set."""
        return getattr(self.config, "credential_command", None)

    def set_credential_command(self, cmd: str | None) -> None:
        """Set or clear the credential command template."""
        raw = self._get_raw()
        if cmd:
            raw["credential_command"] = cmd
        else:
            raw.pop("credential_command", None)
        self.save()

    def get_scraper_names(self) -> list[str]:
        """Return names of all enabled scrapers."""
        result = []
        scrapers = self.config.scrapers
        for key in ("hackernews", "rss", "reddit", "arxiv"):
            scraper_cfg = getattr(scrapers, key, None)
            if scraper_cfg is not None and getattr(scraper_cfg, "enabled", False):
                result.append(key)
        return result

    def get_scraper_config(self, name: str) -> Any:
        """Return the typed config for a specific scraper, or None if unknown."""
        return getattr(self.config.scrapers, name, None)

    def get_scraper_configs(self) -> list[dict[str, Any]]:
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

    def get_output_base_dir(self) -> str:
        """Return the configured base directory for output."""
        output_cfg = getattr(self.config, "output", None)
        if output_cfg is not None:
            return getattr(output_cfg, "base_dir", "research_digest")
        return "research_digest"

    def set_output_base_dir(self, path: str) -> None:
        """Set the output base directory."""
        from ruamel.yaml import CommentedMap  # type: ignore[import-untyped]

        raw = self._get_raw()
        if "output" not in raw:
            raw["output"] = CommentedMap()
        raw["output"]["base_dir"] = path
        self.save()
