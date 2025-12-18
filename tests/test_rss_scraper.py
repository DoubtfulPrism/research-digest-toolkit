#!/usr/bin/env python3
"""
Integration and unit tests for RSS scraper plugin.

Testing Strategy:
1. Unit tests for helper functions (_fetch_feed, _filter_entries_by_date, _format_entry)
2. Integration tests for RSSScraper.run() with mocked feeds
3. Database integration verification
4. File I/O verification
5. Error handling and edge cases

Pattern established here will be replicated for other scrapers.
"""

import sys
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import database
from scrapers.rss_scraper import (
    RSSScraper,
    _fetch_feed,
    _filter_entries_by_date,
    _format_entry,
)

# ============================================================================
# FIXTURES - Reusable test data
# ============================================================================


@pytest.fixture
def mock_feed_entry():
    """Create a mock RSS feed entry with complete data."""
    entry = Mock()
    entry.title = "Test Article Title"
    entry.link = "https://example.com/article-123"
    entry.author = "Test Author"
    entry.summary = "<p>This is a test article summary with <strong>HTML</strong>.</p>"

    # Published date (2 days ago)
    two_days_ago = datetime.now() - timedelta(days=2)
    entry.published_parsed = two_days_ago.timetuple()[:6]

    # Content
    entry.content = [{"value": "<p>Full article content here.</p>"}]

    # Configure .get() to return actual values
    def mock_get(key, default=""):
        values = {
            "title": "Test Article Title",
            "link": "https://example.com/article-123",
            "author": "Test Author",
        }
        return values.get(key, default)

    entry.get = mock_get

    return entry


@pytest.fixture
def mock_feed_minimal():
    """Create a mock RSS feed entry with minimal data."""
    entry = Mock()
    entry.title = "Minimal Entry"
    entry.link = "https://example.com/minimal"
    entry.summary = "Basic summary"

    # Configure .get() to return actual values
    def mock_get(key, default=""):
        values = {
            "title": "Minimal Entry",
            "link": "https://example.com/minimal",
        }
        return values.get(key, default)

    entry.get = mock_get

    # No author, published date, or content
    delattr(entry, "author")
    delattr(entry, "published_parsed")
    delattr(entry, "updated_parsed")
    delattr(entry, "content")

    return entry


@pytest.fixture
def mock_feed_old():
    """Create a mock RSS feed entry from 30 days ago."""
    entry = Mock()
    entry.title = "Old Article"
    entry.link = "https://example.com/old-article"

    # Published 30 days ago
    thirty_days_ago = datetime.now() - timedelta(days=30)
    entry.published_parsed = thirty_days_ago.timetuple()[:6]

    # Configure .get() to return actual values
    def mock_get(key, default=""):
        values = {
            "title": "Old Article",
            "link": "https://example.com/old-article",
        }
        return values.get(key, default)

    entry.get = mock_get

    return entry


@pytest.fixture
def mock_feedparser_response(mock_feed_entry):
    """Create a mock feedparser response object."""
    feed = Mock()
    feed.bozo = False  # No parsing errors
    feed.entries = [mock_feed_entry]
    feed.feed = {"title": "Test Feed"}
    return feed


# ============================================================================
# UNIT TESTS - Helper Functions
# ============================================================================


@pytest.mark.unit
class TestFetchFeed:
    """Tests for _fetch_feed helper function."""

    @patch("scrapers.rss_scraper.feedparser")
    def test_fetch_feed_success(self, mock_feedparser, mock_feedparser_response):
        """Test successful feed fetch and parse."""
        # Arrange
        mock_feedparser.parse.return_value = mock_feedparser_response
        feed_url = "https://example.com/feed.xml"

        # Act
        result = _fetch_feed(feed_url)

        # Assert
        mock_feedparser.parse.assert_called_once_with(feed_url)
        assert result == mock_feedparser_response
        assert len(result.entries) > 0

    @patch("scrapers.rss_scraper.feedparser")
    def test_fetch_feed_parsing_error(self, mock_feedparser):
        """Test handling of feed parsing errors."""
        # Arrange
        bad_feed = Mock()
        bad_feed.bozo = True  # Parsing error
        bad_feed.entries = []  # No entries
        mock_feedparser.parse.return_value = bad_feed

        # Act & Assert
        with pytest.raises(ValueError, match="Failed to parse feed"):
            _fetch_feed("https://example.com/bad-feed.xml")

    @patch("scrapers.rss_scraper.FEEDPARSER_AVAILABLE", False)
    def test_fetch_feed_no_feedparser(self):
        """Test error when feedparser is not installed."""
        # Act & Assert
        with pytest.raises(ImportError, match="feedparser library is required"):
            _fetch_feed("https://example.com/feed.xml")

    @patch("scrapers.rss_scraper.feedparser")
    def test_fetch_feed_with_entries_despite_bozo(self, mock_feedparser):
        """Test that feeds with bozo=True but valid entries still work."""
        # Arrange - Some feeds have minor issues but still have entries
        feed = Mock()
        feed.bozo = True  # Has parsing warnings
        feed.entries = [Mock()]  # But has valid entries
        mock_feedparser.parse.return_value = feed

        # Act
        result = _fetch_feed("https://example.com/feed.xml")

        # Assert
        assert result == feed
        assert len(result.entries) > 0


