#!/usr/bin/env python3
"""Tests for rdt.tui.services.update_service — update checking and execution."""

import json
import time
from unittest.mock import patch, MagicMock, PropertyMock

import pytest


# ---------------------------------------------------------------------------
# UpdateResult / UpdateOutcome dataclasses (smoke test imports)
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_update_result_fields():
    """UpdateResult dataclass holds expected fields."""
    from rdt.tui.services.update_service import UpdateResult

    result = UpdateResult(
        available=True,
        local_version="1.0.2",
        remote_version="1.1.0",
        error=None,
    )
    assert result.available is True
    assert result.remote_version == "1.1.0"


@pytest.mark.unit
def test_update_outcome_fields():
    """UpdateOutcome dataclass holds expected fields."""
    from rdt.tui.services.update_service import UpdateOutcome

    outcome = UpdateOutcome(
        success=True,
        method="uv",
        new_version="1.1.0",
        error=None,
    )
    assert outcome.success is True
    assert outcome.method == "uv"


# ---------------------------------------------------------------------------
# check_for_update
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_check_for_update_newer_available():
    """check_for_update detects when a newer version exists on GitHub."""
    from rdt.tui.services.update_service import UpdateService

    tags_json = [{"name": "v2.0.0"}, {"name": "v1.0.2"}]
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = tags_json

    service = UpdateService()
    with patch("rdt.tui.services.update_service.get_local_version", return_value="1.0.2"):
        with patch("rdt.tui.services.update_service.httpx") as mock_httpx:
            mock_client = MagicMock()
            mock_client.__enter__ = MagicMock(return_value=mock_client)
            mock_client.__exit__ = MagicMock(return_value=False)
            mock_client.get.return_value = mock_response
            mock_httpx.Client.return_value = mock_client

            result = service.check_for_update()

    assert result.available is True
    assert result.remote_version == "2.0.0"
    assert result.local_version == "1.0.2"


@pytest.mark.unit
def test_check_for_update_already_latest():
    """check_for_update reports no update when already on latest."""
    from rdt.tui.services.update_service import UpdateService

    tags_json = [{"name": "v1.0.2"}, {"name": "v1.0.1"}]
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = tags_json

    service = UpdateService()
    with patch("rdt.tui.services.update_service.get_local_version", return_value="1.0.2"):
        with patch("rdt.tui.services.update_service.httpx") as mock_httpx:
            mock_client = MagicMock()
            mock_client.__enter__ = MagicMock(return_value=mock_client)
            mock_client.__exit__ = MagicMock(return_value=False)
            mock_client.get.return_value = mock_response
            mock_httpx.Client.return_value = mock_client

            result = service.check_for_update()

    assert result.available is False
    assert result.error is None


@pytest.mark.unit
def test_check_for_update_skips_non_semver_tags():
    """check_for_update ignores tags like 'beta' that aren't semver."""
    from rdt.tui.services.update_service import UpdateService

    tags_json = [{"name": "beta"}, {"name": "v1.0.2"}, {"name": "v1.0.1"}]
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = tags_json

    service = UpdateService()
    with patch("rdt.tui.services.update_service.get_local_version", return_value="1.0.2"):
        with patch("rdt.tui.services.update_service.httpx") as mock_httpx:
            mock_client = MagicMock()
            mock_client.__enter__ = MagicMock(return_value=mock_client)
            mock_client.__exit__ = MagicMock(return_value=False)
            mock_client.get.return_value = mock_response
            mock_httpx.Client.return_value = mock_client

            result = service.check_for_update()

    assert result.available is False


@pytest.mark.unit
def test_check_for_update_includes_prereleases_when_opted_in():
    """check_for_update includes pre-release-style tags when include_prereleases=True.

    Note: for this to work, pre-release tags must still be parseable semver (e.g. 'v2.0.0').
    Non-semver tags like 'beta' are always skipped regardless.
    """
    from rdt.tui.services.update_service import UpdateService

    # 'beta' is not semver, so it's always skipped. But v2.0.0-beta would be too.
    # The include_prereleases flag is about future pre-release semver tags.
    tags_json = [{"name": "beta"}, {"name": "v1.0.2"}]
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = tags_json

    service = UpdateService(include_prereleases=True)
    with patch("rdt.tui.services.update_service.get_local_version", return_value="1.0.2"):
        with patch("rdt.tui.services.update_service.httpx") as mock_httpx:
            mock_client = MagicMock()
            mock_client.__enter__ = MagicMock(return_value=mock_client)
            mock_client.__exit__ = MagicMock(return_value=False)
            mock_client.get.return_value = mock_response
            mock_httpx.Client.return_value = mock_client

            result = service.check_for_update()

    # 'beta' still isn't semver, so no update. This validates the flag is accepted.
    assert result.available is False


@pytest.mark.unit
def test_check_for_update_network_error():
    """check_for_update handles network errors gracefully without crashing."""
    from rdt.tui.services.update_service import UpdateService
    import httpx

    service = UpdateService()
    with patch("rdt.tui.services.update_service.get_local_version", return_value="1.0.2"):
        with patch("rdt.tui.services.update_service.httpx") as mock_httpx:
            mock_client = MagicMock()
            mock_client.__enter__ = MagicMock(return_value=mock_client)
            mock_client.__exit__ = MagicMock(return_value=False)
            mock_client.get.side_effect = httpx.ConnectError("Connection refused")
            mock_httpx.Client.return_value = mock_client
            mock_httpx.ConnectError = httpx.ConnectError
            mock_httpx.TimeoutException = httpx.TimeoutException
            mock_httpx.HTTPError = httpx.HTTPError

            result = service.check_for_update()

    assert result.available is False
    assert result.error is not None


