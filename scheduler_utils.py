#!/usr/bin/env python3
"""
Scheduler utilities for Research Digest.

Provides safe, validated scheduling functionality using the schedule library.
Implements proper error handling, signal handling, and follows modern Python practices.
"""

import re
import time
from typing import Callable, Tuple

import schedule

from rich_utils import print_info


class ScheduleError(ValueError):
    """Raised when schedule string is invalid or malicious."""


class SignalHandler:
    """Handles graceful shutdown on SIGINT/SIGTERM."""

    def __init__(self):
        """Initialize the signal handler."""
        self.should_shutdown = False

    def handle_signal(self, signum: int, frame) -> None:
        """Handle shutdown signals.

        Args:
            signum: Signal number.
            frame: Current stack frame.
        """
        print_info("\nShutting down gracefully...", verbose=True)
        self.should_shutdown = True


def parse_schedule_string(schedule_str: str) -> Tuple[str, ...]:
    """Parse and validate a schedule string.

    Supports formats:
    - "every N hours/minutes/seconds"
    - "every hour/day"
    - "every day at HH:MM"
    - "every monday/tuesday/.../sunday at HH:MM"

    Args:
        schedule_str: The schedule string to parse.

    Returns:
        Tuple of parsed components (schedule_type, *args).

    Raises:
        ScheduleError: If the schedule string is invalid or potentially malicious.

    Examples:
        >>> parse_schedule_string("every 4 hours")
        ('every', 4, 'hours')
        >>> parse_schedule_string("every day at 10:30")
        ('every_day_at', '10:30')
    """
    if not schedule_str or not isinstance(schedule_str, str):
        raise ScheduleError("Schedule string must be a non-empty string")

    # Normalize: strip and lowercase
    normalized = schedule_str.strip().lower()

    # Security: Check for suspicious patterns (code injection attempts)
    suspicious_patterns = [
        r"__import__",
        r"exec\(",
        r"eval\(",
        r"system\(",
        r"subprocess",
        r"os\.",
        r"sys\.",
        r"[;\n]",  # Statement separators
        r"DROP\s+TABLE",  # SQL injection
    ]

    for pattern in suspicious_patterns:
        if re.search(pattern, normalized, re.IGNORECASE):
            raise ScheduleError(
                f"Potentially malicious schedule string detected: {schedule_str}"
            )

    # Pattern matching with regex for validation
    # Format: "every N unit" (e.g., "every 4 hours")
    match = re.match(r"^every\s+(\d+)\s+(hour|minute|second|day)s?$", normalized)
    if match:
        number = int(match.group(1))
        unit = match.group(2) + "s"  # Normalize to plural
        return ("every", number, unit)

    # Format: "every unit" (e.g., "every hour")
    match = re.match(r"^every\s+(hour|day|minute|second)s?$", normalized)
    if match:
        unit = match.group(1)
        return (f"every_{unit}",)

    # Format: "every day at HH:MM"
    match = re.match(r"^every\s+day\s+at\s+(\d{1,2}:\d{2})$", normalized)
    if match:
        time_str = match.group(1)
        _validate_time_format(time_str)
        return ("every_day_at", time_str)

    # Format: "every weekday at HH:MM"
    weekdays = [
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday",
    ]
    for weekday in weekdays:
        match = re.match(rf"^every\s+{weekday}\s+at\s+(\d{{1,2}}:\d{{2}})$", normalized)
        if match:
            time_str = match.group(1)
            _validate_time_format(time_str)
            return (f"every_{weekday}_at", time_str)

    # If no pattern matched, it's invalid
    raise ScheduleError(
        f"Invalid schedule format: '{schedule_str}'. "
        f"Supported formats: 'every N hours', 'every day at HH:MM', "
        f"'every monday at HH:MM', etc."
    )


def _validate_time_format(time_str: str) -> None:
    """Validate time string is in valid HH:MM format.

    Args:
        time_str: Time string in HH:MM format.

    Raises:
        ScheduleError: If time format is invalid.
    """
    try:
        hours, minutes = map(int, time_str.split(":"))
        if not (0 <= hours <= 23 and 0 <= minutes <= 59):
            raise ScheduleError(
                f"Invalid time: {time_str}. Hours must be 0-23, minutes 0-59."
            )
    except ValueError:
        raise ScheduleError(f"Invalid time format: {time_str}. Expected HH:MM.")


def setup_schedule(schedule_str: str, job_func: Callable) -> schedule.Job:
    """Set up a schedule job safely without using eval.

    Args:
        schedule_str: The schedule string (e.g., "every 4 hours").
        job_func: The function to run on schedule.

    Returns:
        The created schedule.Job object.

    Raises:
        ScheduleError: If the schedule string is invalid.

    Examples:
        >>> def my_job():
        ...     print("Running job")
        >>> job = setup_schedule("every hour", my_job)
    """
    parsed = parse_schedule_string(schedule_str)
    schedule_type = parsed[0]

    # Map schedule types to schedule API calls
    if schedule_type == "every" and len(parsed) == 3:
        _, number, unit = parsed
        # schedule.every(N).hours/minutes/seconds.do(job)
        job = getattr(schedule.every(number), unit).do(job_func)

    elif schedule_type == "every_hour":
        job = schedule.every().hour.do(job_func)

    elif schedule_type == "every_day":
        job = schedule.every().day.do(job_func)

    elif schedule_type == "every_minute":
        job = schedule.every().minute.do(job_func)

    elif schedule_type == "every_second":
        job = schedule.every().second.do(job_func)

    elif schedule_type == "every_day_at":
        time_str = parsed[1]
        job = schedule.every().day.at(time_str).do(job_func)

    elif schedule_type.startswith("every_") and schedule_type.endswith("_at"):
        # Extract weekday (e.g., "every_monday_at" -> "monday")
        weekday = schedule_type.replace("every_", "").replace("_at", "")
        time_str = parsed[1]
        weekday_obj = getattr(schedule.every(), weekday)
        job = weekday_obj.at(time_str).do(job_func)

    else:
        raise ScheduleError(f"Unsupported schedule type: {schedule_type}")

    return job


def run_scheduler(signal_handler: SignalHandler, sleep_interval: float = 1.0) -> None:
    """Run the scheduler loop.

    Args:
        signal_handler: Signal handler for graceful shutdown.
        sleep_interval: Time to sleep between checking pending jobs (seconds).
    """
    print_info("Scheduler running. Press Ctrl+C to stop.", verbose=True)

    while not signal_handler.should_shutdown:
        schedule.run_pending()
        time.sleep(sleep_interval)

    print_info("Scheduler stopped.", verbose=True)
