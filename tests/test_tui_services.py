#!/usr/bin/env python3
"""Unit tests for TUI service layer (ConfigService and DataService)."""

import sqlite3
from pathlib import Path

import pytest
import yaml

# ─── ConfigService Tests ───────────────────────────────────────────────────


@pytest.mark.unit
def test_config_service_loads_valid_yaml(tmp_path):
    """ConfigService loads a valid YAML config file."""
    config_data = {
        "days_back": 7,
        "scrapers": {
            "hackernews": {"enabled": True, "min_points": 50, "search_topics": ["AI"]},
            "rss": {"enabled": False, "feeds": []},
            "reddit": {"enabled": True, "subreddits": []},
            "arxiv": {"enabled": True, "search_queries": ["machine learning"]},
        },
        "output": {"base_dir": "research_digest"},
        "processing": {},
        "topics": {},
        "formats": {},
        "report": {},
    }
    config_file = tmp_path / "test_config.yaml"
    config_file.write_text(yaml.dump(config_data))

    from rdt.tui.services.config_service import ConfigService

    service = ConfigService(config_file)
    config = service.get_config()
    assert config is not None
    assert config.days_back == 7


@pytest.mark.unit
def test_config_service_missing_file_returns_default(tmp_path):
    """ConfigService returns default config when file is missing."""
    from rdt.tui.services.config_service import ConfigService

    service = ConfigService(tmp_path / "nonexistent.yaml")
    config = service.get_config()
    assert config is not None
    assert config.days_back == 7  # default value


@pytest.mark.unit
def test_config_service_get_scraper_configs(tmp_path):
    """get_scraper_configs returns list with name, enabled, config_summary."""
    config_data = {
        "scrapers": {
            "hackernews": {
                "enabled": True,
                "min_points": 50,
                "min_comments": 20,
                "search_topics": ["engineering culture", "platform engineering"],
            },
            "rss": {"enabled": False, "feeds": [], "days_back": 7},
            "reddit": {
                "enabled": True,
                "subreddits": [
                    {"name": "ExperiencedDevs", "min_upvotes": 100, "tags": []}
                ],
            },
            "arxiv": {
                "enabled": True,
                "search_queries": ["machine learning"],
                "days_back": 30,
            },
        },
        "output": {"base_dir": "research_digest"},
        "processing": {},
        "topics": {},
        "formats": {},
        "report": {},
    }
    config_file = tmp_path / "config.yaml"
    config_file.write_text(yaml.dump(config_data))

    from rdt.tui.services.config_service import ConfigService

    service = ConfigService(config_file)
    configs = service.get_scraper_configs()

    assert isinstance(configs, list)
    assert len(configs) == 4

    names = [c["name"] for c in configs]
    assert "HackerNews" in names
    assert "RSS" in names
    assert "Reddit" in names
    assert "ArXiv" in names

    hn = next(c for c in configs if c["name"] == "HackerNews")
    assert hn["enabled"] is True
    assert "config_summary" in hn
    assert isinstance(hn["config_summary"], str)

    rss = next(c for c in configs if c["name"] == "RSS")
    assert rss["enabled"] is False


@pytest.mark.unit
def test_config_service_source_name_mapping(tmp_path):
    """ConfigService provides correct DB source name mapping."""
    config_file = tmp_path / "config.yaml"
    config_file.write_text(
        yaml.dump(
            {
                "scrapers": {},
                "output": {},
                "processing": {},
                "topics": {},
                "formats": {},
                "report": {},
            }
        )
    )

    from rdt.tui.services.config_service import ConfigService

    service = ConfigService(config_file)
    mapping = service.get_source_name_mapping()

    assert mapping["hackernews"] == "hn"
    assert mapping["rss"] == "rss"
    assert mapping["reddit"] == "reddit"
    assert mapping["arxiv"] == "arxiv"


@pytest.mark.unit
def test_config_service_scraper_config_summary_includes_key_settings(tmp_path):
    """Config summary string includes meaningful settings info."""
    config_data = {
        "scrapers": {
            "hackernews": {
                "enabled": True,
                "min_points": 50,
                "search_topics": ["AI", "DevOps"],
            },
            "rss": {"enabled": False, "feeds": [], "days_back": 7},
            "reddit": {"enabled": False, "subreddits": []},
            "arxiv": {"enabled": False, "search_queries": [], "days_back": 30},
        },
        "output": {},
        "processing": {},
        "topics": {},
        "formats": {},
        "report": {},
    }
    config_file = tmp_path / "config.yaml"
    config_file.write_text(yaml.dump(config_data))

    from rdt.tui.services.config_service import ConfigService

    service = ConfigService(config_file)
    configs = service.get_scraper_configs()
    hn = next(c for c in configs if c["name"] == "HackerNews")

    # Config summary should mention something meaningful about the scraper
    assert len(hn["config_summary"]) > 0


