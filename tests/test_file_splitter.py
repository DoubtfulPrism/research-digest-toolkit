#!/usr/bin/env python3
"""
Unit tests for file_splitter.py.
"""

import os
import sys
from pathlib import Path

import pytest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from file_splitter import (
    DEFAULT_MAX_CHARS,
    is_text_file,
    process_directory,
    process_files,
    split_file_by_lines,
    split_file_by_words,
)

# --- Fixtures ---


@pytest.fixture
def sample_text_file(tmp_path):
    file_path = tmp_path / "test.txt"
    file_path.write_text("This is a sample text file.")
    return file_path


@pytest.fixture
def sample_long_text_file(tmp_path):
    file_path = tmp_path / "long_test.txt"
    file_path.write_text(("This is a long sample text file." * 1000 + "\n") * 10)
    return file_path


# --- Tests ---


def test_is_text_file():
    assert is_text_file("test.txt") is True
    assert is_text_file("test.md") is True
    assert is_text_file("test.json") is True
    assert is_text_file("test.py") is True
    assert is_text_file("test.unknown") is False
    assert is_text_file("test.unknown", check_extensions=False) is True


def test_split_file_by_words(sample_long_text_file, tmp_path):
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    chunks = split_file_by_words(
        str(sample_long_text_file), str(output_dir), max_chars=10000
    )
    assert chunks > 1


def test_split_file_by_lines(sample_long_text_file, tmp_path):
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    chunks = split_file_by_lines(
        str(sample_long_text_file), str(output_dir), max_chars=10000
    )
    assert chunks > 1


def test_process_files(sample_text_file, tmp_path):
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    stats = process_files([str(sample_text_file)], str(output_dir))
    assert stats["processed"] == 1
    assert stats["chunks_created"] == 1


def test_process_directory(sample_text_file, tmp_path):
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    stats = process_directory(str(tmp_path), str(output_dir))
    assert stats["processed"] == 1
    assert stats["chunks_created"] == 1
