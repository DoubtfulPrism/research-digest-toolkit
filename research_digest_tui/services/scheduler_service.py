#!/usr/bin/env python3
"""SchedulerService — wraps ConfigService for schedule configuration."""

from __future__ import annotations

from typing import TYPE_CHECKING

from research_digest_tui.scheduler_utils import ScheduleError, parse_schedule_string

if TYPE_CHECKING:
    from .config_service import ConfigService


class SchedulerService:
    """Provides schedule configuration access and validation.

    Wraps ConfigService write methods with schedule-specific validation.
    """

    _config: ConfigService

    def __init__(self, config_service: ConfigService) -> None:
        self._config = config_service

    def get_schedule_string(self) -> str | None:
        """Return the current schedule string, or None if not set."""
        schedule_cfg = getattr(self._config.config, "schedule", None)
        if schedule_cfg is None:
            return None
        result: str | None = schedule_cfg.schedule_string
        return result

    def get_schedule_enabled(self) -> bool:
        """Return whether the schedule is currently enabled."""
        schedule_cfg = getattr(self._config.config, "schedule", None)
        if schedule_cfg is None:
            return False
        return bool(schedule_cfg.enabled)

    def set_schedule(self, schedule_str: str) -> None:
        """Validate and save the schedule string.

        Raises ScheduleError if the schedule string is invalid.
        """
        valid, msg = self.validate(schedule_str)
        if not valid:
            raise ScheduleError(msg)
        self._config.set_schedule(schedule_str)

    def set_enabled(self, enabled: bool) -> None:
        """Enable or disable the schedule."""
        self._config.set_schedule_enabled(enabled)

    def validate(self, schedule_str: str) -> tuple[bool, str]:
        """Validate a schedule string.

        Returns (True, 'Valid') or (False, error_message).
        """
        if not schedule_str or not schedule_str.strip():
            return False, "Schedule string cannot be empty"
        try:
            _ = parse_schedule_string(schedule_str)
            return True, "Valid"
        except ScheduleError as e:
            return False, str(e)
