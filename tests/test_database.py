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

    # Initialize the database with the new path
    database.init_db()

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

        # Insert first item
        cur.execute(
            "INSERT INTO processed_items (source, unique_id, processed_at) VALUES (?, ?, ?)",
            ("hn", "item123", datetime.now()),
        )
        con.commit()

        # Try to insert duplicate - should fail or be ignored
        with pytest.raises(sqlite3.IntegrityError):
            cur.execute(
                "INSERT INTO processed_items (source, unique_id, processed_at) VALUES (?, ?, ?)",
                ("hn", "item123", datetime.now()),
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

        # Simulate a database error by breaking the connection
        def broken_connection():
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
        con = database.get_connection()
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
        database.add_item("hn", "duplicate123")
        database.add_item("hn", "duplicate123")

        # Should still only exist once
        con = database.get_connection()
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
        con = database.get_connection()
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
        con = database.get_connection()
        cur = con.cursor()
        cur.execute("SELECT COUNT(*) FROM processed_items WHERE source = ?", ("hn",))
        count = cur.fetchone()[0]
        con.close()

        assert count == 100

        # Verify a sample exists
        assert database.item_exists("hn", "item_50") is True


@pytest.mark.unit
class TestGetConnection:
    """Tests for get_connection function."""

    def test_get_connection_returns_connection(self, temp_db):
        """Test that get_connection returns a valid SQLite connection."""
        con = database.get_connection()

        assert isinstance(con, sqlite3.Connection)

        # Test that we can execute a query
        cur = con.cursor()
        cur.execute("SELECT 1")
        result = cur.fetchone()
        con.close()

        assert result[0] == 1
