#!/usr/bin/env python3
"""
Tests for database.py - State tracking and deduplication logic.
"""

import sqlite3
import sys
import tempfile
from datetime import datetime
from pathlib import Path

import pytest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import database


@pytest.fixture
def temp_db(monkeypatch):
    """
    Fixture that creates a temporary database for testing.
    Patches the DB_PATH to use a temporary file.
    """
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        temp_db_path = Path(tmp.name)

    # Patch the database module's DB_PATH
    monkeypatch.setattr(database, "DB_PATH", temp_db_path)

    # Reset initialization flag for each test
    monkeypatch.setattr(database, "_db_initialized", False)

    # Initialize the database with the new path
    database.init_db(str(temp_db_path))

    yield temp_db_path

    # Cleanup
    if temp_db_path.exists():
        temp_db_path.unlink()


@pytest.mark.unit
@pytest.mark.database
class TestDatabaseInit:
    """Tests for database initialization."""

    def test_init_db_creates_table(self, temp_db):
        """Test that init_db creates the processed_items table."""
        con = sqlite3.connect(temp_db)
        cur = con.cursor()

        # Check if table exists
        cur.execute(
            """
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='processed_items'
        """
        )

        result = cur.fetchone()
        con.close()

        assert result is not None
        assert result[0] == "processed_items"

    def test_table_schema(self, temp_db):
        """Test that the table has the correct schema."""
        con = sqlite3.connect(temp_db)
        cur = con.cursor()

        # Get table info
        cur.execute("PRAGMA table_info(processed_items)")
        columns = cur.fetchall()
        con.close()

        # Extract column names
        column_names = [col[1] for col in columns]

        assert "source" in column_names
        assert "unique_id" in column_names
        assert "processed_at" in column_names

    def test_composite_primary_key(self, temp_db):
        """Test that the composite primary key prevents duplicates."""
        con = sqlite3.connect(temp_db)
        cur = con.cursor()

        # Use ISO format timestamp (Python 3.12+ compatible)
        timestamp = datetime.now().isoformat()

        # Insert first item
        cur.execute(
            "INSERT INTO processed_items (source, unique_id, processed_at) VALUES (?, ?, ?)",
            ("hn", "item123", timestamp),
        )
        con.commit()

        # Try to insert duplicate - should fail or be ignored
        with pytest.raises(sqlite3.IntegrityError):
            cur.execute(
                "INSERT INTO processed_items (source, unique_id, processed_at) VALUES (?, ?, ?)",
                ("hn", "item123", timestamp),
            )
            con.commit()

        con.close()


@pytest.mark.unit
@pytest.mark.database
class TestItemExists:
    """Tests for item_exists function."""

    def test_item_exists_returns_false_for_new_item(self, temp_db):
        """Test that item_exists returns False for a new item."""
        exists = database.item_exists("hn", "new_item_123")
        assert exists is False

    def test_item_exists_returns_true_for_existing_item(self, temp_db):
        """Test that item_exists returns True for an existing item."""
        # Add an item
        database.add_item("reddit", "post456")

        # Check if it exists
        exists = database.item_exists("reddit", "post456")
        assert exists is True

    def test_item_exists_differentiates_sources(self, temp_db):
        """Test that item_exists differentiates between sources."""
        # Add item to one source
        database.add_item("hn", "item789")

        # Check that it exists for that source
        assert database.item_exists("hn", "item789") is True

        # Check that it doesn't exist for a different source
        assert database.item_exists("reddit", "item789") is False

    def test_item_exists_handles_database_errors_gracefully(self, temp_db, monkeypatch):
        """Test that item_exists returns False on database errors."""

        # Database already initialized by fixture, so skip initialization
        monkeypatch.setattr(database, "_db_initialized", True)

        # Simulate a database error by breaking the connection
        def broken_connection(db_path=None):
            raise sqlite3.Error("Simulated database error")

        monkeypatch.setattr(database, "get_connection", broken_connection)

        # Should return False (fail-safe behavior)
        exists = database.item_exists("hn", "item999")
        assert exists is False


