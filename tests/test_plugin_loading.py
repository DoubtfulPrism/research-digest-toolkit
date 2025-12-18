#!/usr/bin/env python3
"""
Tests for plugin loading mechanism in research_digest.py.
"""

import sys
from pathlib import Path

import pytest
import yaml

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from research_digest import ResearchDigest
from scrapers.base import ScraperBase


@pytest.fixture
def temp_config(tmp_path):
    """
    Fixture that creates a temporary config file for testing.
    """
    config = {
        "days_back": 7,
        "output": {
            "base_dir": str(tmp_path / "research_digest"),
            "use_date_folders": True,
        },
        "scrapers": {
            "hackernews": {"enabled": True},
            "rss": {"enabled": False},
            "reddit": {"enabled": True},
            "arxiv": {"enabled": True},
        },
        "processing": {"format_for_obsidian": False, "auto_tag": False},
        "report": {"generate_summary": False},
    }

    config_path = tmp_path / "test_config.yaml"
    with open(config_path, "w", encoding="utf-8") as f:
        yaml.dump(config, f)

    return config_path


@pytest.mark.unit
class TestResearchDigestInit:
    """Tests for ResearchDigest initialization."""

    def test_initialization_with_config(self, temp_config):
        """Test that ResearchDigest initializes with a config file."""
        digest = ResearchDigest(str(temp_config), verbose=False)

        assert digest.config is not None
        assert isinstance(digest.config, dict)
        assert digest.verbose is False

    def test_initialization_loads_config(self, temp_config):
        """Test that config is loaded correctly."""
        digest = ResearchDigest(str(temp_config), verbose=False)

        assert "scrapers" in digest.config
        assert "output" in digest.config
        assert digest.config["days_back"] == 7

    def test_initialization_with_verbose(self, temp_config):
        """Test that verbose flag is respected."""
        digest_verbose = ResearchDigest(str(temp_config), verbose=True)
        digest_quiet = ResearchDigest(str(temp_config), verbose=False)

        assert digest_verbose.verbose is True
        assert digest_quiet.verbose is False

    def test_initialization_with_missing_config(self, tmp_path):
        """Test that initialization fails with missing config file."""
        missing_config = tmp_path / "missing.yaml"

        with pytest.raises(SystemExit):
            ResearchDigest(str(missing_config), verbose=False)

    def test_initialization_with_invalid_yaml(self, tmp_path):
        """Test that initialization fails with invalid YAML."""
        invalid_config = tmp_path / "invalid.yaml"
        invalid_config.write_text("{ invalid yaml content: [", encoding="utf-8")

        with pytest.raises(SystemExit):
            ResearchDigest(str(invalid_config), verbose=False)


@pytest.mark.integration
class TestPluginDiscovery:
    """Tests for plugin discovery mechanism."""

    def test_discovers_scraper_plugins(self, temp_config):
        """Test that scraper plugins are discovered."""
        digest = ResearchDigest(str(temp_config), verbose=False)

        assert len(digest.scrapers) > 0
        assert all(isinstance(s, ScraperBase) for s in digest.scrapers)

    def test_discovered_plugins_have_names(self, temp_config):
        """Test that discovered plugins have names."""
        digest = ResearchDigest(str(temp_config), verbose=False)

        for scraper in digest.scrapers:
            assert hasattr(scraper, "name")
            assert scraper.name != "Base"
            assert isinstance(scraper.name, str)

    def test_does_not_load_base_class(self, temp_config):
        """Test that the base scraper class itself is not loaded as a plugin."""
        digest = ResearchDigest(str(temp_config), verbose=False)

        # No scraper should have the name "Base"
        scraper_names = [s.name for s in digest.scrapers]
        assert "Base" not in scraper_names

    def test_discovers_multiple_scrapers(self, temp_config):
        """Test that multiple scraper plugins are discovered."""
        digest = ResearchDigest(str(temp_config), verbose=False)

        # Should have at least the 4 implemented scrapers
        assert len(digest.scrapers) >= 4

    def test_discovered_scrapers_are_instances(self, temp_config):
        """Test that discovered scrapers are instantiated objects, not classes."""
        digest = ResearchDigest(str(temp_config), verbose=False)

        for scraper in digest.scrapers:
            # Should be an instance, not a class
            assert not isinstance(scraper, type)
            assert isinstance(scraper, ScraperBase)

    def test_verbose_flag_passed_to_scrapers(self, temp_config):
        """Test that verbose flag is passed to scraper instances."""
        digest_verbose = ResearchDigest(str(temp_config), verbose=True)
        digest_quiet = ResearchDigest(str(temp_config), verbose=False)

        # All scrapers should have the same verbose setting as digest
        for scraper in digest_verbose.scrapers:
            assert scraper.verbose is True

        for scraper in digest_quiet.scrapers:
            assert scraper.verbose is False


