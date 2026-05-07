"""Tests for research_digest_tui.cli config discovery and entry point."""

from pathlib import Path
from unittest.mock import patch

import pytest


@pytest.mark.unit
def test_find_or_create_config_returns_cwd_config_when_present(tmp_path):
    """When config exists in CWD, _find_or_create_config returns the CWD path."""
    cwd_config = tmp_path / "research_config.yaml"
    cwd_config.write_text("days_back: 7\n")

    from research_digest_tui.cli import _find_or_create_config

    with patch("research_digest_tui.cli._cwd_config", return_value=cwd_config):
        result = _find_or_create_config()

    assert result == cwd_config
    assert isinstance(result, Path)


@pytest.mark.unit
def test_find_or_create_config_returns_home_config_when_cwd_absent(tmp_path):
    """When config is absent in CWD but present in home dir, returns home path."""
    home_config = tmp_path / ".research_digest" / "research_config.yaml"
    home_config.parent.mkdir(parents=True)
    home_config.write_text("days_back: 14\n")

    missing_cwd = tmp_path / "nonexistent_research_config.yaml"

    from research_digest_tui.cli import _find_or_create_config

    with (
        patch("research_digest_tui.cli._cwd_config", return_value=missing_cwd),
        patch("research_digest_tui.cli._home_config", return_value=home_config),
    ):
        result = _find_or_create_config()

    assert result == home_config
    assert isinstance(result, Path)


@pytest.mark.unit
def test_find_or_create_config_copies_default_on_first_run(tmp_path):
    """When no config exists anywhere, copies bundled default to home dir."""
    home_config = tmp_path / ".research_digest" / "research_config.yaml"
    missing_cwd = tmp_path / "nonexistent_research_config.yaml"

    # Create a fake bundled default for the test
    fake_bundled = tmp_path / "research_config.default.yaml"
    fake_bundled.write_text("scrapers: {}\n")

    from research_digest_tui.cli import _find_or_create_config

    with (
        patch("research_digest_tui.cli._cwd_config", return_value=missing_cwd),
        patch("research_digest_tui.cli._home_config", return_value=home_config),
        patch("research_digest_tui.cli._bundled_default", return_value=fake_bundled),
    ):
        result = _find_or_create_config()

    assert result == home_config
    assert home_config.exists()
    assert home_config.read_text() == "scrapers: {}\n"
    assert isinstance(result, Path)


@pytest.mark.unit
def test_find_or_create_config_returns_path_object(tmp_path):
    """Return value is always a Path, not a string."""
    cwd_config = tmp_path / "research_config.yaml"
    cwd_config.write_text("days_back: 7\n")

    from research_digest_tui.cli import _find_or_create_config

    with patch("research_digest_tui.cli._cwd_config", return_value=cwd_config):
        result = _find_or_create_config()

    assert isinstance(result, Path)


@pytest.mark.unit
def test_main_function_is_callable():
    """main() exists and is callable (no args required)."""
    from research_digest_tui.cli import main

    assert callable(main)


@pytest.mark.unit
def test_bundled_default_returns_path_within_package():
    """_bundled_default() returns a path inside the research_digest_tui package."""
    from research_digest_tui.cli import _bundled_default

    path = _bundled_default()
    assert isinstance(path, Path)
    assert "research_digest_tui" in str(path)
    assert path.name == "research_config.default.yaml"
    assert path.exists(), f"Bundled default config not found at: {path}"
