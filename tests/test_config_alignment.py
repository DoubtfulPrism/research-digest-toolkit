#!/usr/bin/env python3
"""Tests for configuration alignment and round-trip safety."""

import pytest
import yaml
from pathlib import Path
from rdt.tui.services.config_service import ConfigService

@pytest.fixture
def complex_config_file(tmp_path):
    """Create a complex config file with nested metadata and comments."""
    config_content = """# Global Settings
days_back: 7

scrapers:
  reddit:
    enabled: true
    time_filter: week
    subreddits:
      - name: MachineLearning
        min_upvotes: 100
        tags: [ml, ai]
      - name: Python
        min_upvotes: 50
        tags: [coding]

topics:
  software_leadership:
    - "engineering culture"
    - "team leadership"

processing:
  convert_documents: true
  auto_tag: true
"""
    config_file = tmp_path / "research_config.yaml"
    config_file.write_text(config_content)
    return config_file

@pytest.mark.unit
def test_reddit_metadata_preservation(complex_config_file):
    """Verify that updating subreddits preserves existing metadata (min_upvotes, tags)."""
    service = ConfigService(config_path=complex_config_file)
    
    # Simulate TUI update: user adds "NaturalLanguage" and keeps "MachineLearning" but removes "Python"
    new_sub_names = ["MachineLearning", "NaturalLanguage"]
    service.update_reddit_subreddits(new_sub_names)
    
    # Reload and check
    service.reload()
    subs = service.config.scrapers.reddit.subreddits
    
    assert len(subs) == 2
    
    # MachineLearning should have preserved its 100 upvotes and tags
    ml_sub = next(s for s in subs if s.name == "MachineLearning")
    assert ml_sub.min_upvotes == 100
    assert "ml" in ml_sub.tags
    
    # NaturalLanguage should have defaults
    nl_sub = next(s for s in subs if s.name == "NaturalLanguage")
    assert nl_sub.min_upvotes == 50
    assert nl_sub.tags == []

@pytest.mark.unit
def test_topic_keywords_round_trip(complex_config_file):
    """Verify that adding/removing topics works without data loss in other sections."""
    service = ConfigService(config_path=complex_config_file)
    
    service.set_topic("new_topic", ["keyword1", "keyword2"])
    service.reload()
    
    assert "software_leadership" in service.config.topics
    assert "new_topic" in service.config.topics
    assert service.config.topics["new_topic"] == ["keyword1", "keyword2"]
    
    # Verify processing section is still there
    assert service.config.processing.convert_documents is True

@pytest.mark.unit
def test_round_trip_preserves_comments(complex_config_file):
    """Verify that ruamel.yaml preserves top-level comments."""
    service = ConfigService(config_path=complex_config_file)
    service.set_scraper_enabled("hackernews", True)
    
    content = complex_config_file.read_text()
    assert "# Global Settings" in content