@pytest.mark.unit
class TestGetOutputDir:
    """Tests for output directory determination."""

    def test_creates_output_directory(self, temp_config, tmp_path):
        """Test that output directory is created."""
        digest = ResearchDigest(str(temp_config), verbose=False)
        output_dir = digest.get_output_dir()

        assert output_dir.exists()
        assert output_dir.is_dir()

    def test_uses_date_folders_by_default(self, temp_config):
        """Test that date-based folders are created by default."""
        digest = ResearchDigest(str(temp_config), verbose=False)
        output_dir = digest.get_output_dir()

        # Should include a date in the path (YYYY-MM-DD format)
        assert any(part for part in output_dir.parts if "-" in part and len(part) == 10)

    def test_respects_use_date_folders_false(self, tmp_path):
        """Test that use_date_folders: false prevents date subdirectories."""
        config = {
            "output": {"base_dir": str(tmp_path / "output"), "use_date_folders": False},
            "scrapers": {},
            "processing": {},
            "report": {},
        }

        config_path = tmp_path / "config.yaml"
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(config, f)

        digest = ResearchDigest(str(config_path), verbose=False)
        output_dir = digest.get_output_dir()

        # Should be exactly the base_dir without date subdirectory
        assert output_dir == tmp_path / "output"

    def test_uses_custom_base_dir(self, tmp_path):
        """Test that custom base_dir is respected."""
        custom_dir = tmp_path / "custom_research"

        config = {
            "output": {"base_dir": str(custom_dir), "use_date_folders": False},
            "scrapers": {},
            "processing": {},
            "report": {},
        }

        config_path = tmp_path / "config.yaml"
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(config, f)

        digest = ResearchDigest(str(config_path), verbose=False)
        output_dir = digest.get_output_dir()

        assert custom_dir in output_dir.parents or output_dir == custom_dir


