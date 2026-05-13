#!/usr/bin/env python3
"""Unit tests for db_init.py."""

import sqlite3
from pathlib import Path

import pytest
import yaml


def _write_config(tmp_path: Path, topics: dict | None = None) -> Path:
    """Write a minimal research_config.yaml with optional topics."""
    cfg: dict = {}
    if topics is not None:
        cfg["topics"] = topics
    p = tmp_path / "research_config.yaml"
    p.write_text(yaml.dump(cfg))
    return p


@pytest.mark.unit
class TestInitTopicsAndKeywords:
    """Tests for init_topics_and_keywords()."""

    def test_creates_topics_and_keywords_in_db(self, tmp_path):
        from rdt.shared.db_init import init_topics_and_keywords

        config_path = _write_config(
            tmp_path, topics={"AI": ["machine learning", "llm"]}
        )
        db_path = str(tmp_path / "test.db")

        init_topics_and_keywords(str(config_path), db_path)

        conn = sqlite3.connect(db_path)
        topics = conn.execute("SELECT name FROM topics").fetchall()
        keywords = conn.execute("SELECT keyword FROM keywords").fetchall()
        conn.close()

        assert ("AI",) in topics
        assert ("machine learning",) in keywords
        assert ("llm",) in keywords

    def test_handles_empty_topics_config(self, tmp_path, capsys):
        from rdt.shared.db_init import init_topics_and_keywords

        config_path = _write_config(tmp_path, topics={})
        db_path = str(tmp_path / "test.db")

        init_topics_and_keywords(str(config_path), db_path)
        # Should not raise — prints warning about no topics

    def test_handles_missing_topics_key(self, tmp_path):
        from rdt.shared.db_init import init_topics_and_keywords

        config_path = _write_config(tmp_path, topics=None)  # no topics key
        db_path = str(tmp_path / "test.db")

        init_topics_and_keywords(str(config_path), db_path)
        # Should not raise

    def test_invalid_config_file_raises_exit(self, tmp_path):
        """Non-existent config file raises click Exit (typer.Exit wraps click)."""
        import click

        from rdt.shared.db_init import init_topics_and_keywords

        with pytest.raises((click.exceptions.Exit, SystemExit)):
            init_topics_and_keywords("/nonexistent/config.yaml", str(tmp_path / "db"))

    def test_idempotent_insert(self, tmp_path):
        """Calling twice with same data doesn't raise."""
        from rdt.shared.db_init import init_topics_and_keywords

        config_path = _write_config(tmp_path, topics={"AI": ["ml"]})
        db_path = str(tmp_path / "test.db")

        init_topics_and_keywords(str(config_path), db_path)
        init_topics_and_keywords(str(config_path), db_path)  # second call — no error

        conn = sqlite3.connect(db_path)
        count = conn.execute("SELECT COUNT(*) FROM topics").fetchone()[0]
        conn.close()
        assert count == 1  # Only one "AI" topic despite two inserts
