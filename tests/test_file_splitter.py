#!/usr/bin/env python3
"""
Unit tests for file_splitter.py.
"""

import sys
from pathlib import Path

import pytest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from file_splitter import (
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


def test_split_file_by_words_empty_file(tmp_path):
    """Empty file returns 0 chunks."""
    empty_file = tmp_path / "empty.txt"
    empty_file.write_text("")
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    chunks = split_file_by_words(str(empty_file), str(output_dir))
    assert chunks == 0


def test_split_file_by_words_unicode_error(tmp_path):
    """UnicodeDecodeError returns 0 chunks."""
    from unittest.mock import mock_open, patch

    output_dir = tmp_path / "output"
    output_dir.mkdir()
    with patch("builtins.open", mock_open()) as m:
        m.side_effect = UnicodeDecodeError("utf-8", b"", 0, 1, "reason")
        chunks = split_file_by_words(str(tmp_path / "fake.txt"), str(output_dir))
    assert chunks == 0


def test_split_file_by_words_ioerror(tmp_path):
    """IOError returns 0 chunks."""
    from unittest.mock import mock_open, patch

    output_dir = tmp_path / "output"
    output_dir.mkdir()
    with patch("builtins.open", mock_open()) as m:
        m.side_effect = IOError("disk error")
        chunks = split_file_by_words(str(tmp_path / "fake.txt"), str(output_dir))
    assert chunks == 0


def test_split_file_by_words_unexpected_error(tmp_path):
    """Unexpected exception returns 0 chunks."""
    from unittest.mock import mock_open, patch

    output_dir = tmp_path / "output"
    output_dir.mkdir()
    with patch("builtins.open", mock_open()) as m:
        m.side_effect = RuntimeError("unexpected")
        chunks = split_file_by_words(str(tmp_path / "fake.txt"), str(output_dir))
    assert chunks == 0


def test_split_file_by_lines_empty_file(tmp_path):
    """Empty file returns 0 chunks for line-based splitting."""
    empty_file = tmp_path / "empty.txt"
    empty_file.write_text("")
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    chunks = split_file_by_lines(str(empty_file), str(output_dir))
    assert chunks == 0


def test_split_file_by_lines_unicode_error(tmp_path):
    """UnicodeDecodeError in split_by_lines returns 0."""
    from unittest.mock import mock_open, patch

    output_dir = tmp_path / "output"
    output_dir.mkdir()
    with patch("builtins.open", mock_open()) as m:
        m.side_effect = UnicodeDecodeError("utf-8", b"", 0, 1, "reason")
        chunks = split_file_by_lines(str(tmp_path / "fake.txt"), str(output_dir))
    assert chunks == 0


def test_split_file_by_lines_ioerror(tmp_path):
    """IOError in split_by_lines returns 0."""
    from unittest.mock import mock_open, patch

    output_dir = tmp_path / "output"
    output_dir.mkdir()
    with patch("builtins.open", mock_open()) as m:
        m.side_effect = IOError("disk error")
        chunks = split_file_by_lines(str(tmp_path / "fake.txt"), str(output_dir))
    assert chunks == 0


def test_process_files_failed_when_split_returns_zero(tmp_path):
    """process_files records failure when split returns 0 chunks."""
    from unittest.mock import patch

    output_dir = tmp_path / "output"
    output_dir.mkdir()
    text_file = tmp_path / "test.txt"
    text_file.write_text("content")

    with patch("file_splitter.split_file_by_words", return_value=0):
        stats = process_files([str(text_file)], str(output_dir))
    assert stats["failed"] == 1
    assert stats["processed"] == 0


def test_process_files_skips_non_text_extension(tmp_path):
    """process_files skips files with unrecognized extensions."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    binary_file = tmp_path / "file.xyz"
    binary_file.write_text("content")
    stats = process_files([str(binary_file)], str(output_dir))
    assert stats["skipped"] == 1


def test_process_directory_empty_dir(tmp_path):
    """process_directory returns empty stats for empty directory."""
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()
    output_dir = tmp_path / "output"
    stats = process_directory(str(empty_dir), str(output_dir))
    assert stats["total_files"] == 0


def test_process_directory_recursive(tmp_path):
    """process_directory with recursive=True descends into subdirectories."""
    subdir = tmp_path / "sub"
    subdir.mkdir()
    (subdir / "file.txt").write_text("hello world content here")
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    stats = process_directory(str(tmp_path), str(output_dir), recursive=True)
    assert stats["total_files"] >= 1


def test_process_directory_creates_output_dir(tmp_path):
    """process_directory creates the output directory if it doesn't exist."""
    import os

    (tmp_path / "file.txt").write_text("hello world")
    output_dir = tmp_path / "new_output"
    assert not output_dir.exists()
    process_directory(str(tmp_path), str(output_dir))
    assert os.path.exists(str(output_dir))


def test_split_file_by_lines_single_chunk_verbose(tmp_path):
    """Small file fits in one chunk; verbose prints 'No split needed'."""
    small_file = tmp_path / "small.txt"
    small_file.write_text("hello world\n")
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    chunks = split_file_by_lines(
        str(small_file), str(output_dir), max_chars=100000, verbose=True
    )
    assert chunks == 1


def test_split_file_by_lines_unexpected_error(tmp_path):
    """Generic Exception in split_by_lines returns 0."""
    from unittest.mock import mock_open, patch

    output_dir = tmp_path / "output"
    output_dir.mkdir()
    with patch("builtins.open", mock_open()) as m:
        m.side_effect = RuntimeError("unexpected")
        chunks = split_file_by_lines(str(tmp_path / "fake.txt"), str(output_dir))
    assert chunks == 0


def test_process_files_skips_non_file_path(tmp_path):
    """process_files skips paths that are not regular files (e.g. directories)."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    subdir = tmp_path / "subdir"
    subdir.mkdir()
    stats = process_files([str(subdir)], str(output_dir))
    assert stats["skipped"] == 1


def test_process_directory_skips_non_text_extension(tmp_path):
    """process_directory skips files with non-text extensions."""
    (tmp_path / "file.xyz").write_text("content")
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    stats = process_directory(str(tmp_path), str(output_dir))
    assert stats["skipped"] >= 1