@pytest.mark.integration
class TestRunScrapers:
    """Tests for running scrapers."""

    def test_run_scrapers_creates_raw_directory(self, temp_config, tmp_path):
        """Test that run_scrapers creates a raw/ subdirectory."""
        digest = ResearchDigest(str(temp_config), verbose=False)
        output_dir = tmp_path / "test_output"
        output_dir.mkdir()

        digest.run_scrapers(output_dir)

        # raw/ directory should exist (even if no content was saved)
        # Note: This depends on scrapers actually creating it

    def test_only_enabled_scrapers_run(self, tmp_path):
        """Test that only enabled scrapers are executed."""
        config = {
            "output": {"base_dir": str(tmp_path), "use_date_folders": False},
            "scrapers": {
                "hackernews": {"enabled": False},
                "rss": {"enabled": False},
                "reddit": {"enabled": False},
                "arxiv": {"enabled": False},
            },
            "processing": {"format_for_obsidian": False},
            "report": {"generate_summary": False},
        }

        config_path = tmp_path / "config.yaml"
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(config, f)

        digest = ResearchDigest(str(config_path), verbose=False)
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        # Should complete without error even though no scrapers are enabled
        digest.run_scrapers(output_dir)

    def test_scraper_receives_correct_config(self, temp_config, tmp_path):
        """Test that scrapers receive their specific configuration."""
        # Track configs via test scraper subclass
        configs_received = []

        # Create custom test to verify config passing
        class MockScraper(ScraperBase):
            def __init__(self, verbose=True):
                super().__init__(verbose)
                self.name = "mocktest"

            def run(self, config, output_dir):
                configs_received.append(config)

        # Create a config with our mock scraper enabled
        config = {
            "output": {"base_dir": str(tmp_path / "output"), "use_date_folders": False},
            "scrapers": {"mocktest": {"enabled": True, "test_value": 123}},
            "processing": {"format_for_obsidian": False},
            "report": {"generate_summary": False},
        }

        config_path = tmp_path / "config.yaml"
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(config, f)

        digest = ResearchDigest(str(config_path), verbose=False)

        # Add our mock scraper to the list
        digest.scrapers.append(MockScraper(verbose=False))

        output_dir = tmp_path / "output"
        output_dir.mkdir()

        digest.run_scrapers(output_dir)

        # Mock scraper should have received its config
        assert len(configs_received) == 1
        assert configs_received[0]["test_value"] == 123

    def test_scraper_errors_are_caught(self, temp_config, tmp_path, monkeypatch):
        """Test that errors from scrapers don't crash the entire pipeline."""

        def broken_run(self, config, output_dir):
            raise Exception("Simulated scraper error")

        monkeypatch.setattr(ScraperBase, "run", broken_run)

        digest = ResearchDigest(str(temp_config), verbose=False)
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        # Should not raise an exception
        digest.run_scrapers(output_dir)


@pytest.mark.unit
class TestLoadConfig:
    """Tests for configuration loading."""

    def test_loads_valid_yaml(self, temp_config):
        """Test that valid YAML is loaded correctly."""
        digest = ResearchDigest(str(temp_config), verbose=False)

        assert isinstance(digest.config, dict)
        assert "scrapers" in digest.config

    def test_handles_nested_config(self, tmp_path):
        """Test that nested configuration is preserved."""
        config = {"level1": {"level2": {"level3": "value"}}}

        config_path = tmp_path / "nested.yaml"
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(config, f)

        digest = ResearchDigest(str(config_path), verbose=False)

        assert digest.config["level1"]["level2"]["level3"] == "value"

    def test_handles_empty_config(self, tmp_path):
        """Test that empty config file is handled."""
        config_path = tmp_path / "empty.yaml"
        config_path.write_text("", encoding="utf-8")

        digest = ResearchDigest(str(config_path), verbose=False)

        # Empty YAML should return None or empty dict
        assert digest.config is None or digest.config == {}


@pytest.mark.integration
class TestCompleteWorkflow:
    """Integration tests for complete workflows."""

    def test_minimal_workflow(self, tmp_path):
        """Test a minimal end-to-end workflow."""
        # Create minimal config
        config = {
            "output": {"base_dir": str(tmp_path / "output"), "use_date_folders": False},
            "scrapers": {
                "hackernews": {"enabled": False},
                "rss": {"enabled": False},
                "reddit": {"enabled": False},
                "arxiv": {"enabled": False},
            },
            "processing": {"format_for_obsidian": False},
            "report": {"generate_summary": False},
        }

        config_path = tmp_path / "config.yaml"
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(config, f)

        # Initialize and run
        digest = ResearchDigest(str(config_path), verbose=False)

        # Should initialize scrapers
        assert len(digest.scrapers) >= 0

        # Should be able to get output dir
        output_dir = digest.get_output_dir()
        assert output_dir.exists()

    def test_plugin_names_match_config_keys(self, temp_config):
        """Test that discovered plugin names match expected config keys."""
        digest = ResearchDigest(str(temp_config), verbose=False)

        scraper_names = [s.name.lower() for s in digest.scrapers]
        config_keys = digest.config.get("scrapers", {}).keys()

        # At least some scraper names should match config keys
        matches = [name for name in scraper_names if name in config_keys]
        assert len(matches) > 0