@pytest.mark.unit
class TestFilterEntriesByDate:
    """Tests for _filter_entries_by_date helper function."""

    def test_filter_recent_entries(self, mock_feed_entry):
        """Test filtering keeps recent entries (2 days old)."""
        # Arrange
        entries = [mock_feed_entry]
        days_back = 7

        # Act
        filtered = _filter_entries_by_date(entries, days_back)

        # Assert
        assert len(filtered) == 1
        assert filtered[0] == mock_feed_entry

    def test_filter_old_entries(self, mock_feed_old):
        """Test filtering removes old entries (30 days old with 7 day filter)."""
        # Arrange
        entries = [mock_feed_old]
        days_back = 7

        # Act
        filtered = _filter_entries_by_date(entries, days_back)

        # Assert
        assert len(filtered) == 0

    def test_filter_mixed_entries(self, mock_feed_entry, mock_feed_old):
        """Test filtering with mix of recent and old entries."""
        # Arrange
        entries = [mock_feed_entry, mock_feed_old]
        days_back = 7

        # Act
        filtered = _filter_entries_by_date(entries, days_back)

        # Assert
        assert len(filtered) == 1
        assert filtered[0] == mock_feed_entry

    def test_filter_entry_without_date(self):
        """Test entries without date are included (assumed recent)."""
        # Arrange
        entry_no_date = Mock()
        entry_no_date.title = "No Date Entry"
        delattr(entry_no_date, "published_parsed")
        delattr(entry_no_date, "updated_parsed")

        entries = [entry_no_date]
        days_back = 7

        # Act
        filtered = _filter_entries_by_date(entries, days_back)

        # Assert
        assert len(filtered) == 1  # Included because no date means "assume recent"

    def test_filter_uses_updated_date_fallback(self):
        """Test that updated_parsed is used if published_parsed is missing."""
        # Arrange
        entry = Mock()
        entry.title = "Updated Entry"
        delattr(entry, "published_parsed")

        # Updated 3 days ago
        three_days_ago = datetime.now() - timedelta(days=3)
        entry.updated_parsed = three_days_ago.timetuple()[:6]

        # Act
        filtered = _filter_entries_by_date([entry], days_back=7)

        # Assert
        assert len(filtered) == 1


