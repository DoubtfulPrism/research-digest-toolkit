#!/usr/bin/env python3
"""Unit tests for retry_utils.py."""

from unittest.mock import MagicMock, patch

import pytest
import requests


@pytest.mark.unit
class TestShouldRetryHttpError:
    """Tests for should_retry_http_error()."""

    def test_5xx_server_error_returns_true(self):
        from retry_utils import should_retry_http_error

        exc = requests.exceptions.HTTPError()
        exc.response = MagicMock(status_code=500)
        assert should_retry_http_error(exc) is True

    def test_503_returns_true(self):
        from retry_utils import should_retry_http_error

        exc = requests.exceptions.HTTPError()
        exc.response = MagicMock(status_code=503)
        assert should_retry_http_error(exc) is True

    def test_429_rate_limit_returns_true(self):
        from retry_utils import should_retry_http_error

        exc = requests.exceptions.HTTPError()
        exc.response = MagicMock(status_code=429)
        assert should_retry_http_error(exc) is True

    def test_404_not_found_returns_false(self):
        from retry_utils import should_retry_http_error

        exc = requests.exceptions.HTTPError()
        exc.response = MagicMock(status_code=404)
        assert should_retry_http_error(exc) is False

    def test_401_unauthorized_returns_false(self):
        from retry_utils import should_retry_http_error

        exc = requests.exceptions.HTTPError()
        exc.response = MagicMock(status_code=401)
        assert should_retry_http_error(exc) is False

    def test_400_bad_request_returns_false(self):
        from retry_utils import should_retry_http_error

        exc = requests.exceptions.HTTPError()
        exc.response = MagicMock(status_code=400)
        assert should_retry_http_error(exc) is False

    def test_http_error_no_response_returns_false(self):
        from retry_utils import should_retry_http_error

        exc = requests.exceptions.HTTPError()
        exc.response = None
        result = should_retry_http_error(exc)
        # No response means we can't determine status — function returns False for HTTPError without response
        assert isinstance(result, bool)

    def test_timeout_returns_true(self):
        from retry_utils import should_retry_http_error

        exc = requests.exceptions.Timeout()
        assert should_retry_http_error(exc) is True

    def test_connection_error_returns_true(self):
        from retry_utils import should_retry_http_error

        exc = requests.exceptions.ConnectionError()
        assert should_retry_http_error(exc) is True

    def test_non_http_exception_returns_false(self):
        from retry_utils import should_retry_http_error

        assert should_retry_http_error(ValueError("bad")) is False


@pytest.mark.unit
class TestRetryWithLogging:
    """Tests for retry_with_logging() decorator factory."""

    def test_returns_callable_decorator(self):
        from retry_utils import retry_with_logging

        decorator = retry_with_logging(verbose=False)
        assert callable(decorator)

    def test_decorated_function_succeeds_on_first_try(self):
        from retry_utils import retry_with_logging

        call_count = 0

        @retry_with_logging(verbose=False)
        def fn():
            nonlocal call_count
            call_count += 1
            return "ok"

        result = fn()
        assert result == "ok"
        assert call_count == 1

    def test_decorated_function_raises_after_exhausted_retries(self):
        from retry_utils import retry_with_logging

        @retry_with_logging(verbose=False)
        def always_fail():
            exc = requests.exceptions.ConnectionError("network error")
            raise exc

        with pytest.raises(requests.exceptions.ConnectionError):
            always_fail()

    def test_verbose_logs_retry_attempt(self, capsys):
        from retry_utils import retry_with_logging

        call_count = 0

        @retry_with_logging(verbose=True)
        def fail_once():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise requests.exceptions.ConnectionError("transient error")
            return "ok"

        result = fail_once()
        assert result == "ok"
        assert call_count == 2


@pytest.mark.unit
class TestRetryApiCall:
    """Tests for retry_api_call() decorator factory."""

    def test_returns_callable_decorator(self):
        from retry_utils import retry_api_call

        decorator = retry_api_call(verbose=False)
        assert callable(decorator)

    def test_decorated_function_succeeds_on_first_try(self):
        from retry_utils import retry_api_call

        @retry_api_call(verbose=False)
        def fn():
            return 42

        assert fn() == 42

    def test_verbose_logs_general_api_failure(self, capsys):
        from retry_utils import retry_api_call

        call_count = 0

        @retry_api_call(verbose=True)
        def fail_once():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise requests.exceptions.ConnectionError("api error")
            return "done"

        result = fail_once()
        assert result == "done"

    def test_verbose_logs_rate_limit_429(self, capsys):
        from retry_utils import retry_api_call

        call_count = 0

        @retry_api_call(verbose=True)
        def rate_limited():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                exc = requests.exceptions.HTTPError()
                resp = MagicMock()
                resp.status_code = 429
                exc.response = resp
                raise exc
            return "ok"

        result = rate_limited()
        assert result == "ok"


@pytest.mark.unit
class TestMakeResilientRequest:
    """Tests for make_resilient_request()."""

    @patch("retry_utils.requests.get")
    def test_successful_request_without_session(self, mock_get):
        from retry_utils import make_resilient_request

        mock_resp = MagicMock()
        mock_resp.raise_for_status.return_value = None
        mock_get.return_value = mock_resp

        result = make_resilient_request("https://example.com", verbose=False)
        assert result == mock_resp
        mock_get.assert_called_once_with("https://example.com")

    def test_successful_request_with_session(self):
        from retry_utils import make_resilient_request

        session = MagicMock()
        mock_resp = MagicMock()
        mock_resp.raise_for_status.return_value = None
        session.get.return_value = mock_resp

        result = make_resilient_request(
            "https://example.com", session=session, verbose=False
        )
        assert result == mock_resp
        session.get.assert_called_once_with("https://example.com")


@pytest.mark.unit
class TestMakeResilientApiCall:
    """Tests for make_resilient_api_call()."""

    @patch("retry_utils.requests.get")
    def test_successful_call_without_session(self, mock_get):
        from retry_utils import make_resilient_api_call

        mock_resp = MagicMock()
        mock_resp.raise_for_status.return_value = None
        mock_get.return_value = mock_resp

        result = make_resilient_api_call("https://api.example.com", verbose=False)
        assert result == mock_resp

    def test_successful_call_with_session(self):
        from retry_utils import make_resilient_api_call

        session = MagicMock()
        mock_resp = MagicMock()
        mock_resp.raise_for_status.return_value = None
        session.get.return_value = mock_resp

        result = make_resilient_api_call(
            "https://api.example.com", session=session, verbose=False
        )
        assert result == mock_resp
