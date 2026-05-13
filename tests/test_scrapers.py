#!/usr/bin/env python3
"""
Tests for scrapers - Base scraper class, plugin architecture, and scraper run() methods.
"""

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

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


# ===========================================================================
# HNScraper run() method tests
# ===========================================================================


@pytest.mark.integration
class TestHNScraperRun:
    """Tests for HNScraper.run() — covers the main processing loop."""

    def _make_story(self, story_id=42, descendants=25, kids=None):
        return {
            "id": story_id,
            "title": "Test Story Title",
            "by": "testuser",
            "score": 100,
            "descendants": descendants,
            "time": 1700000000,
            "url": "https://example.com/article",
            "text": None,
            "kids": kids or [],
        }

    @patch("scrapers.hn_scraper.time.sleep")
    @patch("scrapers.hn_scraper.utils.save_document")
    @patch("scrapers.hn_scraper.database.add_item")
    @patch("scrapers.hn_scraper.database.item_exists", return_value=False)
    def test_run_processes_new_story(
        self, mock_exists, mock_add, mock_save, mock_sleep, tmp_path
    ):
        from rdt.shared.config_models import HNConfig
        from scrapers.hn_scraper import HNScraper

        scraper = HNScraper(verbose=False)
        mock_client = MagicMock()
        mock_client.search_stories.return_value = [42]
        mock_client.get_item.return_value = self._make_story(story_id=42)
        scraper.client = mock_client

        config = HNConfig(min_points=50, min_comments=20, search_topics=["AI"])
        scraper.run(config, tmp_path)

        mock_add.assert_called_once()
        mock_save.assert_called_once()
        mock_sleep.assert_called_once_with(1)

    @patch("scrapers.hn_scraper.time.sleep")
    @patch("scrapers.hn_scraper.utils.save_document")
    @patch("scrapers.hn_scraper.database.add_item")
    @patch("scrapers.hn_scraper.database.item_exists", return_value=True)
    def test_run_skips_already_processed_story(
        self, mock_exists, mock_add, mock_save, mock_sleep, tmp_path
    ):
        from rdt.shared.config_models import HNConfig
        from scrapers.hn_scraper import HNScraper

        scraper = HNScraper(verbose=False)
        mock_client = MagicMock()
        mock_client.search_stories.return_value = [42]
        scraper.client = mock_client

        config = HNConfig(min_points=50, min_comments=20, search_topics=["AI"])
        scraper.run(config, tmp_path)

        mock_add.assert_not_called()
        mock_save.assert_not_called()

    @patch("scrapers.hn_scraper.time.sleep")
    @patch("scrapers.hn_scraper.utils.save_document")
    @patch("scrapers.hn_scraper.database.add_item")
    @patch("scrapers.hn_scraper.database.item_exists", return_value=False)
    def test_run_skips_story_below_min_comments(
        self, mock_exists, mock_add, mock_save, mock_sleep, tmp_path
    ):
        from rdt.shared.config_models import HNConfig
        from scrapers.hn_scraper import HNScraper

        scraper = HNScraper(verbose=False)
        mock_client = MagicMock()
        mock_client.search_stories.return_value = [42]
        mock_client.get_item.return_value = self._make_story(descendants=5)
        scraper.client = mock_client

        config = HNConfig(min_points=50, min_comments=20, search_topics=["AI"])
        scraper.run(config, tmp_path)

        mock_add.assert_not_called()

    @patch("scrapers.hn_scraper.time.sleep")
    @patch("scrapers.hn_scraper.utils.save_document")
    @patch("scrapers.hn_scraper.database.add_item")
    @patch("scrapers.hn_scraper.database.item_exists", return_value=False)
    def test_run_handles_search_error_gracefully(
        self, mock_exists, mock_add, mock_save, mock_sleep, tmp_path
    ):
        from rdt.shared.config_models import HNConfig
        from scrapers.hn_scraper import HNScraper

        scraper = HNScraper(verbose=False)
        mock_client = MagicMock()
        mock_client.search_stories.side_effect = Exception("Network error")
        scraper.client = mock_client

        config = HNConfig(min_points=50, min_comments=20, search_topics=["AI"])
        # Should not raise — errors are caught and logged
        scraper.run(config, tmp_path)

        mock_add.assert_not_called()

    @patch("scrapers.hn_scraper.time.sleep")
    @patch("scrapers.hn_scraper.utils.save_document")
    @patch("scrapers.hn_scraper.database.add_item")
    @patch("scrapers.hn_scraper.database.item_exists", return_value=False)
    def test_run_empty_search_topics_processes_nothing(
        self, mock_exists, mock_add, mock_save, mock_sleep, tmp_path
    ):
        from rdt.shared.config_models import HNConfig
        from scrapers.hn_scraper import HNScraper

        scraper = HNScraper(verbose=False)
        mock_client = MagicMock()
        scraper.client = mock_client

        config = HNConfig(min_points=50, min_comments=20, search_topics=[])
        scraper.run(config, tmp_path)

        mock_client.search_stories.assert_not_called()
        mock_add.assert_not_called()

    @patch("scrapers.hn_scraper.time.sleep")
    @patch("scrapers.hn_scraper.utils.save_document")
    @patch("scrapers.hn_scraper.database.add_item")
    @patch("scrapers.hn_scraper.database.item_exists", return_value=False)
    def test_run_story_with_kids_fetches_comments(
        self, mock_exists, mock_add, mock_save, mock_sleep, tmp_path
    ):
        from rdt.shared.config_models import HNConfig
        from scrapers.hn_scraper import HNScraper

        scraper = HNScraper(verbose=False)
        mock_client = MagicMock()
        mock_client.search_stories.return_value = [42]
        story = self._make_story(story_id=42, kids=[100, 101])
        mock_client.get_item.side_effect = [
            story,
            {"by": "commenter1", "text": "Great post!", "kids": []},
            {"by": "commenter2", "text": "Agreed!", "kids": []},
        ]
        scraper.client = mock_client

        config = HNConfig(min_points=50, min_comments=20, search_topics=["AI"])
        scraper.run(config, tmp_path)

        mock_add.assert_called_once()