@pytest.mark.unit
class TestFormatEntry:
    """Tests for _format_entry helper function."""

    def test_format_entry_complete_data(self, mock_feed_entry):
        """Test formatting entry with complete data."""
        # Arrange
        feed_title = "Test Feed"
        tags = ["python", "testing"]

        # Act
        result = _format_entry(mock_feed_entry, feed_title, tags)

        # Assert
        assert "---" in result  # YAML frontmatter
        assert "type: rss" in result
        assert "Test Article Title" in result
        assert "https://example.com/article-123" in result
        assert "Test Author" in result
        assert "Test Feed" in result
        assert "python, testing" in result
        assert "# Test Article Title" in result  # Markdown heading

    def test_format_entry_minimal_data(self, mock_feed_minimal):
        """Test formatting entry with minimal data."""
        # Arrange
        feed_title = "Minimal Feed"
        tags = []

        # Act
        result = _format_entry(mock_feed_minimal, feed_title, tags)

        # Assert
        assert "type: rss" in result
        assert "Minimal Entry" in result
        assert "https://example.com/minimal" in result
        assert "published: Unknown" in result  # No date
        assert "Basic summary" in result

    def test_format_entry_strips_html_from_content(self):
        """Test that HTML tags are removed from content."""
        # Arrange
        entry = Mock()
        entry.title = "HTML Test"
        entry.link = "https://example.com/html"
        entry.summary = (
            "<p>Text with <strong>HTML</strong> and <a href='#'>links</a>.</p>"
        )

        def mock_get(key, default=""):
            values = {
                "title": "HTML Test",
                "link": "https://example.com/html",
            }
            return values.get(key, default)

        entry.get = mock_get
        delattr(entry, "published_parsed")
        delattr(entry, "content")
        delattr(entry, "author")

        # Act
        result = _format_entry(entry, "Feed", [])

        # Assert
        assert "<p>" not in result
        assert "<strong>" not in result
        assert "<a href" not in result
        assert "Text with HTML and links." in result

    def test_format_entry_prefers_content_over_summary(self):
        """Test that entry.content is used if available instead of summary."""
        # Arrange
        entry = Mock()
        entry.title = "Content Test"
        entry.link = "https://example.com/content"
        entry.summary = "This is the summary"
        entry.content = [{"value": "This is the full content"}]

        def mock_get(key, default=""):
            values = {
                "title": "Content Test",
                "link": "https://example.com/content",
            }
            return values.get(key, default)

        entry.get = mock_get
        delattr(entry, "published_parsed")
        delattr(entry, "author")

        # Act
        result = _format_entry(entry, "Feed", [])

        # Assert
        assert "This is the full content" in result
        assert "This is the summary" not in result

    def test_format_entry_escapes_quotes_in_yaml(self):
        """Test that quotes in titles/authors are escaped for YAML."""
        # Arrange
        entry = Mock()
        entry.title = 'Article with "quotes" in title'
        entry.link = "https://example.com/quotes"
        entry.author = 'Author "Name"'
        entry.summary = "Content"

        def mock_get(key, default=""):
            values = {
                "title": 'Article with "quotes" in title',
                "link": "https://example.com/quotes",
                "author": 'Author "Name"',
            }
            return values.get(key, default)

        entry.get = mock_get
        delattr(entry, "published_parsed")
        delattr(entry, "content")

        # Act
        result = _format_entry(entry, "Feed", [])

        # Assert
        # Quotes should be replaced with right double quotation mark (curly quotes)
        assert "Article with “quotes“ in title" in result
        assert "Author “Name“" in result


# ============================================================================
# INTEGRATION TESTS - RSSScraper Plugin
# ============================================================================


@pytest.mark.integration
class TestRSSScraperInitialization:
    """Tests for RSSScraper initialization."""

    def test_rss_scraper_inherits_from_base(self):
        """Test that RSSScraper properly inherits from ScraperBase."""
        from scrapers.base import ScraperBase

        scraper = RSSScraper(verbose=False)

        assert isinstance(scraper, ScraperBase)

    def test_rss_scraper_initialization_default_verbose(self):
        """Test RSSScraper initializes with verbose=True by default."""
        scraper = RSSScraper()

        assert scraper.name == "RSS"
        assert scraper.verbose is True

    def test_rss_scraper_initialization_verbose_false(self):
        """Test RSSScraper initializes with verbose=False."""
        scraper = RSSScraper(verbose=False)

        assert scraper.name == "RSS"
        assert scraper.verbose is False


