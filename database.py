#!/usr/bin/env python3
"""Database management for the Research Digest Toolkit.

Handles a persistent SQLite database to track processed items and avoid duplicates.

Note: For Python 3.12+ compatibility, all datetime values are stored as
ISO 8601 formatted strings (YYYY-MM-DD HH:MM:SS.ffffff) to avoid the
deprecated datetime adapter.
"""

import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

# Database file will be created in the script's directory
DB_PATH = Path(__file__).parent / "research_digest_state.db"


def _get_current_timestamp() -> str:
    """Get current UTC timestamp in ISO 8601 format.

    Returns:
        ISO 8601 formatted timestamp string (e.g., '2026-01-09T12:34:56.789012').

    Note:
        This is the Python 3.12+ compatible way to store timestamps in SQLite.
        The timestamp is stored as a TEXT field in ISO 8601 format.
    """
    return datetime.now(timezone.utc).isoformat()


def get_connection(db_path: str = None):
    """Establishes a connection to the SQLite database."""
    if db_path is None:
        db_path = str(DB_PATH)
    try:
        # isolation_level=None enables autocommit mode
        return sqlite3.connect(db_path, isolation_level=None)
    except sqlite3.Error as e:
        print(f"Database connection error: {e}", file=sys.stderr)
        return None


def init_db(db_path: str = None):
    """Initializes the database and creates tables if they don't exist.

    Note:
        processed_at is stored as TEXT in ISO 8601 format for Python 3.12+ compatibility.
        CURRENT_TIMESTAMP in SQLite already returns ISO 8601 format (TEXT).
    """
    if db_path is None:
        db_path = str(DB_PATH)
    schema = """
    CREATE TABLE IF NOT EXISTS processed_items (
        source TEXT NOT NULL,
        unique_id TEXT NOT NULL,
        processed_at TEXT DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (source, unique_id)
    );
    CREATE TABLE IF NOT EXISTS topics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE
    );
    CREATE TABLE IF NOT EXISTS keywords (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        topic_id INTEGER NOT NULL,
        keyword TEXT NOT NULL UNIQUE,
        FOREIGN KEY (topic_id) REFERENCES topics (id)
    );
    CREATE TABLE IF NOT EXISTS topic_occurrences (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_id TEXT NOT NULL,
        source TEXT NOT NULL,
        topic_id INTEGER NOT NULL,
        date DATETIME NOT NULL,
        FOREIGN KEY (topic_id) REFERENCES topics (id)
    );
    """
    conn = get_connection(db_path)
    if conn is None:
        return
    try:
        conn.executescript(schema)
    finally:
        conn.close()


def item_exists(source: str, unique_id: str, db_path: str = None) -> bool:
    """Checks if an item with the given source and unique_id already exists.

    Args:
        source: The source of the content (e.g., 'hn', 'rss', 'reddit').
        unique_id: The unique identifier for the item (e.g., URL or item ID).
        db_path: Optional path to database file.

    Returns:
        True if the item exists, False otherwise.
    """
    ensure_initialized(db_path)  # Lazy initialization

    try:
        con = get_connection(db_path)
        if con is None:
            return False

        try:
            cur = con.cursor()
            cur.execute(
                "SELECT 1 FROM processed_items WHERE source = ? AND unique_id = ?",
                (source, unique_id),
            )
            exists = cur.fetchone() is not None
            return exists
        finally:
            con.close()
    except sqlite3.Error as e:
        print(f"Database error checking item: {e}", file=sys.stderr)
        return False  # Fail safe: assume it doesn't exist


def add_item(source: str, unique_id: str, db_path: str = None):
    """Adds a new processed item to the database.

    Args:
        source: The source of the content (e.g., 'hn', 'rss', 'reddit').
        unique_id: The unique identifier for the item (e.g., URL or item ID).
        db_path: Optional path to database file.

    Note:
        Timestamp is stored as ISO 8601 TEXT format for Python 3.12+ compatibility.
    """
    ensure_initialized(db_path)  # Lazy initialization

    try:
        con = get_connection(db_path)
        if con is None:
            return

        try:
            cur = con.cursor()
            # Use ISO format string instead of datetime object (Python 3.12+ compatible)
            cur.execute(
                "INSERT OR IGNORE INTO processed_items (source, unique_id, processed_at) VALUES (?, ?, ?)",
                (source, unique_id, _get_current_timestamp()),
            )
            con.commit()
        finally:
            con.close()
    except sqlite3.Error as e:
        print(f"Database error adding item: {e}", file=sys.stderr)


# Module-level flag to track initialization
_db_initialized = False


def ensure_initialized(db_path: str = None):
    """Ensure database is initialized (lazy initialization).

    This is called automatically by item_exists() and add_item() on first use.
    Thread-safe for single-threaded applications (GIL protection).

    Args:
        db_path: Optional path to database file.
    """
    global _db_initialized
    if not _db_initialized:
        init_db(db_path)
        _db_initialized = True
