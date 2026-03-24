#!/usr/bin/env python3
"""Retry utilities for resilient network operations.

Provides retry decorators and configurations for handling transient network
failures with exponential backoff and intelligent error handling.
"""

import requests
from tenacity import (
    retry,
    retry_if_exception,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from rich_utils import print_warning

# Standard retry configuration for HTTP requests
# Retries: 3 attempts
# Backoff: 1s, 2s, 4s (exponential)
# Retry on: Network errors, 5xx server errors, 429 rate limit
standard_retry = retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type(
        (
            requests.exceptions.Timeout,
            requests.exceptions.ConnectionError,
            requests.exceptions.HTTPError,
        )
    ),
    reraise=True,
)

# Rate-limited API retry configuration
# Retries: 5 attempts (more lenient for rate limits)
# Backoff: 2s, 4s, 8s, 16s, 32s (exponential with longer waits)
# Retry on: Network errors, 5xx server errors, 429 rate limit
rate_limit_retry = retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=2, min=2, max=60),
    retry=retry_if_exception_type(
        (
            requests.exceptions.Timeout,
            requests.exceptions.ConnectionError,
            requests.exceptions.HTTPError,
        )
    ),
    reraise=True,
)


def should_retry_http_error(exception):
    """Determine if an HTTP error should be retried.

    Args:
        exception: The exception to check.

    Returns:
        True if the error should be retried, False otherwise.
    """
    if isinstance(exception, requests.exceptions.HTTPError):
        # Retry on 5xx server errors and 429 rate limit
        if exception.response is not None:
            status_code = exception.response.status_code
            # Don't retry 4xx client errors (except 429 rate limit)
            if 400 <= status_code < 500 and status_code != 429:
                return False
            # Retry 5xx server errors and 429 rate limit
            return status_code >= 500 or status_code == 429
    # Retry all network-related errors
    return isinstance(
        exception,
        (
            requests.exceptions.Timeout,
            requests.exceptions.ConnectionError,
        ),
    )


def retry_with_logging(verbose=True):
    """Decorator factory for retrying with rich logging.

    Args:
        verbose: Whether to log retry attempts.

    Returns:
        Retry decorator with logging.
    """

    def log_retry_attempt(retry_state):
        """Log retry attempts with rich formatting."""
        if verbose:
            attempt = retry_state.attempt_number
            if retry_state.outcome.failed:
                exception = retry_state.outcome.exception()
                wait_time = (
                    retry_state.next_action.sleep if retry_state.next_action else 0
                )
                print_warning(
                    f"Attempt {attempt} failed: {type(exception).__name__}: {exception}. "
                    f"Retrying in {wait_time:.1f}s...",
                    verbose,
                )

    return retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception(should_retry_http_error),
        before_sleep=log_retry_attempt,
        reraise=True,
    )


def retry_api_call(verbose=True):
    """Decorator factory for API calls with rate limit handling.

    Args:
        verbose: Whether to log retry attempts.

    Returns:
        Retry decorator optimized for API calls.
    """

    def log_retry_attempt(retry_state):
        """Log retry attempts with rich formatting."""
        if verbose:
            attempt = retry_state.attempt_number
            if retry_state.outcome.failed:
                exception = retry_state.outcome.exception()
                wait_time = (
                    retry_state.next_action.sleep if retry_state.next_action else 0
                )

                # Special message for rate limits
                if isinstance(exception, requests.exceptions.HTTPError):
                    if (
                        exception.response is not None
                        and exception.response.status_code == 429
                    ):
                        print_warning(
                            f"Rate limited (attempt {attempt}). Waiting {wait_time:.1f}s before retry...",
                            verbose,
                        )
                        return

                print_warning(
                    f"API call failed (attempt {attempt}): {type(exception).__name__}. "
                    f"Retrying in {wait_time:.1f}s...",
                    verbose,
                )

    return retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=2, min=2, max=60),
        retry=retry_if_exception(should_retry_http_error),
        before_sleep=log_retry_attempt,
        reraise=True,
    )


def make_resilient_request(url, session=None, verbose=True, **kwargs):
    """Make a resilient HTTP GET request with automatic retries.

    Args:
        url: The URL to fetch.
        session: Optional requests.Session to use.
        verbose: Whether to log retry attempts.
        **kwargs: Additional arguments passed to requests.get().

    Returns:
        requests.Response object.

    Raises:
        requests.exceptions.RequestException: After all retries exhausted.
    """

    @retry_with_logging(verbose=verbose)
    def _make_request():
        if session:
            response = session.get(url, **kwargs)
        else:
            response = requests.get(url, **kwargs)
        response.raise_for_status()
        return response

    return _make_request()


def make_resilient_api_call(url, session=None, verbose=True, **kwargs):
    """Make a resilient API call with rate limit handling.

    Args:
        url: The API endpoint URL.
        session: Optional requests.Session to use.
        verbose: Whether to log retry attempts.
        **kwargs: Additional arguments passed to requests.get().

    Returns:
        requests.Response object.

    Raises:
        requests.exceptions.RequestException: After all retries exhausted.
    """

    @retry_api_call(verbose=verbose)
    def _make_request():
        if session:
            response = session.get(url, **kwargs)
        else:
            response = requests.get(url, **kwargs)
        response.raise_for_status()
        return response

    return _make_request()
