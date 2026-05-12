#!/usr/bin/env python3
"""Tests for rdt.core.version — version parsing and comparison logic."""

from unittest.mock import patch, MagicMock

import pytest


# ---------------------------------------------------------------------------
# parse_semver
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_parse_semver_strips_v_prefix():
    """parse_semver('v1.2.3') strips the leading 'v' and returns (1, 2, 3)."""
    from rdt.core.version import parse_semver

    assert parse_semver("v1.2.3") == (1, 2, 3)


@pytest.mark.unit
def test_parse_semver_no_prefix():
    """parse_semver('1.0.0') works without the 'v' prefix."""
    from rdt.core.version import parse_semver

    assert parse_semver("1.0.0") == (1, 0, 0)


@pytest.mark.unit
def test_parse_semver_rejects_non_semver():
    """parse_semver('beta') raises ValueError for non-semver strings."""
    from rdt.core.version import parse_semver

    with pytest.raises(ValueError):
        parse_semver("beta")


@pytest.mark.unit
def test_parse_semver_rejects_partial():
    """parse_semver('1.2') raises ValueError for incomplete version strings."""
    from rdt.core.version import parse_semver

    with pytest.raises(ValueError):
        parse_semver("1.2")


@pytest.mark.unit
def test_parse_semver_with_prerelease_suffix():
    """parse_semver('v1.2.3-rc1') raises ValueError (strict semver only)."""
    from rdt.core.version import parse_semver

    with pytest.raises(ValueError):
        parse_semver("v1.2.3-rc1")


# ---------------------------------------------------------------------------
# is_newer
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_is_newer_true():
    """is_newer returns True when remote version is higher (patch bump)."""
    from rdt.core.version import is_newer

    assert is_newer("1.1.0", "1.0.2") is True


@pytest.mark.unit
def test_is_newer_false_equal():
    """is_newer returns False when versions are equal."""
    from rdt.core.version import is_newer

    assert is_newer("1.0.2", "1.0.2") is False


@pytest.mark.unit
def test_is_newer_false_older():
    """is_newer returns False when remote is older than local."""
    from rdt.core.version import is_newer

    assert is_newer("1.0.1", "1.0.2") is False


@pytest.mark.unit
def test_is_newer_major_bump():
    """is_newer returns True for a major version bump."""
    from rdt.core.version import is_newer

    assert is_newer("2.0.0", "1.9.9") is True


@pytest.mark.unit
def test_is_newer_minor_bump():
    """is_newer returns True for a minor version bump."""
    from rdt.core.version import is_newer

    assert is_newer("1.1.0", "1.0.9") is True


# ---------------------------------------------------------------------------
# get_local_version
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_get_local_version_from_metadata():
    """get_local_version reads from importlib.metadata when package is installed."""
    from rdt.core.version import get_local_version

    with patch("rdt.core.version.metadata_version", return_value="1.0.2"):
        assert get_local_version() == "1.0.2"


@pytest.mark.unit
def test_get_local_version_fallback_pyproject(tmp_path):
    """get_local_version falls back to parsing pyproject.toml when metadata is unavailable."""
    from rdt.core.version import get_local_version

    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text('[project]\nname = "test"\nversion = "3.4.5"\n')

    with patch(
        "rdt.core.version.metadata_version",
        side_effect=Exception("PackageNotFoundError"),
    ):
        with patch("rdt.core.version._find_pyproject_toml", return_value=pyproject):
            assert get_local_version() == "3.4.5"


@pytest.mark.unit
def test_get_local_version_returns_unknown_when_all_fail():
    """get_local_version returns '0.0.0' when both metadata and pyproject.toml fail."""
    from rdt.core.version import get_local_version

    with patch(
        "rdt.core.version.metadata_version",
        side_effect=Exception("PackageNotFoundError"),
    ):
        with patch("rdt.core.version._find_pyproject_toml", return_value=None):
            assert get_local_version() == "0.0.0"