# ─── DataService Tests ──────────────────────────────────────────────────────


def _create_test_db(db_path: Path, rows: list[tuple]) -> None:
    """Helper: create a test database with processed_items rows."""
    conn = sqlite3.connect(str(db_path))
    try:
        conn.execute(
            """
            CREATE TABLE processed_items (
                source TEXT NOT NULL,
                unique_id TEXT NOT NULL,
                processed_at TEXT DEFAULT CURRENT_TIMESTAMP,
                title TEXT,
                url TEXT,
                PRIMARY KEY (source, unique_id)
            )
        """
        )
        conn.executemany(
            "INSERT INTO processed_items (source, unique_id, processed_at) VALUES (?, ?, ?)",
            rows,
        )
        conn.commit()
    finally:
        conn.close()


@pytest.mark.unit
def test_data_service_get_item_counts_by_source(tmp_path):
    """get_item_counts_by_source returns dict mapping source to count."""
    db_path = tmp_path / "test.db"
    _create_test_db(
        db_path,
        [
            ("hn", "url1", "2026-01-01T10:00:00"),
            ("hn", "url2", "2026-01-02T10:00:00"),
            ("arxiv", "url3", "2026-01-01T10:00:00"),
            ("rss", "url4", "2026-01-01T10:00:00"),
        ],
    )

    from rdt.tui.services.data_service import DataService

    service = DataService(db_path)
    counts = service.get_item_counts_by_source()

    assert isinstance(counts, dict)
    assert counts["hn"] == 2
    assert counts["arxiv"] == 1
    assert counts["rss"] == 1


@pytest.mark.unit
def test_data_service_get_item_counts_empty_db(tmp_path):
    """get_item_counts_by_source returns empty dict for empty database."""
    db_path = tmp_path / "test.db"
    _create_test_db(db_path, [])

    from rdt.tui.services.data_service import DataService

    service = DataService(db_path)
    counts = service.get_item_counts_by_source()
    assert isinstance(counts, dict)
    assert len(counts) == 0


@pytest.mark.unit
def test_data_service_missing_db_returns_empty(tmp_path):
    """DataService returns empty results when database file is missing."""
    from rdt.tui.services.data_service import DataService

    service = DataService(tmp_path / "nonexistent.db")
    assert service.get_item_counts_by_source() == {}
    assert service.get_items_timeline() == []
    assert service.get_daily_counts() == []
    assert service.get_summary_stats()["total_items"] == 0
    assert service.get_source_distribution() == []


@pytest.mark.unit
def test_data_service_get_items_timeline_returns_list(tmp_path):
    """get_items_timeline returns list of dicts with source, unique_id, processed_at."""
    db_path = tmp_path / "test.db"
    _create_test_db(
        db_path,
        [
            ("hn", "https://hn.com/1", "2026-01-03T10:00:00"),
            ("rss", "https://rss.com/1", "2026-01-02T10:00:00"),
            ("arxiv", "https://arxiv.org/1", "2026-01-01T10:00:00"),
        ],
    )

    from rdt.tui.services.data_service import DataService

    service = DataService(db_path)
    timeline = service.get_items_timeline(limit=10)

    assert isinstance(timeline, list)
    assert len(timeline) == 3
    # Most recent first
    assert timeline[0]["source"] == "hn"
    # Each item has required fields including title and url
    for item in timeline:
        assert "source" in item
        assert "unique_id" in item
        assert "processed_at" in item
        assert "title" in item
        assert "url" in item


@pytest.mark.unit
def test_data_service_get_items_timeline_rejects_invalid_source(tmp_path):
    """get_items_timeline returns [] for unrecognized source_filter (SQL injection guard)."""
    db_path = tmp_path / "test.db"
    _create_test_db(db_path, [("hn", "url1", "2026-01-01T10:00:00")])

    from rdt.tui.services.data_service import DataService

    service = DataService(db_path)
    result = service.get_items_timeline(
        source_filter="hn'; DROP TABLE processed_items;--"
    )
    assert result == []


@pytest.mark.unit
def test_data_service_get_items_timeline_source_filter(tmp_path):
    """get_items_timeline filters by source when source_filter is given."""
    db_path = tmp_path / "test.db"
    _create_test_db(
        db_path,
        [
            ("hn", "https://hn.com/1", "2026-01-03T10:00:00"),
            ("rss", "https://rss.com/1", "2026-01-02T10:00:00"),
            ("arxiv", "https://arxiv.org/1", "2026-01-01T10:00:00"),
        ],
    )

    from rdt.tui.services.data_service import DataService

    service = DataService(db_path)
    hn_items = service.get_items_timeline(source_filter="hn")
    assert len(hn_items) == 1
    assert hn_items[0]["source"] == "hn"