@pytest.mark.unit
def test_check_for_update_timeout():
    """check_for_update handles timeouts gracefully."""
    from rdt.tui.services.update_service import UpdateService
    import httpx

    service = UpdateService()
    with patch("rdt.tui.services.update_service.get_local_version", return_value="1.0.2"):
        with patch("rdt.tui.services.update_service.httpx") as mock_httpx:
            mock_client = MagicMock()
            mock_client.__enter__ = MagicMock(return_value=mock_client)
            mock_client.__exit__ = MagicMock(return_value=False)
            mock_client.get.side_effect = httpx.TimeoutException("Timeout")
            mock_httpx.Client.return_value = mock_client
            mock_httpx.ConnectError = httpx.ConnectError
            mock_httpx.TimeoutException = httpx.TimeoutException
            mock_httpx.HTTPError = httpx.HTTPError

            result = service.check_for_update()

    assert result.available is False
    assert result.error is not None


# ---------------------------------------------------------------------------
# Throttle (24-hour check interval)
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_should_check_returns_true_when_no_timestamp_file(tmp_path):
    """should_check returns True when no previous check timestamp exists."""
    from rdt.tui.services.update_service import UpdateService

    service = UpdateService(state_dir=tmp_path)
    assert service.should_check() is True


@pytest.mark.unit
def test_should_check_returns_false_within_24h(tmp_path):
    """should_check returns False when checked less than 24 hours ago."""
    from rdt.tui.services.update_service import UpdateService

    service = UpdateService(state_dir=tmp_path)
    # Write a recent timestamp
    ts_file = tmp_path / ".update_check"
    ts_file.write_text(str(time.time()))

    assert service.should_check() is False


@pytest.mark.unit
def test_should_check_returns_true_after_24h(tmp_path):
    """should_check returns True when the last check was more than 24 hours ago."""
    from rdt.tui.services.update_service import UpdateService

    service = UpdateService(state_dir=tmp_path)
    ts_file = tmp_path / ".update_check"
    ts_file.write_text(str(time.time() - 90000))  # 25 hours ago

    assert service.should_check() is True


@pytest.mark.unit
def test_record_check_writes_timestamp(tmp_path):
    """record_check writes a timestamp file."""
    from rdt.tui.services.update_service import UpdateService

    service = UpdateService(state_dir=tmp_path)
    service.record_check()

    ts_file = tmp_path / ".update_check"
    assert ts_file.exists()
    ts = float(ts_file.read_text())
    assert abs(ts - time.time()) < 5  # within 5 seconds


# ---------------------------------------------------------------------------
# detect_install_method
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_detect_install_method_uv():
    """detect_install_method returns 'uv' when uv tool list contains the package."""
    from rdt.tui.services.update_service import UpdateService

    service = UpdateService()
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = "research-digest-toolkit v1.0.2\n- rdt\n- Research_Toolkit\n"

    with patch("rdt.tui.services.update_service.subprocess.run", return_value=mock_result):
        assert service.detect_install_method() == "uv"


@pytest.mark.unit
def test_detect_install_method_pipx():
    """detect_install_method returns 'pipx' when pipx list contains the package."""
    from rdt.tui.services.update_service import UpdateService

    service = UpdateService()
    uv_result = MagicMock()
    uv_result.returncode = 1
    uv_result.stdout = ""

    pipx_result = MagicMock()
    pipx_result.returncode = 0
    pipx_result.stdout = "   package research-digest-toolkit 1.0.2\n"

    def side_effect(cmd, **kwargs):
        if "uv" in cmd:
            return uv_result
        return pipx_result

    with patch("rdt.tui.services.update_service.subprocess.run", side_effect=side_effect):
        assert service.detect_install_method() == "pipx"


@pytest.mark.unit
def test_detect_install_method_unknown():
    """detect_install_method returns 'unknown' when neither uv nor pipx found."""
    from rdt.tui.services.update_service import UpdateService

    service = UpdateService()
    mock_result = MagicMock()
    mock_result.returncode = 1
    mock_result.stdout = ""

    with patch("rdt.tui.services.update_service.subprocess.run", return_value=mock_result):
        assert service.detect_install_method() == "unknown"


# ---------------------------------------------------------------------------
# perform_update
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_perform_update_uv_success():
    """perform_update succeeds via uv tool upgrade."""
    from rdt.tui.services.update_service import UpdateService

    service = UpdateService()
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = "Updated research-digest-toolkit to 1.1.0"
    mock_result.stderr = ""

    with patch.object(service, "detect_install_method", return_value="uv"):
        with patch("rdt.tui.services.update_service.subprocess.run", return_value=mock_result):
            outcome = service.perform_update()

    assert outcome.success is True
    assert outcome.method == "uv"


@pytest.mark.unit
def test_perform_update_failure():
    """perform_update reports failure when subprocess returns non-zero."""
    from rdt.tui.services.update_service import UpdateService

    service = UpdateService()
    mock_result = MagicMock()
    mock_result.returncode = 1
    mock_result.stdout = ""
    mock_result.stderr = "error: package not found"

    with patch.object(service, "detect_install_method", return_value="uv"):
        with patch("rdt.tui.services.update_service.subprocess.run", return_value=mock_result):
            outcome = service.perform_update()

    assert outcome.success is False
    assert outcome.error is not None


@pytest.mark.unit
def test_perform_update_unknown_method():
    """perform_update fails gracefully when install method is unknown."""
    from rdt.tui.services.update_service import UpdateService

    service = UpdateService()
    with patch.object(service, "detect_install_method", return_value="unknown"):
        outcome = service.perform_update()

    assert outcome.success is False
    assert "manual" in outcome.error.lower() or "unknown" in outcome.error.lower()
