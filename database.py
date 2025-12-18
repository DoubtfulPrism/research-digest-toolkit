#!/usr/bin/env python3
"""Database management for the Research Digest Toolkit.

Handles a persistent SQLite database to track processed items and avoid duplicates.
"""

import sqlite3
import sys
from datetime import datetime
from pathlib import Path

# Database file will be created in the script's directory
DB_PATH = Path(__file__).parent / "research_digest_state.db"


def get_connection():
    """Establishes a connection to the SQLite database."""
    con = sqlite3.connect(DB_PATH, check_same_thread=False)
    return con


def init_db():
    """Initializes the database and creates the 'processed_items' table.

    The table is only created if it doesn't already exist.
    """
    try:
        con = get_connection()
        cur = con.cursor()

        # Create table with a composite primary key for efficiency
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS processed_items (
                source TEXT NOT NULL,
                unique_id TEXT NOT NULL,
                processed_at TIMESTAMP NOT NULL,
                PRIMARY KEY (source, unique_id)
            )
        """
        )

        con.commit()
        con.close()
    except sqlite3.Error as e:
        print(f"Database error during initialization: {e}", file=sys.stderr)


def item_exists(source: str, unique_id: str) -> bool:
    """Checks if an item with the given source and unique_id already exists.

    Args:
        source: The source of the content (e.g., 'hn', 'rss', 'reddit').
        unique_id: The unique identifier for the item (e.g., URL or item ID).

    Returns:
        True if the item exists, False otherwise.
    """
    try:
        con = get_connection()
        cur = con.cursor()

        cur.execute(
            "SELECT 1 FROM processed_items WHERE source = ? AND unique_id = ?",
            (source, unique_id),
        )

        exists = cur.fetchone() is not None
        con.close()
        return exists
    except sqlite3.Error as e:
        print(f"Database error checking item: {e}", file=sys.stderr)
        return False  # Fail safe: assume it doesn't exist


def add_item(source: str, unique_id: str):
    """Adds a new processed item to the database.

    Args:
        source: The source of the content (e.g., 'hn', 'rss', 'reddit').
        unique_id: The unique identifier for the item (e.g., URL or item ID).
    """
    try:
        con = get_connection()
        cur = con.cursor()

        cur.execute(
            "INSERT OR IGNORE INTO processed_items (source, unique_id, processed_at) VALUES (?, ?, ?)",
            (source, unique_id, datetime.now()),
        )

        con.commit()
        con.close()
    except sqlite3.Error as e:
        print(f"Database error adding item: {e}", file=sys.stderr)


# Initialize the database when this module is first imported
init_db()