@pytest.mark.unit
def test_data_service_get_daily_counts(tmp_path):
    """get_daily_counts returns list of dicts with date and count."""
    db_path = tmp_path / "test.db"
    _create_test_db(
        db_path,
        [
            ("hn", "url1", "2026-01-10T10:00:00"),
            ("hn", "url2", "2026-01-10T11:00:00"),
            ("rss", "url3", "2026-01-09T10:00:00"),
        ],
    )

    from rdt.tui.services.data_service import DataService

    service = DataService(db_path)
    daily = service.get_daily_counts(days=30)

    assert isinstance(daily, list)
    for row in daily:
        assert "date" in row
        assert "count" in row
        assert isinstance(row["count"], int)


@pytest.mark.unit
def test_data_service_get_summary_stats(tmp_path):
    """get_summary_stats returns dict with total_items, source_count, etc."""
    db_path = tmp_path / "test.db"
    _create_test_db(
        db_path,
        [
            ("hn", "url1", "2026-01-01T10:00:00"),
            ("hn", "url2", "2026-01-02T10:00:00"),
            ("arxiv", "url3", "2026-01-01T10:00:00"),
        ],
    )

    from rdt.tui.services.data_service import DataService

    service = DataService(db_path)
    stats = service.get_summary_stats()

    assert stats["total_items"] == 3
    assert stats["source_count"] == 2
    assert "date_range" in stats
    assert "avg_per_day" in stats


@pytest.mark.unit
def test_data_service_get_summary_stats_with_days_filter(tmp_path):
    """get_summary_stats(days=N) filters to last N days."""
    db_path = tmp_path / "test.db"
    # Use dates far in the past — only 'old' items exist
    _create_test_db(
        db_path,
        [
            ("hn", "url1", "2020-01-01T10:00:00"),
            ("hn", "url2", "2020-01-02T10:00:00"),
        ],
    )

    from rdt.tui.services.data_service import DataService

    service = DataService(db_path)
    # Filter to last 7 days — none of those items should be included
    stats = service.get_summary_stats(days=7)
    assert stats["total_items"] == 0


@pytest.mark.unit
def test_data_service_get_source_distribution(tmp_path):
    """get_source_distribution returns list with source, count, percentage."""
    db_path = tmp_path / "test.db"
    _create_test_db(
        db_path,
        [
            ("hn", "url1", "2026-01-01T10:00:00"),
            ("hn", "url2", "2026-01-01T10:00:00"),
            ("arxiv", "url3", "2026-01-01T10:00:00"),
        ],
    )

    from rdt.tui.services.data_service import DataService

    service = DataService(db_path)
    distribution = service.get_source_distribution()

    assert isinstance(distribution, list)
    assert len(distribution) == 2
    for row in distribution:
        assert "source" in row
        assert "count" in row
        assert "percentage" in row

    hn = next(r for r in distribution if r["source"] == "hn")
    assert hn["count"] == 2
    assert abs(hn["percentage"] - 66.67) < 1.0  # 2/3 ≈ 66.67%


@pytest.mark.unit
def test_data_service_get_source_distribution_with_days_filter(tmp_path):
    """get_source_distribution(days=N) filters to last N days."""
    db_path = tmp_path / "test.db"
    _create_test_db(
        db_path,
        [
            ("hn", "url1", "2020-01-01T10:00:00"),
        ],
    )

    from rdt.tui.services.data_service import DataService

    service = DataService(db_path)
    distribution = service.get_source_distribution(days=7)
    assert distribution == []


@pytest.mark.unit
def test_data_service_get_last_run_per_source(tmp_path):
    """get_last_run_per_source returns dict with most recent processed_at per source."""
    db_path = tmp_path / "test.db"
    _create_test_db(
        db_path,
        [
            ("hn", "url1", "2026-01-01T10:00:00"),
            ("hn", "url2", "2026-01-02T11:00:00"),
            ("arxiv", "url3", "2026-01-03T12:00:00"),
        ],
    )

    from rdt.tui.services.data_service import DataService

    service = DataService(db_path)
    last_runs = service.get_last_run_per_source()

    assert isinstance(last_runs, dict)
    assert last_runs["hn"] == "2026-01-02T11:00:00"
    assert last_runs["arxiv"] == "2026-01-03T12:00:00"


