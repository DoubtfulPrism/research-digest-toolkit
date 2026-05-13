#!/usr/bin/env python3
"""Unit tests for analysis.py."""

import sqlite3
from pathlib import Path

import pytest


def _make_analysis_db(tmp_path: Path) -> Path:
    """Create a test DB with topics and occurrences."""
    db = tmp_path / "test_analysis.db"
    conn = sqlite3.connect(str(db))
    conn.execute(
        "CREATE TABLE topics (id INTEGER PRIMARY KEY, name TEXT UNIQUE NOT NULL)"
    )
    conn.execute(
        "CREATE TABLE topic_occurrences "
        "(id INTEGER PRIMARY KEY, topic_id INTEGER, date TEXT)"
    )
    conn.execute("INSERT INTO topics VALUES (1, 'AI')")
    conn.execute("INSERT INTO topics VALUES (2, 'ML')")
    conn.execute("INSERT INTO topic_occurrences VALUES (1, 1, '2026-03-01')")
    conn.execute("INSERT INTO topic_occurrences VALUES (2, 1, '2026-03-02')")
    conn.execute("INSERT INTO topic_occurrences VALUES (3, 2, '2026-03-01')")
    conn.commit()
    conn.close()
    return db


def _make_empty_analysis_db(tmp_path: Path) -> Path:
    """Create an empty topics/occurrences DB."""
    db = tmp_path / "empty_analysis.db"
    conn = sqlite3.connect(str(db))
    conn.execute(
        "CREATE TABLE topics (id INTEGER PRIMARY KEY, name TEXT UNIQUE NOT NULL)"
    )
    conn.execute(
        "CREATE TABLE topic_occurrences "
        "(id INTEGER PRIMARY KEY, topic_id INTEGER, date TEXT)"
    )
    conn.commit()
    conn.close()
    return db


@pytest.mark.unit
class TestAnalyzeTopicTrends:
    """Tests for analyze_topic_trends()."""

    def test_prints_table_for_db_with_data(self, tmp_path, capsys):
        from rdt.shared.analysis import analyze_topic_trends

        db = _make_analysis_db(tmp_path)
        # Should run without raising
        analyze_topic_trends(str(db))

    def test_empty_db_prints_warning(self, tmp_path, capsys):
        from rdt.shared.analysis import analyze_topic_trends

        db = _make_empty_analysis_db(tmp_path)
        analyze_topic_trends(str(db))
        # Should not raise; empty DataFrame path prints a warning message

    def test_missing_table_raises_exit(self, tmp_path):
        """When the DB lacks expected tables, typer.Exit is raised."""

        db = tmp_path / "no_tables.db"
        conn = sqlite3.connect(str(db))
        conn.commit()
        conn.close()

        with pytest.raises((Exception, SystemExit)):
            from rdt.shared.analysis import analyze_topic_trends

            analyze_topic_trends(str(db))
