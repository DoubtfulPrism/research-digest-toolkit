#!/usr/bin/env python3
"""
Tests for scheduler functionality in research_digest.py.

Testing Strategy:
1. Unit tests for schedule string parsing
2. Integration tests for schedule setup
3. Error handling and validation tests
4. Signal handling tests
"""

import signal
import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from scheduler_utils import (
    ScheduleError,
    SignalHandler,
    _validate_time_format,
    parse_schedule_string,
    setup_schedule,
)


@pytest.mark.unit
class TestParseScheduleString:
    """Tests for schedule string parsing."""

    def test_parse_every_n_hours(self):
        """Test parsing 'every N hours' format."""
        result = parse_schedule_string("every 4 hours")
        assert result == ("every", 4, "hours")

    def test_parse_every_n_minutes(self):
        """Test parsing 'every N minutes' format."""
        result = parse_schedule_string("every 30 minutes")
        assert result == ("every", 30, "minutes")

    def test_parse_every_day_at_time(self):
        """Test parsing 'every day at HH:MM' format."""
        result = parse_schedule_string("every day at 10:30")
        assert result == ("every_day_at", "10:30")

    def test_parse_every_monday_at_time(self):
        """Test parsing 'every monday at HH:MM' format."""
        result = parse_schedule_string("every monday at 09:00")
        assert result == ("every_monday_at", "09:00")

    def test_parse_every_day(self):
        """Test parsing 'every day' format."""
        result = parse_schedule_string("every day")
        assert result == ("every_day",)

    def test_parse_every_hour(self):
        """Test parsing 'every hour' format."""
        result = parse_schedule_string("every hour")
        assert result == ("every_hour",)

    def test_invalid_schedule_string_raises_error(self):
        """Test that invalid schedule strings raise ScheduleError."""
        with pytest.raises(ScheduleError):
            parse_schedule_string("invalid format")

    def test_empty_schedule_string_raises_error(self):
        """Test that empty string raises ScheduleError."""
        with pytest.raises(ScheduleError):
            parse_schedule_string("")

    def test_malicious_code_injection_prevented(self):
        """Test that code injection attempts are rejected."""
        malicious_inputs = [
            "__import__('os').system('ls')",
            "every.__import__('sys').exit()",
            "'; DROP TABLE items; --",
        ]
        for malicious in malicious_inputs:
            with pytest.raises(ScheduleError):
                parse_schedule_string(malicious)

    def test_case_insensitive_parsing(self):
        """Test that parsing is case-insensitive for keywords."""
        result = parse_schedule_string("EVERY DAY AT 10:30")
        assert result == ("every_day_at", "10:30")


