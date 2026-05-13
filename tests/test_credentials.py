#!/usr/bin/env python3
"""Unit tests for CredentialService."""

import subprocess
from unittest.mock import MagicMock, patch

import pytest


@pytest.mark.unit
def test_is_available_false_when_no_template():
    """is_available returns False when command_template is None."""
    from rdt.shared.credentials import CredentialService

    svc = CredentialService(None)
    assert svc.is_available() is False


@pytest.mark.unit
def test_is_available_true_when_template_set():
    """is_available returns True when command_template is configured."""
    from rdt.shared.credentials import CredentialService

    svc = CredentialService("mypass get {key}")
    assert svc.is_available() is True


@pytest.mark.unit
def test_get_credential_calls_subprocess_with_substituted_key():
    """get_credential calls subprocess with the key substituted into the template."""
    from rdt.shared.credentials import CredentialService

    svc = CredentialService("mypass get {key}")
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = "mysecret\n"

    with patch("rdt.shared.credentials.subprocess.run", return_value=mock_result) as mock_run:
        svc.get_credential("my_api_key")
        mock_run.assert_called_once()
        cmd = mock_run.call_args[0][0]
        assert "my_api_key" in cmd


@pytest.mark.unit
def test_get_credential_returns_stripped_stdout_on_success():
    """get_credential returns stripped stdout when returncode is 0."""
    from rdt.shared.credentials import CredentialService

    svc = CredentialService("mypass get {key}")
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = "  mysecret  \n"

    with patch("rdt.shared.credentials.subprocess.run", return_value=mock_result):
        result = svc.get_credential("api_key")
        assert result == "mysecret"


@pytest.mark.unit
def test_get_credential_returns_none_on_nonzero_returncode():
    """get_credential returns None when the command exits with non-zero status."""
    from rdt.shared.credentials import CredentialService

    svc = CredentialService("mypass get {key}")
    mock_result = MagicMock()
    mock_result.returncode = 1
    mock_result.stdout = ""

    with patch("rdt.shared.credentials.subprocess.run", return_value=mock_result):
        result = svc.get_credential("missing_key")
        assert result is None


@pytest.mark.unit
def test_get_credential_returns_none_on_timeout():
    """get_credential returns None when the subprocess times out."""
    from rdt.shared.credentials import CredentialService

    svc = CredentialService("slowpass get {key}")
    with patch(
        "rdt.shared.credentials.subprocess.run",
        side_effect=subprocess.TimeoutExpired("slowpass", 10),
    ):
        result = svc.get_credential("slow_key")
        assert result is None


@pytest.mark.unit
def test_get_credential_returns_none_on_file_not_found():
    """get_credential returns None when the credential command is not installed."""
    from rdt.shared.credentials import CredentialService

    svc = CredentialService("notinstalled get {key}")
    with patch(
        "rdt.shared.credentials.subprocess.run",
        side_effect=FileNotFoundError("notinstalled"),
    ):
        result = svc.get_credential("some_key")
        assert result is None


@pytest.mark.unit
def test_get_credential_returns_none_when_no_template():
    """get_credential returns None immediately when no template is configured."""
    from rdt.shared.credentials import CredentialService

    svc = CredentialService(None)
    result = svc.get_credential("any_key")
    assert result is None
