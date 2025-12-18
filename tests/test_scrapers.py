#!/usr/bin/env python3
"""
Tests for scrapers/base.py - Base scraper class and plugin architecture.
"""

import sys
from pathlib import Path

import pytest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scrapers.base import ScraperBase


@pytest.mark.unit
class TestScraperBase:
    """Tests for the ScraperBase class."""

    def test_initialization_default_verbose(self):
        """Test that ScraperBase initializes with default verbose=True."""
        scraper = ScraperBase()

        assert scraper.verbose is True
        assert scraper.name == "Base"

    def test_initialization_with_verbose_false(self):
        """Test that ScraperBase can be initialized with verbose=False."""
        scraper = ScraperBase(verbose=False)

        assert scraper.verbose is False
        assert scraper.name == "Base"

    def test_run_method_not_implemented(self, tmp_path):
        """Test that calling run() raises NotImplementedError."""
        scraper = ScraperBase()

        with pytest.raises(NotImplementedError) as exc_info:
            scraper.run(config={}, output_dir=tmp_path)

        assert "must be implemented" in str(exc_info.value)

    def test_name_attribute_exists(self):
        """Test that the name attribute is set."""
        scraper = ScraperBase()

        assert hasattr(scraper, "name")
        assert isinstance(scraper.name, str)

    def test_verbose_attribute_exists(self):
        """Test that the verbose attribute is set."""
        scraper = ScraperBase()

        assert hasattr(scraper, "verbose")
        assert isinstance(scraper.verbose, bool)


@pytest.mark.unit
class TestScraperInheritance:
    """Tests for scraper inheritance from ScraperBase."""

    def test_subclass_can_implement_run(self, tmp_path):
        """Test that subclasses can successfully implement run()."""

        class TestScraper(ScraperBase):
            def __init__(self, verbose=True):
                super().__init__(verbose)
                self.name = "TestScraper"

            def run(self, config, output_dir):
                # Simple implementation
                self.last_config = config
                self.last_output_dir = output_dir
                return "Success"

        scraper = TestScraper()
        config = {"test": "value"}
        result = scraper.run(config, tmp_path)

        assert result == "Success"
        assert scraper.last_config == config
        assert scraper.last_output_dir == tmp_path

    def test_subclass_inherits_attributes(self):
        """Test that subclasses inherit verbose and name attributes."""

        class TestScraper(ScraperBase):
            def __init__(self, verbose=True):
                super().__init__(verbose)
                self.name = "TestScraper"

        scraper = TestScraper(verbose=False)

        assert scraper.verbose is False
        assert scraper.name == "TestScraper"

    def test_multiple_scrapers_can_coexist(self):
        """Test that multiple scraper instances can exist independently."""

        class Scraper1(ScraperBase):
            def __init__(self):
                super().__init__()
                self.name = "Scraper1"

        class Scraper2(ScraperBase):
            def __init__(self):
                super().__init__()
                self.name = "Scraper2"

        s1 = Scraper1()
        s2 = Scraper2()

        assert s1.name == "Scraper1"
        assert s2.name == "Scraper2"
        assert s1 is not s2


@pytest.mark.integration
class TestScraperContract:
    """Tests for the scraper contract/interface."""

    def test_scraper_accepts_config_dict(self, tmp_path):
        """Test that scrapers accept a config dictionary."""

        class TestScraper(ScraperBase):
            def __init__(self):
                super().__init__()
                self.name = "TestScraper"

            def run(self, config, output_dir):
                assert isinstance(config, dict)
                return config

        scraper = TestScraper()
        config = {"enabled": True, "days_back": 7, "topics": ["test", "example"]}

        result = scraper.run(config, tmp_path)
        assert result == config

    def test_scraper_accepts_output_dir_path(self, tmp_path):
        """Test that scrapers accept an output_dir Path object."""

        class TestScraper(ScraperBase):
            def __init__(self):
                super().__init__()
                self.name = "TestScraper"

            def run(self, config, output_dir):
                assert isinstance(output_dir, Path)
                return output_dir

        scraper = TestScraper()
        result = scraper.run({}, tmp_path)

        assert result == tmp_path
        assert isinstance(result, Path)

    def test_scraper_can_write_to_output_dir(self, tmp_path):
        """Test that scrapers can write files to the output directory."""

        class TestScraper(ScraperBase):
            def __init__(self):
                super().__init__()
                self.name = "TestScraper"

            def run(self, config, output_dir):
                # Create a subdirectory
                scraper_dir = output_dir / "test_scraper"
                scraper_dir.mkdir(parents=True, exist_ok=True)

                # Write a test file
                test_file = scraper_dir / "test.md"
                test_file.write_text("Test content", encoding="utf-8")

                return scraper_dir

        scraper = TestScraper()
        result_dir = scraper.run({}, tmp_path)

        assert result_dir.exists()
        assert (result_dir / "test.md").exists()
        assert (result_dir / "test.md").read_text(encoding="utf-8") == "Test content"