@pytest.mark.unit
@pytest.mark.database
class TestAddItem:
    """Tests for add_item function."""

    def test_add_item_inserts_new_item(self, temp_db):
        """Test that add_item successfully inserts a new item."""
        # Add item
        database.add_item("arxiv", "paper123")

        # Verify it was added
        assert database.item_exists("arxiv", "paper123") is True

    def test_add_item_sets_timestamp(self, temp_db):
        """Test that add_item sets a processed_at timestamp."""
        # Add item
        database.add_item("rss", "article456")

        # Query the timestamp
        con = database.get_connection(str(temp_db))
        cur = con.cursor()
        cur.execute(
            "SELECT processed_at FROM processed_items WHERE source = ? AND unique_id = ?",
            ("rss", "article456"),
        )
        result = cur.fetchone()
        con.close()

        assert result is not None
        assert result[0] is not None

    def test_add_item_ignores_duplicates(self, temp_db):
        """Test that add_item handles duplicate inserts gracefully (INSERT OR IGNORE)."""
        # Add item twice
        database.add_item("hn", "duplicate123", str(temp_db))
        database.add_item("hn", "duplicate123", str(temp_db))

        # Should still only exist once
        con = database.get_connection(str(temp_db))
        cur = con.cursor()
        cur.execute(
            "SELECT COUNT(*) FROM processed_items WHERE source = ? AND unique_id = ?",
            ("hn", "duplicate123"),
        )
        count = cur.fetchone()[0]
        con.close()

        assert count == 1

    def test_add_item_handles_special_characters(self, temp_db):
        """Test that add_item handles URLs and special characters."""
        special_url = "https://example.com/article?id=123&param=value#section"

        database.add_item("rss", special_url)

        assert database.item_exists("rss", special_url) is True


@pytest.mark.integration
@pytest.mark.database
class TestDatabaseWorkflow:
    """Integration tests for typical database workflows."""

    def test_complete_deduplication_workflow(self, temp_db):
        """Test a complete workflow of checking, adding, and verifying items."""
        items = [
            ("hn", "item1"),
            ("hn", "item2"),
            ("reddit", "post1"),
            ("rss", "article1"),
        ]

        # Check that none exist initially
        for source, unique_id in items:
            assert database.item_exists(source, unique_id) is False

        # Add all items
        for source, unique_id in items:
            database.add_item(source, unique_id)

        # Verify all exist now
        for source, unique_id in items:
            assert database.item_exists(source, unique_id) is True

    def test_multi_source_deduplication(self, temp_db):
        """Test that the same ID in different sources is tracked separately."""
        shared_id = "12345"

        # Add to multiple sources
        database.add_item("hn", shared_id)
        database.add_item("reddit", shared_id)
        database.add_item("rss", shared_id)

        # All should exist independently
        assert database.item_exists("hn", shared_id) is True
        assert database.item_exists("reddit", shared_id) is True
        assert database.item_exists("rss", shared_id) is True

        # Count total items
        con = database.get_connection(str(temp_db))
        cur = con.cursor()
        cur.execute(
            "SELECT COUNT(*) FROM processed_items WHERE unique_id = ?", (shared_id,)
        )
        count = cur.fetchone()[0]
        con.close()

        assert count == 3

    def test_large_batch_processing(self, temp_db):
        """Test handling a large batch of items."""
        # Add 100 items
        for i in range(100):
            database.add_item("hn", f"item_{i}")

        # Verify count
        con = database.get_connection(str(temp_db))
        cur = con.cursor()
        cur.execute("SELECT COUNT(*) FROM processed_items WHERE source = ?", ("hn",))
        count = cur.fetchone()[0]
        con.close()

        assert count == 100

        # Verify a sample exists
        assert database.item_exists("hn", "item_50") is True


