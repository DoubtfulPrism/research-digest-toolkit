#!/usr/bin/env python3
"""Tests for ConfigService."""

import pytest
import yaml

from research_digest_tui.services.config_service import ConfigService


@pytest.mark.unit
def test_config_service_loads_real_config(tmp_path):
    """ConfigService loads a real YAML config and returns a typed ResearchDigestConfig."""
    config_data = {
        "days_back": 14,
        "output": {"base_dir": "test_output", "use_date_folders": True},
        "scrapers": {
            "hackernews": {
                "enabled": True,
                "min_points": 100,
                "min_comments": 5,
                "search_topics": ["ai", "ml"],
            },
            "rss": {"enabled": False, "feeds": []},
            "reddit": {"enabled": False, "subreddits": []},
            "arxiv": {
                "enabled": True,
                "search_queries": ["machine learning"],
                "max_results": 10,
            },
        },
        "topics": {"tech": ["python", "rust"]},
        "processing": {
            "convert_documents": True,
            "auto_tag": True,
            "format_for_obsidian": True,
            "split_large_files": True,
        },
    }
    config_file = tmp_path / "research_config.yaml"
    config_file.write_text(yaml.dump(config_data))

    service = ConfigService(config_path=config_file)

    assert service.config.days_back == 14
    assert service.config.scrapers.hackernews.min_points == 100


@pytest.mark.unit
def test_config_service_returns_defaults_when_file_missing(tmp_path):
    """ConfigService returns ResearchDigestConfig defaults when config file does not exist."""
    service = ConfigService(config_path=tmp_path / "nonexistent.yaml")

    assert service.config is not None
    assert service.config.days_back == 7  # Pydantic default


@pytest.mark.unit
def test_config_service_sets_config_path_to_actual_path(tmp_path):
    """ConfigService sets config_path on the model to reflect the actual loaded file path."""
    config_file = tmp_path / "my_config.yaml"
    config_file.write_text(
        yaml.dump(
            {
                "days_back": 7,
                "scrapers": {
                    "hackernews": {"enabled": False},
                    "rss": {"enabled": False},
                    "reddit": {"enabled": False},
                    "arxiv": {"enabled": False},
                },
            }
        )
    )

    service = ConfigService(config_path=config_file)

    assert service.config.config_path == str(config_file)


@pytest.mark.unit
def test_get_scraper_names_returns_enabled_scrapers(tmp_path):
    """get_scraper_names() returns only enabled scraper names."""
    config_data = {
        "scrapers": {
            "hackernews": {
                "enabled": True,
                "min_points": 50,
                "min_comments": 20,
                "search_topics": [],
            },
            "rss": {"enabled": False, "feeds": []},
            "reddit": {"enabled": True, "subreddits": []},
            "arxiv": {"enabled": False, "search_queries": []},
        }
    }
    config_file = tmp_path / "config.yaml"
    config_file.write_text(yaml.dump(config_data))

    service = ConfigService(config_path=config_file)
    names = service.get_scraper_names()

    assert "hackernews" in names
    assert "reddit" in names
    assert "rss" not in names
    assert "arxiv" not in names


@pytest.mark.unit
def test_get_scraper_config_returns_typed_config(tmp_path):
    """get_scraper_config('hackernews') returns HNConfig with correct values."""
    config_data = {
        "scrapers": {
            "hackernews": {
                "enabled": True,
                "min_points": 75,
                "min_comments": 10,
                "search_topics": ["devops"],
            },
            "rss": {"enabled": False, "feeds": []},
            "reddit": {"enabled": False, "subreddits": []},
            "arxiv": {"enabled": False, "search_queries": []},
        }
    }
    config_file = tmp_path / "config.yaml"
    config_file.write_text(yaml.dump(config_data))

    service = ConfigService(config_path=config_file)
    hn_config = service.get_scraper_config("hackernews")

    assert hn_config.min_points == 75
    assert hn_config.min_comments == 10
    assert "devops" in hn_config.search_topics


@pytest.mark.unit
def test_get_scraper_config_returns_none_for_unknown_scraper(tmp_path):
    """get_scraper_config() returns None for unknown scraper names."""
    config_file = tmp_path / "config.yaml"
    config_file.write_text(
        yaml.dump(
            {
                "scrapers": {
                    "hackernews": {"enabled": False},
                    "rss": {"enabled": False},
                    "reddit": {"enabled": False},
                    "arxiv": {"enabled": False},
                }
            }
        )
    )

    service = ConfigService(config_path=config_file)

    assert service.get_scraper_config("unknown_scraper") is None


@pytest.mark.unit
def test_reload_refreshes_config(tmp_path):
    """reload() re-reads the config file so changes are picked up."""
    config_file = tmp_path / "config.yaml"
    config_file.write_text(
        yaml.dump(
            {
                "days_back": 7,
                "scrapers": {
                    "hackernews": {"enabled": False},
                    "rss": {"enabled": False},
                    "reddit": {"enabled": False},
                    "arxiv": {"enabled": False},
                },
            }
        )
    )

    service = ConfigService(config_path=config_file)
    assert service.config.days_back == 7

    # Update the file
    config_file.write_text(
        yaml.dump(
            {
                "days_back": 30,
                "scrapers": {
                    "hackernews": {"enabled": False},
                    "rss": {"enabled": False},
                    "reddit": {"enabled": False},
                    "arxiv": {"enabled": False},
                },
            }
        )
    )
    service.reload()

    assert service.config.days_back == 30
