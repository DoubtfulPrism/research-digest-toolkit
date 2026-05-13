#!/usr/bin/env python3
"""Credential service for fetching secrets from a configured CLI command."""

import shlex
import subprocess

from rdt.shared.rich_utils import print_warning


class CredentialService:
    """Fetches credentials via a user-configured CLI command template.

    The command template uses {key} as a placeholder, e.g.:
        "protonpass item get {key}"
        "pass show {key}"
    """

    _template: str | None

    def __init__(self, command_template: str | None) -> None:
        self._template = command_template

    def is_available(self) -> bool:
        """Return True if a credential command template is configured."""
        return bool(self._template)

    def get_credential(self, key: str) -> str | None:
        """Fetch a credential for the given key.

        Returns the stripped stdout on success, or None on any failure.
        Never raises; failures are logged as warnings.
        The credential value is never logged.
        """
        if not self._template:
            return None
        try:
            cmd = shlex.split(self._template.format(key=key))
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                return result.stdout.strip()
            print_warning(
                f"Credential fetch failed for key '{key}' (exit {result.returncode})",
                verbose=True,
            )
            return None
        except subprocess.TimeoutExpired:
            print_warning(f"Credential fetch timed out for key '{key}'", verbose=True)
            return None
        except FileNotFoundError:
            template_cmd = self._template.split()[0] if self._template else ""
            print_warning(f"Credential command not found: {template_cmd}", verbose=True)
            return None
        except Exception as e:
            print_warning(f"Credential fetch error for key '{key}': {e}", verbose=True)
            return None