@pytest.mark.unit
class TestScraperEdgeCases:
    """Tests for edge cases and error handling."""

    def test_run_with_empty_config(self, tmp_path):
        """Test that scrapers handle empty config dictionary."""

        class TestScraper(ScraperBase):
            def __init__(self):
                super().__init__()
                self.name = "TestScraper"

            def run(self, config, output_dir):
                return len(config)

        scraper = TestScraper()
        result = scraper.run({}, tmp_path)

        assert result == 0

    def test_run_with_none_values_in_config(self, tmp_path):
        """Test that scrapers handle None values in config."""

        class TestScraper(ScraperBase):
            def __init__(self):
                super().__init__()
                self.name = "TestScraper"

            def run(self, config, output_dir):
                return config.get("missing_key", "default")

        scraper = TestScraper()
        config = {"key1": None, "key2": "value"}
        result = scraper.run(config, tmp_path)

        assert result == "default"

    def test_verbose_affects_behavior(self, tmp_path, capsys):
        """Test that verbose flag can affect scraper behavior."""

        class TestScraper(ScraperBase):
            def __init__(self, verbose=True):
                super().__init__(verbose)
                self.name = "TestScraper"

            def run(self, config, output_dir):
                if self.verbose:
                    print("Processing...")
                return "done"

        # Test with verbose=True
        scraper_verbose = TestScraper(verbose=True)
        scraper_verbose.run({}, tmp_path)

        captured = capsys.readouterr()
        assert "Processing..." in captured.out

        # Test with verbose=False
        scraper_silent = TestScraper(verbose=False)
        scraper_silent.run({}, tmp_path)

        captured = capsys.readouterr()
        assert "Processing..." not in captured.out


@pytest.mark.integration
class TestRealScraperPatterns:
    """Tests for common patterns used in real scrapers."""

    def test_scraper_with_database_integration_pattern(self, tmp_path):
        """Test the pattern of checking database and adding items."""

        class TestScraper(ScraperBase):
            def __init__(self):
                super().__init__()
                self.name = "TestScraper"
                self.processed_items = set()

            def run(self, config, output_dir):
                items = ["item1", "item2", "item3"]
                new_items = []

                for item in items:
                    # Simulate database check
                    if item not in self.processed_items:
                        new_items.append(item)
                        self.processed_items.add(item)

                return new_items

        scraper = TestScraper()

        # First run should return all items
        result1 = scraper.run({}, tmp_path)
        assert len(result1) == 3

        # Second run should return no items (all already processed)
        result2 = scraper.run({}, tmp_path)
        assert len(result2) == 0

    def test_scraper_with_file_saving_pattern(self, tmp_path):
        """Test the pattern of saving multiple files."""

        class TestScraper(ScraperBase):
            def __init__(self):
                super().__init__()
                self.name = "TestScraper"

            def run(self, config, output_dir):
                # Create source subdirectory
                source_dir = output_dir / self.name.lower()
                source_dir.mkdir(parents=True, exist_ok=True)

                # Save multiple files
                for i in range(5):
                    filepath = source_dir / f"item_{i}.md"
                    filepath.write_text(f"# Item {i}\n\nContent {i}", encoding="utf-8")

                return source_dir

        scraper = TestScraper()
        result_dir = scraper.run({}, tmp_path)

        # Verify files were created
        assert result_dir.exists()
        files = list(result_dir.glob("*.md"))
        assert len(files) == 5

        # Verify content
        for i in range(5):
            filepath = result_dir / f"item_{i}.md"
            content = filepath.read_text(encoding="utf-8")
            assert f"Item {i}" in content

    def test_scraper_with_config_based_behavior(self, tmp_path):
        """Test that scrapers use config to control behavior."""

        class TestScraper(ScraperBase):
            def __init__(self):
                super().__init__()
                self.name = "TestScraper"

            def run(self, config, output_dir):
                enabled = config.get("enabled", True)
                max_items = config.get("max_items", 10)

                if not enabled:
                    return []

                # Generate items based on config
                items = [f"item_{i}" for i in range(max_items)]
                return items

        scraper = TestScraper()

        # Test with default config
        result1 = scraper.run({}, tmp_path)
        assert len(result1) == 10

        # Test with custom max_items
        result2 = scraper.run({"max_items": 5}, tmp_path)
        assert len(result2) == 5

        # Test with enabled=False
        result3 = scraper.run({"enabled": False}, tmp_path)
        assert len(result3) == 0