# ===========================================================================
# RedditScraper run() method tests
# ===========================================================================


@pytest.mark.integration
class TestRedditScraperRun:
    """Tests for RedditScraper.run() — covers the main processing loop."""

    def _make_post(self, post_id="abc123", score=200, title="Test Post"):
        return {
            "id": post_id,
            "title": title,
            "score": score,
            "selftext": "Post body content here.",
            "author": "testuser",
            "permalink": f"/r/ExperiencedDevs/comments/{post_id}/test_post/",
            "url": f"https://www.reddit.com/r/ExperiencedDevs/comments/{post_id}/",
            "created_utc": 1700000000,
            "num_comments": 50,
            "link_flair_text": None,
        }

    @patch("scrapers.reddit_scraper.time.sleep")
    @patch("scrapers.reddit_scraper.utils.save_document")
    @patch("scrapers.reddit_scraper.database.add_item")
    @patch("scrapers.reddit_scraper.database.item_exists", return_value=False)
    @patch("scrapers.reddit_scraper._fetch_comments", return_value=[])
    @patch("scrapers.reddit_scraper._fetch_subreddit")
    def test_run_processes_new_post(
        self,
        mock_fetch_sub,
        mock_fetch_comments,
        mock_exists,
        mock_add,
        mock_save,
        mock_sleep,
        tmp_path,
    ):
        from rdt.shared.config_models import RedditConfig, RedditSubreddit
        from scrapers.reddit_scraper import RedditScraper

        mock_fetch_sub.return_value = [self._make_post()]

        scraper = RedditScraper(verbose=False)
        config = RedditConfig(
            subreddits=[RedditSubreddit(name="ExperiencedDevs", min_upvotes=50)]
        )
        scraper.run(config, tmp_path)

        mock_add.assert_called_once()
        mock_save.assert_called_once()

    @patch("scrapers.reddit_scraper.time.sleep")
    @patch("scrapers.reddit_scraper.utils.save_document")
    @patch("scrapers.reddit_scraper.database.add_item")
    @patch("scrapers.reddit_scraper.database.item_exists", return_value=True)
    @patch("scrapers.reddit_scraper._fetch_comments", return_value=[])
    @patch("scrapers.reddit_scraper._fetch_subreddit")
    def test_run_skips_already_processed_post(
        self,
        mock_fetch_sub,
        mock_fetch_comments,
        mock_exists,
        mock_add,
        mock_save,
        mock_sleep,
        tmp_path,
    ):
        from rdt.shared.config_models import RedditConfig, RedditSubreddit
        from scrapers.reddit_scraper import RedditScraper

        mock_fetch_sub.return_value = [self._make_post()]

        scraper = RedditScraper(verbose=False)
        config = RedditConfig(
            subreddits=[RedditSubreddit(name="ExperiencedDevs", min_upvotes=50)]
        )
        scraper.run(config, tmp_path)

        mock_add.assert_not_called()

    @patch("scrapers.reddit_scraper.time.sleep")
    @patch("scrapers.reddit_scraper.utils.save_document")
    @patch("scrapers.reddit_scraper.database.add_item")
    @patch("scrapers.reddit_scraper.database.item_exists", return_value=False)
    @patch("scrapers.reddit_scraper._fetch_comments", return_value=[])
    @patch("scrapers.reddit_scraper._fetch_subreddit")
    def test_run_skips_post_below_min_upvotes(
        self,
        mock_fetch_sub,
        mock_fetch_comments,
        mock_exists,
        mock_add,
        mock_save,
        mock_sleep,
        tmp_path,
    ):
        from rdt.shared.config_models import RedditConfig, RedditSubreddit
        from scrapers.reddit_scraper import RedditScraper

        mock_fetch_sub.return_value = [self._make_post(score=10)]

        scraper = RedditScraper(verbose=False)
        config = RedditConfig(
            subreddits=[RedditSubreddit(name="ExperiencedDevs", min_upvotes=100)]
        )
        scraper.run(config, tmp_path)

        mock_add.assert_not_called()

    @patch("scrapers.reddit_scraper.time.sleep")
    @patch("scrapers.reddit_scraper.utils.save_document")
    @patch("scrapers.reddit_scraper.database.add_item")
    @patch("scrapers.reddit_scraper.database.item_exists", return_value=False)
    @patch("scrapers.reddit_scraper._fetch_comments", return_value=[])
    @patch("scrapers.reddit_scraper._fetch_subreddit")
    def test_run_handles_fetch_error_gracefully(
        self,
        mock_fetch_sub,
        mock_fetch_comments,
        mock_exists,
        mock_add,
        mock_save,
        mock_sleep,
        tmp_path,
    ):
        from rdt.shared.config_models import RedditConfig, RedditSubreddit
        from scrapers.reddit_scraper import RedditScraper

        mock_fetch_sub.side_effect = Exception("Rate limited")

        scraper = RedditScraper(verbose=False)
        config = RedditConfig(
            subreddits=[RedditSubreddit(name="ExperiencedDevs", min_upvotes=50)]
        )
        # Should not raise — errors are caught
        scraper.run(config, tmp_path)

        mock_add.assert_not_called()

    @patch("scrapers.reddit_scraper._fetch_subreddit")
    def test_run_empty_subreddits_list(self, mock_fetch_sub, tmp_path):
        from rdt.shared.config_models import RedditConfig
        from scrapers.reddit_scraper import RedditScraper

        scraper = RedditScraper(verbose=False)
        config = RedditConfig(subreddits=[])
        scraper.run(config, tmp_path)

        mock_fetch_sub.assert_not_called()

    @patch("scrapers.reddit_scraper.time.sleep")
    @patch("scrapers.reddit_scraper.utils.save_document")
    @patch("scrapers.reddit_scraper.database.add_item")
    @patch("scrapers.reddit_scraper.database.item_exists", return_value=False)
    @patch("scrapers.reddit_scraper._fetch_comments", return_value=[])
    @patch("scrapers.reddit_scraper._fetch_subreddit")
    def test_run_post_missing_id_skipped(
        self,
        mock_fetch_sub,
        mock_fetch_comments,
        mock_exists,
        mock_add,
        mock_save,
        mock_sleep,
        tmp_path,
    ):
        from rdt.shared.config_models import RedditConfig, RedditSubreddit
        from scrapers.reddit_scraper import RedditScraper

        # Post with no id field
        mock_fetch_sub.return_value = [{"title": "No ID post", "score": 200}]

        scraper = RedditScraper(verbose=False)
        config = RedditConfig(
            subreddits=[RedditSubreddit(name="ExperiencedDevs", min_upvotes=50)]
        )
        scraper.run(config, tmp_path)

        mock_add.assert_not_called()


