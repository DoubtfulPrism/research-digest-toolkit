#!/usr/bin/env python3
"""Unit tests for rich_utils.py covering uncovered helper functions."""

import pytest
from rich.console import Console
from rich.progress import Progress
from rich.table import Table


@pytest.mark.unit
class TestGetConsole:
    """Tests for get_console()."""

    def test_verbose_returns_normal_console(self):
        from rich_utils import console, get_console

        result = get_console(verbose=True)
        assert isinstance(result, Console)
        assert result is console

    def test_quiet_returns_quiet_console(self):
        from rich_utils import get_console, quiet_console

        result = get_console(verbose=False)
        assert result is quiet_console

    def test_stderr_verbose_returns_stderr_console(self):
        from rich_utils import console_err, get_console

        result = get_console(verbose=True, use_stderr=True)
        assert result is console_err

    def test_stderr_quiet_returns_quiet_stderr_console(self):
        from rich_utils import get_console, quiet_console_err

        result = get_console(verbose=False, use_stderr=True)
        assert result is quiet_console_err


@pytest.mark.unit
class TestPrintHeader:
    """Tests for print_header()."""

    def test_print_header_no_subtitle(self, capsys):
        from rich_utils import print_header

        print_header("My Title", verbose=True)
        # Just verify it runs without error; Rich output is hard to capture cleanly

    def test_print_header_with_subtitle(self, capsys):
        from rich_utils import print_header

        print_header("My Title", subtitle="My Subtitle", verbose=True)

    def test_print_header_quiet_mode(self, capsys):
        from rich_utils import print_header

        print_header("Hidden Title", verbose=False)


@pytest.mark.unit
class TestCreateProgressBar:
    """Tests for create_progress_bar()."""

    def test_returns_progress_instance(self):
        from rich_utils import create_progress_bar

        bar = create_progress_bar(verbose=False)
        assert isinstance(bar, Progress)

    def test_verbose_false_disables_bar(self):
        from rich_utils import create_progress_bar

        bar = create_progress_bar(verbose=False)
        assert bar.disable is True

    def test_verbose_true_enables_bar(self):
        from rich_utils import create_progress_bar

        bar = create_progress_bar(verbose=True)
        assert bar.disable is False


@pytest.mark.unit
class TestCreateSummaryTable:
    """Tests for create_summary_table()."""

    def test_returns_table_instance(self):
        from rich_utils import create_summary_table

        table = create_summary_table("My Table", ["Col A", "Col B"])
        assert isinstance(table, Table)

    def test_table_has_correct_title(self):
        from rich_utils import create_summary_table

        table = create_summary_table("Stats", ["Header1"])
        assert table.title == "Stats"

    def test_table_has_correct_column_count(self):
        from rich_utils import create_summary_table

        table = create_summary_table("T", ["A", "B", "C"])
        assert len(table.columns) == 3


@pytest.mark.unit
class TestPrintSeparator:
    """Tests for print_separator()."""

    def test_runs_without_error(self):
        from rich_utils import print_separator

        print_separator(verbose=False)

    def test_verbose_true_runs_without_error(self):
        from rich_utils import print_separator

        print_separator(verbose=True)


@pytest.mark.unit
class TestPrintSection:
    """Tests for print_section()."""

    def test_runs_without_error(self):
        from rich_utils import print_section

        print_section("My Section", verbose=False)