@pytest.mark.unit
class TestSetupSchedule:
    """Tests for schedule setup."""

    @patch("scheduler_utils.schedule")
    def test_setup_every_n_hours(self, mock_schedule):
        """Test setting up 'every N hours' schedule."""
        job_func = Mock()
        mock_job = Mock()
        mock_schedule.every.return_value.hours.do = Mock(return_value=mock_job)

        setup_schedule("every 4 hours", job_func)

        mock_schedule.every.assert_called_once_with(4)
        mock_schedule.every.return_value.hours.do.assert_called_once_with(job_func)

    @patch("scheduler_utils.schedule")
    def test_setup_every_day_at_time(self, mock_schedule):
        """Test setting up 'every day at HH:MM' schedule."""
        job_func = Mock()
        mock_job = Mock()
        mock_schedule.every.return_value.day.at.return_value.do = Mock(
            return_value=mock_job
        )

        setup_schedule("every day at 10:30", job_func)

        mock_schedule.every.return_value.day.at.assert_called_once_with("10:30")

    @patch("scheduler_utils.schedule")
    def test_setup_every_monday_at_time(self, mock_schedule):
        """Test setting up weekday-specific schedule."""
        job_func = Mock()
        mock_job = Mock()
        mock_schedule.every.return_value.monday.at.return_value.do = Mock(
            return_value=mock_job
        )

        setup_schedule("every monday at 09:00", job_func)

        mock_schedule.every.return_value.monday.at.assert_called_once_with("09:00")

    def test_setup_with_invalid_string_raises_error(self):
        """Test that invalid schedule string raises ScheduleError."""
        with pytest.raises(ScheduleError):
            setup_schedule("invalid", Mock())

    @patch("scheduler_utils.schedule")
    def test_setup_every_hour(self, mock_schedule):
        job_func = Mock()
        setup_schedule("every hour", job_func)
        mock_schedule.every.return_value.hour.do.assert_called_once_with(job_func)

    @patch("scheduler_utils.schedule")
    def test_setup_every_day(self, mock_schedule):
        job_func = Mock()
        setup_schedule("every day", job_func)
        mock_schedule.every.return_value.day.do.assert_called_once_with(job_func)

    @patch("scheduler_utils.schedule")
    def test_setup_every_minute(self, mock_schedule):
        job_func = Mock()
        setup_schedule("every minute", job_func)
        mock_schedule.every.return_value.minute.do.assert_called_once_with(job_func)

    @patch("scheduler_utils.schedule")
    def test_setup_every_second(self, mock_schedule):
        job_func = Mock()
        setup_schedule("every second", job_func)
        mock_schedule.every.return_value.second.do.assert_called_once_with(job_func)


@pytest.mark.unit
class TestValidateTimeFormat:
    """Tests for _validate_time_format."""

    def test_valid_time_does_not_raise(self):
        _validate_time_format("10:30")

    def test_non_numeric_raises_schedule_error(self):
        with pytest.raises(ScheduleError, match="Invalid time format"):
            _validate_time_format("ab:cd")

    def test_invalid_hour_raises_schedule_error(self):
        with pytest.raises(ScheduleError, match="Invalid time"):
            _validate_time_format("25:00")

    def test_invalid_minute_raises_schedule_error(self):
        with pytest.raises(ScheduleError, match="Invalid time"):
            _validate_time_format("10:60")


@pytest.mark.unit
class TestSignalHandler:
    """Tests for signal handling."""

    def test_signal_handler_sets_shutdown_flag(self):
        """Test that signal handler sets shutdown flag."""
        handler = SignalHandler()
        assert handler.should_shutdown is False

        # Simulate signal
        handler.handle_signal(signal.SIGINT, None)

        assert handler.should_shutdown is True

    def test_signal_handler_logs_message(self, capsys):
        """Test that signal handler logs shutdown message."""
        handler = SignalHandler()

        handler.handle_signal(signal.SIGINT, None)

        captured = capsys.readouterr()
        assert (
            "Shutting down gracefully" in captured.out
            or "Shutting down gracefully" in captured.err
        )


@pytest.mark.integration
class TestScheduleIntegration:
    """Integration tests for schedule functionality."""

    @patch("scheduler_utils.schedule")
    def test_schedule_job_runs(self, mock_schedule):
        """Test that scheduled job is properly registered."""
        job_func = Mock()
        mock_job = Mock()
        mock_schedule.every.return_value.hour.do = Mock(return_value=mock_job)

        setup_schedule("every hour", job_func)

        # Verify job was registered
        mock_schedule.every.return_value.hour.do.assert_called_once_with(job_func)

    @patch("scheduler_utils.schedule")
    @patch("scheduler_utils.time.sleep")
    def test_run_pending_loop(self, mock_sleep, mock_schedule):
        """Test that run_pending is called in loop."""
        from scheduler_utils import run_scheduler

        handler = SignalHandler()

        # Make it stop after 2 iterations
        call_count = [0]

        def side_effect():
            call_count[0] += 1
            if call_count[0] >= 2:
                handler.should_shutdown = True

        mock_schedule.run_pending.side_effect = side_effect

        run_scheduler(handler)

        assert mock_schedule.run_pending.call_count == 2
        assert mock_sleep.call_count >= 1