@pytest.mark.integration
class TestRSSScraperRun:
    """Tests for RSSScraper.run() integration."""

    @patch("scrapers.rss_scraper.FEEDPARSER_AVAILABLE", False)
    def test_run_without_feedparser_installed(self, tmp_path, capsys):
        """Test that scraper gracefully skips if feedparser not installed."""
        # Arrange
        scraper = RSSScraper(verbose=True)
        config = {"feeds": [{"url": "https://example.com/feed.xml"}]}

        # Act
        scraper.run(config, tmp_path)

        # Assert
        captured = capsys.readouterr()
        assert "feedparser' not installed" in captured.out

    @patch("scrapers.rss_scraper.FEEDPARSER_AVAILABLE", True)
    @patch("scrapers.rss_scraper._fetch_feed")
    def test_run_with_empty_feeds_list(self, mock_fetch, tmp_path):
        """Test run with empty feeds configuration."""
        # Arrange
        scraper = RSSScraper(verbose=False)
        config = {"feeds": []}

        # Act
        scraper.run(config, tmp_path)

        # Assert
        mock_fetch.assert_not_called()  # No feeds to fetch

    @patch("scrapers.rss_scraper.FEEDPARSER_AVAILABLE", True)
    @patch("scrapers.rss_scraper._fetch_feed")
    def test_run_fetches_and_saves_entries(
        self, mock_fetch, tmp_path, mock_feedparser_response, monkeypatch
    ):
        """Test complete workflow: fetch feed, filter, save files."""
        # Arrange
        scraper = RSSScraper(verbose=False)
        mock_fetch.return_value = mock_feedparser_response

        config = {
            "feeds": [
                {
                    "url": "https://example.com/feed.xml",
                    "name": "Test Feed",
                    "tags": ["test"],
                }
            ],
            "days_back": 7,
        }

        # Mock database to allow all items
        def mock_item_exists(source, unique_id):
            return False

        monkeypatch.setattr(database, "item_exists", mock_item_exists)

        # Track database additions
        added_items = []

        def mock_add_item(source, unique_id):
            added_items.append((source, unique_id))

        monkeypatch.setattr(database, "add_item", mock_add_item)

        # Act
        scraper.run(config, tmp_path)

        # Assert
        mock_fetch.assert_called_once_with("https://example.com/feed.xml")

        # Check files were created
        rss_dir = tmp_path / "rss"
        assert rss_dir.exists()

        files = list(rss_dir.glob("*.md"))
        assert len(files) == 1  # One entry in mock feed

        # Check database was updated
        assert len(added_items) == 1
        assert added_items[0][0] == "rss"

    @patch("scrapers.rss_scraper.FEEDPARSER_AVAILABLE", True)
    @patch("scrapers.rss_scraper._fetch_feed")
    def test_run_skips_entries_in_database(
        self, mock_fetch, tmp_path, mock_feedparser_response, monkeypatch
    ):
        """Test that entries already in database are skipped."""
        # Arrange
        scraper = RSSScraper(verbose=False)
        mock_fetch.return_value = mock_feedparser_response

        config = {
            "feeds": [{"url": "https://example.com/feed.xml"}],
            "days_back": 7,
        }

        # Mock database to say item exists
        def mock_item_exists(source, unique_id):
            return True  # All items already exist

        monkeypatch.setattr(database, "item_exists", mock_item_exists)

        added_items = []

        def mock_add_item(source, unique_id):
            added_items.append((source, unique_id))

        monkeypatch.setattr(database, "add_item", mock_add_item)

        # Act
        scraper.run(config, tmp_path)

        # Assert
        rss_dir = tmp_path / "rss"
        if rss_dir.exists():
            files = list(rss_dir.glob("*.md"))
            assert len(files) == 0  # No files created (all skipped)

        assert len(added_items) == 0  # Nothing added to database

    @patch("scrapers.rss_scraper.FEEDPARSER_AVAILABLE", True)
    @patch("scrapers.rss_scraper._fetch_feed")
    def test_run_handles_feed_errors_gracefully(self, mock_fetch, tmp_path, capsys):
        """Test that feed fetch errors are caught and logged."""
        # Arrange
        scraper = RSSScraper(verbose=True)
        mock_fetch.side_effect = ValueError("Feed parsing failed")

        config = {
            "feeds": [{"url": "https://example.com/bad-feed.xml"}],
            "days_back": 7,
        }

        # Act
        scraper.run(config, tmp_path)

        # Assert
        captured = capsys.readouterr()
        assert "Error processing feed" in captured.err
        # Should not crash, just continue

    @patch("scrapers.rss_scraper.FEEDPARSER_AVAILABLE", True)
    @patch("scrapers.rss_scraper._fetch_feed")
    def test_run_processes_multiple_feeds(
        self, mock_fetch, tmp_path, mock_feedparser_response, monkeypatch
    ):
        """Test processing multiple RSS feeds."""
        # Arrange
        scraper = RSSScraper(verbose=False)

        # Create different feeds with different entries
        feed1 = Mock()
        feed1.bozo = False
        feed1.entries = [mock_feedparser_response.entries[0]]
        feed1.feed = {"title": "Feed 1"}

        feed2 = Mock()
        feed2.bozo = False
        entry2 = Mock()
        entry2.title = "Second Entry"
        entry2.link = "https://example.com/entry-2"
        two_days_ago = datetime.now() - timedelta(days=2)
        entry2.published_parsed = two_days_ago.timetuple()[:6]
        entry2.summary = "Second entry content"
        delattr(entry2, "content")
        delattr(entry2, "author")

        # Configure .get() method for entry2
        def mock_get_entry2(key, default=""):
            values = {
                "title": "Second Entry",
                "link": "https://example.com/entry-2",
                "author": "Feed 2",
            }
            return values.get(key, default)

        entry2.get = mock_get_entry2
        feed2.entries = [entry2]
        feed2.feed = {"title": "Feed 2"}

        mock_fetch.side_effect = [feed1, feed2]

        config = {
            "feeds": [
                {"url": "https://example.com/feed1.xml"},
                {"url": "https://example.com/feed2.xml"},
            ],
            "days_back": 7,
        }

        monkeypatch.setattr(database, "item_exists", lambda s, i: False)
        monkeypatch.setattr(database, "add_item", lambda s, i: None)

        # Act
        scraper.run(config, tmp_path)

        # Assert
        assert mock_fetch.call_count == 2

        rss_dir = tmp_path / "rss"
        assert rss_dir.exists()

        files = list(rss_dir.glob("*.md"))
        assert len(files) == 2  # Two entries from two feeds

    @patch("scrapers.rss_scraper.FEEDPARSER_AVAILABLE", True)
    @patch("scrapers.rss_scraper._fetch_feed")
    def test_run_uses_custom_days_back(
        self, mock_fetch, tmp_path, mock_feed_old, monkeypatch
    ):
        """Test that custom days_back configuration is respected."""
        # Arrange
        scraper = RSSScraper(verbose=False)

        feed = Mock()
        feed.bozo = False
        feed.entries = [mock_feed_old]  # Entry from 30 days ago
        feed.feed = {"title": "Test Feed"}

        mock_fetch.return_value = feed

        # Config with days_back=7 (entry is 30 days old, should be filtered)
        config = {"feeds": [{"url": "https://example.com/feed.xml"}], "days_back": 7}

        monkeypatch.setattr(database, "item_exists", lambda s, i: False)

        # Act
        scraper.run(config, tmp_path)

        # Assert
        rss_dir = tmp_path / "rss"
        if rss_dir.exists():
            files = list(rss_dir.glob("*.md"))
            assert len(files) == 0  # Old entry filtered out

    @patch("scrapers.rss_scraper.FEEDPARSER_AVAILABLE", True)
    @patch("scrapers.rss_scraper._fetch_feed")
    def test_run_skips_entries_without_links(self, mock_fetch, tmp_path, monkeypatch):
        """Test that entries without links are skipped."""
        # Arrange
        scraper = RSSScraper(verbose=False)

        entry_no_link = Mock()
        entry_no_link.title = "No Link Entry"
        entry_no_link.link = ""  # Empty link
        two_days_ago = datetime.now() - timedelta(days=2)
        entry_no_link.published_parsed = two_days_ago.timetuple()[:6]

        feed = Mock()
        feed.bozo = False
        feed.entries = [entry_no_link]
        feed.feed = {"title": "Test Feed"}

        mock_fetch.return_value = feed

        config = {"feeds": [{"url": "https://example.com/feed.xml"}], "days_back": 7}

        monkeypatch.setattr(database, "item_exists", lambda s, i: False)

        # Act
        scraper.run(config, tmp_path)

        # Assert
        rss_dir = tmp_path / "rss"
        if rss_dir.exists():
            files = list(rss_dir.glob("*.md"))
            assert len(files) == 0  # No link = skipped


