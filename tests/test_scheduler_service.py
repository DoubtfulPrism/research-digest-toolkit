#!/usr/bin/env python3
"""Unit tests for SchedulerService."""

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).parent.parent))


def _write_config(tmp_path: Path, extra: dict | None = None) -> Path:
    """Write a minimal config YAML for testing."""
    data: dict = {
        "scrapers": {"hackernews": {"enabled": True, "search_topics": []}},
        "output": {},
        "processing": {},
        "topics": {},
        "formats": {},
        "report": {},
    }
    if extra:
        data.update(extra)
    p = tmp_path / "config.yaml"
    p.write_text(yaml.dump(data))
    return p


@pytest.mark.unit
def test_get_schedule_string_returns_config_value(tmp_path):
    """get_schedule_string returns the schedule_string from the YAML config."""
    config_file = _write_config(
        tmp_path,
        {"schedule": {"schedule_string": "every day at 06:00", "enabled": False}},
    )

    from rdt.tui.services.config_service import ConfigService
    from rdt.tui.services.scheduler_service import SchedulerService

    svc = SchedulerService(ConfigService(config_file))
    assert svc.get_schedule_string() == "every day at 06:00"


@pytest.mark.unit
def test_get_schedule_string_returns_none_when_not_set(tmp_path):
    """get_schedule_string returns None when no schedule is configured."""
    config_file = _write_config(tmp_path)

    from rdt.tui.services.config_service import ConfigService
    from rdt.tui.services.scheduler_service import SchedulerService

    svc = SchedulerService(ConfigService(config_file))
    assert svc.get_schedule_string() is None


@pytest.mark.unit
def test_set_schedule_validates_before_saving(tmp_path):
    """set_schedule saves a valid schedule string to the config."""
    pytest.importorskip("ruamel.yaml")
    config_file = _write_config(tmp_path)

    from rdt.tui.services.config_service import ConfigService
    from rdt.tui.services.scheduler_service import SchedulerService

    config_svc = ConfigService(config_file)
    svc = SchedulerService(config_svc)

    svc.set_schedule("every day at 06:00")

    # Reload and verify the value was persisted
    config_svc.reload()
    assert svc.get_schedule_string() == "every day at 06:00"


@pytest.mark.unit
def test_set_schedule_raises_on_invalid_string(tmp_path):
    """set_schedule raises ScheduleError for invalid schedule strings."""
    config_file = _write_config(tmp_path)

    from rdt.shared.scheduler_utils import ScheduleError
    from rdt.tui.services.config_service import ConfigService
    from rdt.tui.services.scheduler_service import SchedulerService

    svc = SchedulerService(ConfigService(config_file))

    with pytest.raises(ScheduleError):
        svc.set_schedule("not a valid schedule")


@pytest.mark.unit
def test_validate_returns_false_for_invalid():
    """validate returns (False, error_message) for invalid schedule strings."""

    from rdt.tui.services.scheduler_service import SchedulerService

    svc = SchedulerService(MagicMock())
    valid, msg = svc.validate("every banana at 99:99")

    assert valid is False
    assert isinstance(msg, str)
    assert len(msg) > 0


@pytest.mark.unit
def test_validate_returns_true_for_valid():
    """validate returns (True, 'Valid') for a well-formed schedule string."""

    from rdt.tui.services.scheduler_service import SchedulerService

    svc = SchedulerService(MagicMock())
    valid, msg = svc.validate("every day at 06:00")

    assert valid is True


@pytest.mark.unit
def test_set_enabled_calls_config_service(tmp_path):
    """set_enabled delegates to config_service.set_schedule_enabled."""

    from rdt.tui.services.scheduler_service import SchedulerService

    mock_config = MagicMock()
    mock_config.config.schedule.enabled = False

    svc = SchedulerService(mock_config)
    svc.set_enabled(True)

    mock_config.set_schedule_enabled.assert_called_once_with(True)