# ===========================================================================
# ArxivScraper run() method tests
# ===========================================================================


@pytest.mark.integration
class TestArxivScraperRun:
    """Tests for ArxivScraper.run() — covers the main processing loop."""

    def _make_paper(self, entry_id="http://arxiv.org/abs/2301.00001v1", days_old=1):
        paper = MagicMock()
        paper.entry_id = entry_id
        paper.title = "Test Paper Title: A Study of Something"
        author = MagicMock()
        author.name = "Author One"
        paper.authors = [author]
        paper.summary = "This paper studies something important."
        paper.published = datetime.now(timezone.utc) - timedelta(days=days_old)
        paper.updated = paper.published
        paper.primary_category = "cs.AI"
        paper.categories = ["cs.AI"]
        paper.pdf_url = entry_id.replace("abs", "pdf")
        return paper

    @patch("scrapers.arxiv_scraper.utils.save_document")
    @patch("scrapers.arxiv_scraper.database.add_item")
    @patch("scrapers.arxiv_scraper.database.item_exists", return_value=False)
    @patch("scrapers.arxiv_scraper.arxiv.Search")
    def test_run_processes_new_paper(
        self, mock_search_cls, mock_exists, mock_add, mock_save, tmp_path
    ):
        from rdt.shared.config_models import ArxivConfig
        from scrapers.arxiv_scraper import ArxivScraper

        paper = self._make_paper()
        mock_search_instance = MagicMock()
        mock_search_instance.results.return_value = [paper]
        mock_search_cls.return_value = mock_search_instance

        scraper = ArxivScraper(verbose=False)
        config = ArxivConfig(
            search_queries=["machine learning"], days_back=7, max_results=10
        )
        scraper.run(config, tmp_path)

        mock_add.assert_called_once()
        mock_save.assert_called_once()

    @patch("scrapers.arxiv_scraper.utils.save_document")
    @patch("scrapers.arxiv_scraper.database.add_item")
    @patch("scrapers.arxiv_scraper.database.item_exists", return_value=True)
    @patch("scrapers.arxiv_scraper.arxiv.Search")
    def test_run_skips_already_processed_paper(
        self, mock_search_cls, mock_exists, mock_add, mock_save, tmp_path
    ):
        from rdt.shared.config_models import ArxivConfig
        from scrapers.arxiv_scraper import ArxivScraper

        paper = self._make_paper()
        mock_search_instance = MagicMock()
        mock_search_instance.results.return_value = [paper]
        mock_search_cls.return_value = mock_search_instance

        scraper = ArxivScraper(verbose=False)
        config = ArxivConfig(
            search_queries=["deep learning"], days_back=7, max_results=10
        )
        scraper.run(config, tmp_path)

        mock_add.assert_not_called()

    @patch("scrapers.arxiv_scraper.utils.save_document")
    @patch("scrapers.arxiv_scraper.database.add_item")
    @patch("scrapers.arxiv_scraper.database.item_exists", return_value=False)
    @patch("scrapers.arxiv_scraper.arxiv.Search")
    def test_run_stops_at_papers_outside_time_window(
        self, mock_search_cls, mock_exists, mock_add, mock_save, tmp_path
    ):
        from rdt.shared.config_models import ArxivConfig
        from scrapers.arxiv_scraper import ArxivScraper

        old_paper = self._make_paper(entry_id="http://arxiv.org/abs/old", days_old=10)
        mock_search_instance = MagicMock()
        mock_search_instance.results.return_value = [old_paper]
        mock_search_cls.return_value = mock_search_instance

        scraper = ArxivScraper(verbose=False)
        config = ArxivConfig(search_queries=["nlp"], days_back=7, max_results=10)
        scraper.run(config, tmp_path)

        mock_add.assert_not_called()

    @patch("scrapers.arxiv_scraper.utils.save_document")
    @patch("scrapers.arxiv_scraper.database.add_item")
    @patch("scrapers.arxiv_scraper.database.item_exists", return_value=False)
    @patch("scrapers.arxiv_scraper.arxiv.Search")
    def test_run_handles_search_error_gracefully(
        self, mock_search_cls, mock_exists, mock_add, mock_save, tmp_path
    ):
        from rdt.shared.config_models import ArxivConfig
        from scrapers.arxiv_scraper import ArxivScraper

        mock_search_cls.side_effect = Exception("API timeout")

        scraper = ArxivScraper(verbose=False)
        config = ArxivConfig(search_queries=["robotics"], days_back=7, max_results=10)
        # Should not raise — errors are caught
        scraper.run(config, tmp_path)

        mock_add.assert_not_called()

    @patch("scrapers.arxiv_scraper.arxiv.Search")
    def test_run_empty_queries_processes_nothing(self, mock_search_cls, tmp_path):
        from rdt.shared.config_models import ArxivConfig
        from scrapers.arxiv_scraper import ArxivScraper

        scraper = ArxivScraper(verbose=False)
        config = ArxivConfig(search_queries=[], days_back=7, max_results=10)
        scraper.run(config, tmp_path)

        mock_search_cls.assert_not_called()