@pytest.mark.unit
@pytest.mark.database
class TestSchemaExtension:
    """Tests for title/url schema extension."""

    def test_processed_items_has_title_column(self, temp_db):
        """processed_items table has a title column after migration."""
        con = sqlite3.connect(str(temp_db))
        cur = con.cursor()
        cur.execute("PRAGMA table_info(processed_items)")
        columns = {col[1] for col in cur.fetchall()}
        con.close()
        assert "title" in columns

    def test_processed_items_has_url_column(self, temp_db):
        """processed_items table has a url column after migration."""
        con = sqlite3.connect(str(temp_db))
        cur = con.cursor()
        cur.execute("PRAGMA table_info(processed_items)")
        columns = {col[1] for col in cur.fetchall()}
        con.close()
        assert "url" in columns

    def test_add_item_stores_title_and_url(self, temp_db):
        """add_item() with title/url stores them in the database."""
        database.add_item(
            "hn",
            "item_with_meta",
            title="My Article",
            url="https://example.com/my-article",
        )

        con = sqlite3.connect(str(temp_db))
        cur = con.cursor()
        cur.execute(
            "SELECT title, url FROM processed_items WHERE source = ? AND unique_id = ?",
            ("hn", "item_with_meta"),
        )
        row = cur.fetchone()
        con.close()

        assert row is not None
        assert row[0] == "My Article"
        assert row[1] == "https://example.com/my-article"

    def test_add_item_without_title_url_stores_null(self, temp_db):
        """add_item() without title/url stores NULL — backward compatible."""
        database.add_item("rss", "item_no_meta")

        con = sqlite3.connect(str(temp_db))
        cur = con.cursor()
        cur.execute(
            "SELECT title, url FROM processed_items WHERE source = ? AND unique_id = ?",
            ("rss", "item_no_meta"),
        )
        row = cur.fetchone()
        con.close()

        assert row is not None
        assert row[0] is None
        assert row[1] is None


@pytest.mark.unit
@pytest.mark.database
class TestGetItems:
    """Tests for the get_items() function."""

    def test_get_items_returns_all_items(self, temp_db):
        """get_items() returns all items when source is None."""
        database.add_item("hn", "item1", title="Article One")
        database.add_item("rss", "item2", title="Article Two")

        items = database.get_items(db_path=str(temp_db))

        assert len(items) == 2

    def test_get_items_filters_by_source(self, temp_db):
        """get_items(source='hn') returns only HN items."""
        database.add_item("hn", "hn_item1")
        database.add_item("hn", "hn_item2")
        database.add_item("rss", "rss_item1")

        items = database.get_items(source="hn", db_path=str(temp_db))

        assert len(items) == 2
        assert all(item["source"] == "hn" for item in items)

    def test_get_items_respects_limit(self, temp_db):
        """get_items(limit=2) returns at most 2 items."""
        for i in range(5):
            database.add_item("hn", f"item_{i}")

        items = database.get_items(limit=2, db_path=str(temp_db))

        assert len(items) == 2

    def test_get_items_includes_title_url(self, temp_db):
        """get_items() includes title and url fields."""
        database.add_item(
            "hn", "item_with_meta", title="My Title", url="https://example.com"
        )

        items = database.get_items(db_path=str(temp_db))

        assert len(items) == 1
        assert items[0]["title"] == "My Title"
        assert items[0]["url"] == "https://example.com"

    def test_get_items_returns_empty_list_when_db_empty(self, temp_db):
        """get_items() returns empty list when database is empty."""
        items = database.get_items(db_path=str(temp_db))
        assert items == []