@pytest.mark.unit
def test_data_service_get_last_run_per_source_missing_db(tmp_path):
    """get_last_run_per_source returns empty dict when database is missing."""
    from rdt.tui.services.data_service import DataService

    service = DataService(tmp_path / "nonexistent.db")
    assert service.get_last_run_per_source() == {}


# ─── ConfigService Write Tests ────────────────────────────────────────────────


def _yaml_with_comments(tmp_path: Path) -> Path:
    """Write a YAML file with a comment for round-trip testing."""
    text = "# my important comment\ndays_back: 7\nscrapers: {}\n"
    p = tmp_path / "config_comments.yaml"
    p.write_text(text)
    return p


@pytest.mark.unit
def test_config_service_save_preserves_yaml_comments(tmp_path):
    """save() preserves YAML comments when round-tripping via ruamel."""
    pytest.importorskip("ruamel.yaml")
    config_file = _yaml_with_comments(tmp_path)

    from rdt.tui.services.config_service import ConfigService

    svc = ConfigService(config_file)
    # Trigger a write
    svc.set_scraper_field("hackernews", "enabled", True)

    content = config_file.read_text()
    assert "# my important comment" in content


@pytest.mark.unit
def test_set_scraper_enabled_writes_and_reloads(tmp_path):
    """set_scraper_enabled persists the change and reloads the Pydantic cache."""
    pytest.importorskip("ruamel.yaml")
    config_data = {
        "scrapers": {
            "hackernews": {"enabled": False, "min_points": 50, "search_topics": []},
            "rss": {"enabled": False, "feeds": []},
            "reddit": {"enabled": False, "subreddits": []},
            "arxiv": {"enabled": False, "search_queries": []},
        },
        "output": {},
        "processing": {},
        "topics": {},
        "formats": {},
        "report": {},
    }
    config_file = tmp_path / "config.yaml"
    config_file.write_text(yaml.dump(config_data))

    from rdt.tui.services.config_service import ConfigService

    svc = ConfigService(config_file)
    assert svc.get_scraper_config("hackernews").enabled is False

    svc.set_scraper_enabled("hackernews", True)
    assert svc.get_scraper_config("hackernews").enabled is True


@pytest.mark.unit
def test_add_rss_feed_appends_to_yaml(tmp_path):
    """add_rss_feed appends a new feed entry and saves to YAML."""
    pytest.importorskip("ruamel.yaml")
    config_data = {
        "scrapers": {"rss": {"enabled": True, "feeds": []}},
        "output": {},
        "processing": {},
        "topics": {},
        "formats": {},
        "report": {},
    }
    config_file = tmp_path / "config.yaml"
    config_file.write_text(yaml.dump(config_data))

    from rdt.tui.services.config_service import ConfigService

    svc = ConfigService(config_file)
    svc.add_rss_feed(
        url="https://example.com/feed.xml", name="Test Feed", tags=["tech"]
    )

    rss_cfg = svc.get_scraper_config("rss")
    assert rss_cfg is not None
    feeds = rss_cfg.feeds
    assert len(feeds) == 1
    assert str(feeds[0].url) == "https://example.com/feed.xml"
    assert feeds[0].name == "Test Feed"


@pytest.mark.unit
def test_remove_rss_feed_by_index(tmp_path):
    """remove_rss_feed removes the feed at the given index."""
    pytest.importorskip("ruamel.yaml")
    config_data = {
        "scrapers": {
            "rss": {
                "enabled": True,
                "feeds": [
                    {"url": "https://feed1.example.com/"},
                    {"url": "https://feed2.example.com/"},
                ],
            }
        },
        "output": {},
        "processing": {},
        "topics": {},
        "formats": {},
        "report": {},
    }
    config_file = tmp_path / "config.yaml"
    config_file.write_text(yaml.dump(config_data))

    from rdt.tui.services.config_service import ConfigService

    svc = ConfigService(config_file)
    svc.remove_rss_feed(0)

    rss_cfg = svc.get_scraper_config("rss")
    feeds = rss_cfg.feeds
    assert len(feeds) == 1
    assert "feed2" in str(feeds[0].url)


@pytest.mark.unit
def test_reload_clears_both_raw_and_pydantic_caches(tmp_path):
    """reload() clears _config (Pydantic) and _raw (ruamel) so next access re-reads."""
    pytest.importorskip("ruamel.yaml")
    config_file = tmp_path / "config.yaml"
    config_file.write_text(yaml.dump({"days_back": 7, "scrapers": {}}))

    from rdt.tui.services.config_service import ConfigService

    svc = ConfigService(config_file)
    _ = svc.config  # populate _config
    _ = svc._get_raw()  # populate _raw

    assert svc._config is not None
    assert svc._raw is not None

    svc.reload()

    assert svc._config is None
    assert svc._raw is None