# ===========================================================================
# Reddit helper function direct unit tests
# ===========================================================================


@pytest.mark.unit
class TestRedditHelpers:
    """Direct unit tests for reddit_scraper helper functions."""

    def test_fetch_subreddit_parses_response(self):
        from scrapers.reddit_scraper import _fetch_subreddit

        mock_client = MagicMock()
        mock_resp = MagicMock()
        mock_resp.json.return_value = {
            "data": {
                "children": [
                    {"data": {"id": "abc", "title": "Post 1", "score": 200}},
                    {"data": {"id": "def", "title": "Post 2", "score": 100}},
                ]
            }
        }
        mock_client.get.return_value = mock_resp
        result = _fetch_subreddit(mock_client, "ExperiencedDevs", "week", 50)
        assert len(result) == 2
        assert result[0]["id"] == "abc"

    def test_fetch_subreddit_empty_response(self):
        from scrapers.reddit_scraper import _fetch_subreddit

        mock_client = MagicMock()
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"data": {"children": []}}
        mock_client.get.return_value = mock_resp
        result = _fetch_subreddit(mock_client, "test", "week", 25)
        assert result == []

    def test_fetch_comments_parses_response(self):
        from scrapers.reddit_scraper import _fetch_comments

        mock_client = MagicMock()
        mock_resp = MagicMock()
        mock_resp.json.return_value = [
            {},  # post listing (ignored)
            {
                "data": {
                    "children": [
                        {
                            "kind": "t1",
                            "data": {
                                "author": "user1",
                                "body": "comment 1",
                                "score": 10,
                                "replies": "",
                            },
                        },
                    ]
                }
            },
        ]
        mock_client.get.return_value = mock_resp
        result = _fetch_comments(mock_client, "abc123", "ExperiencedDevs", 50)
        assert len(result) == 1
        assert result[0]["author"] == "user1"

    def test_format_post_returns_markdown(self):
        from scrapers.reddit_scraper import _format_post

        post = {
            "title": "Test Post",
            "author": "testuser",
            "score": 150,
            "num_comments": 30,
            "permalink": "/r/test/comments/abc/test_post/",
            "created_utc": 1700000000,
            "selftext": "Post body here.",
            "url": "https://example.com",
        }
        result = _format_post(post, [], [])
        assert "Test Post" in result
        assert "testuser" in result
        assert "150" in result


@pytest.mark.unit
class TestHNHelpers:
    """Direct unit tests for hn_scraper helper functions."""

    def test_format_story_returns_markdown(self):
        from scrapers.hn_scraper import _format_story

        story = {
            "id": 42,
            "title": "Test Story",
            "by": "testuser",
            "score": 100,
            "descendants": 25,
            "time": 1700000000,
            "url": "https://example.com",
            "comments": [],
        }
        result = _format_story(story)
        assert "Test Story" in result
        assert "testuser" in result
        assert "100" in result

    def test_format_comments_returns_empty_for_no_comments(self):
        from scrapers.hn_scraper import _format_comments

        result = _format_comments([], 0)
        assert result == ""

    def test_format_comments_formats_comment(self):
        from scrapers.hn_scraper import _format_comments

        comments = [{"by": "user1", "text": "Great post!", "score": 5, "replies": []}]
        result = _format_comments(comments, 0)
        assert "user1" in result
        assert "Great post!" in result