@pytest.mark.unit
@pytest.mark.database
class TestGetItemCounts:
    """Tests for get_item_counts() function."""

    def test_get_item_counts_returns_counts_per_source(self, temp_db):
        """get_item_counts() returns correct counts per source."""
        database.add_item("hn", "hn1")
        database.add_item("hn", "hn2")
        database.add_item("rss", "rss1")

        counts = database.get_item_counts(db_path=str(temp_db))

        assert counts.get("hn") == 2
        assert counts.get("rss") == 1

    def test_get_item_counts_returns_empty_dict_for_empty_db(self, temp_db):
        """get_item_counts() returns empty dict when database is empty."""
        counts = database.get_item_counts(db_path=str(temp_db))
        assert counts == {}


@pytest.mark.unit
class TestGetConnection:
    """Tests for get_connection function."""

    def test_get_connection_returns_connection(self, temp_db):
        """Test that get_connection returns a valid SQLite connection."""
        con = database.get_connection(str(temp_db))

        assert isinstance(con, sqlite3.Connection)

        # Test that we can execute a query
        cur = con.cursor()
        cur.execute("SELECT 1")
        result = cur.fetchone()
        con.close()

        assert result[0] == 1


@pytest.mark.unit
@pytest.mark.database
class TestDatetimeHandling:
    """Tests for Python 3.12+ compatible datetime handling."""

    def test_get_current_timestamp_returns_iso_format(self):
        """Test that _get_current_timestamp returns ISO 8601 format."""
        timestamp = database._get_current_timestamp()

        # Should be a string
        assert isinstance(timestamp, str)

        # Should be parseable as ISO format datetime
        from datetime import datetime

        parsed = datetime.fromisoformat(timestamp)
        assert isinstance(parsed, datetime)

        # Should contain timezone info (UTC)
        assert parsed.tzinfo is not None

    def test_add_item_stores_timestamp_as_text(self, temp_db):
        """Test that timestamps are stored as TEXT in ISO format (Python 3.12+)."""
        # Add an item
        database.add_item("test_source", "test_id_123", str(temp_db))

        # Query the database directly
        con = sqlite3.connect(str(temp_db))
        cur = con.cursor()
        cur.execute(
            "SELECT processed_at FROM processed_items WHERE source = ? AND unique_id = ?",
            ("test_source", "test_id_123"),
        )
        result = cur.fetchone()
        con.close()

        assert result is not None
        timestamp = result[0]

        # Should be a string (TEXT type in SQLite)
        assert isinstance(timestamp, str)

        # Should be parseable as ISO format
        from datetime import datetime

        parsed = datetime.fromisoformat(timestamp)
        assert isinstance(parsed, datetime)

    def test_timestamp_column_type_is_text(self, temp_db):
        """Test that processed_at column is TEXT type (not DATETIME)."""
        con = sqlite3.connect(str(temp_db))
        cur = con.cursor()

        # Get table schema
        cur.execute("PRAGMA table_info(processed_items)")
        columns = cur.fetchall()
        con.close()

        # Find processed_at column
        processed_at_col = [col for col in columns if col[1] == "processed_at"]
        assert len(processed_at_col) == 1

        # Column type should be TEXT (Python 3.12+ compatible)
        col_type = processed_at_col[0][2]
        assert col_type == "TEXT", f"Expected TEXT, got {col_type}"

    def test_no_datetime_deprecation_warning(self, temp_db):
        """Test that no DeprecationWarning is raised for datetime adapter."""
        import warnings

        # Catch all warnings
        with warnings.catch_warnings(record=True) as warning_list:
            warnings.simplefilter("always", DeprecationWarning)

            # Perform database operations
            database.add_item("test", "id1", str(temp_db))
            database.item_exists("test", "id1", str(temp_db))

            # Check that no datetime adapter deprecation warnings were raised
            datetime_warnings = [
                w
                for w in warning_list
                if issubclass(w.category, DeprecationWarning)
                and "datetime adapter" in str(w.message).lower()
            ]

            assert len(datetime_warnings) == 0, (
                f"Found {len(datetime_warnings)} datetime deprecation warnings: "
                f"{[str(w.message) for w in datetime_warnings]}"
            )