# ============================================================================
# EDGE CASES & ERROR HANDLING
# ============================================================================


@pytest.mark.unit
class TestRSSScraperEdgeCases:
    """Tests for edge cases and error conditions."""

    @patch("scrapers.rss_scraper.FEEDPARSER_AVAILABLE", True)
    @patch("scrapers.rss_scraper._fetch_feed")
    def test_run_with_feed_missing_url(self, mock_fetch, tmp_path):
        """Test that feeds without URL are skipped."""
        # Arrange
        scraper = RSSScraper(verbose=False)
        config = {
            "feeds": [{"name": "Feed without URL", "tags": ["test"]}]  # No 'url' key
        }

        # Act
        scraper.run(config, tmp_path)

        # Assert
        mock_fetch.assert_not_called()  # Feed skipped

    def test_filter_entries_with_empty_list(self):
        """Test filtering empty entries list."""
        # Act
        result = _filter_entries_by_date([], days_back=7)

        # Assert
        assert result == []

    def test_format_entry_with_none_values(self):
        """Test formatting handles None values gracefully."""
        # Arrange
        entry = Mock()

        def mock_get(key, default=""):
            return default  # Return default for all keys

        entry.get = mock_get
        delattr(entry, "published_parsed")
        delattr(entry, "content")
        entry.summary = ""  # Empty summary

        # Act
        result = _format_entry(entry, "", [])

        # Assert
        assert "type: rss" in result  # Basic structure still there
        assert "Untitled" in result  # Default title
