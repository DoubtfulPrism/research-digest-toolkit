#!/usr/bin/env python3
"""Service for checking and performing RDT updates from GitHub.

Handles version checking against GitHub tags, 24-hour throttling,
install-method detection (uv / pipx / pip), and subprocess-based upgrades.
"""

from __future__ import annotations

import subprocess
import time
from dataclasses import dataclass
from pathlib import Path

import httpx

from rdt.core.version import get_local_version, is_newer, parse_semver


_CHECK_INTERVAL_SECONDS = 86400  # 24 hours
_GITHUB_TAGS_URL = (
    "https://api.github.com/repos/DoubtfulPrism/research-digest-toolkit/tags"
)
_PACKAGE_NAME = "research-digest-toolkit"
_DEFAULT_STATE_DIR = Path.home() / ".research_digest"


@dataclass
class UpdateResult:
    """Result of a version check against GitHub."""

    available: bool
    local_version: str
    remote_version: str | None
    error: str | None


@dataclass
class UpdateOutcome:
    """Result of an update/upgrade attempt."""

    success: bool
    method: str
    new_version: str | None
    error: str | None


class UpdateService:
    """Check GitHub for newer RDT releases and upgrade in-place."""

    def __init__(
        self,
        *,
        state_dir: Path | None = None,
        include_prereleases: bool = False,
    ) -> None:
        self._state_dir = state_dir or _DEFAULT_STATE_DIR
        self._include_prereleases = include_prereleases

    # ------------------------------------------------------------------
    # Throttle helpers
    # ------------------------------------------------------------------

    def _timestamp_path(self) -> Path:
        return self._state_dir / ".update_check"

    def should_check(self) -> bool:
        """Return ``True`` if enough time has passed since the last check."""
        ts_file = self._timestamp_path()
        if not ts_file.exists():
            return True
        try:
            last_ts = float(ts_file.read_text().strip())
            return (time.time() - last_ts) >= _CHECK_INTERVAL_SECONDS
        except (ValueError, OSError):
            return True

    def record_check(self) -> None:
        """Write the current timestamp so we don't re-check within 24 h."""
        self._state_dir.mkdir(parents=True, exist_ok=True)
        self._timestamp_path().write_text(str(time.time()))

    # ------------------------------------------------------------------
    # Version check
    # ------------------------------------------------------------------

    def check_for_update(self) -> UpdateResult:
        """Query GitHub tags and compare to the locally installed version.

        Returns an :class:`UpdateResult` that is safe to inspect regardless
        of network conditions — errors are captured, never raised.
        """
        local = get_local_version()
        try:
            with httpx.Client(timeout=5.0) as client:
                resp = client.get(_GITHUB_TAGS_URL)
                resp.raise_for_status()
                tags = resp.json()

            # Parse all valid semver tags and find the highest
            versions: list[tuple[int, int, int]] = []
            tag_map: dict[tuple[int, int, int], str] = {}
            for tag in tags:
                name: str = tag.get("name", "")
                try:
                    parsed = parse_semver(name)
                    versions.append(parsed)
                    # Store without leading 'v'
                    tag_map[parsed] = name.lstrip("v")
                except ValueError:
                    continue

            if not versions:
                return UpdateResult(
                    available=False,
                    local_version=local,
                    remote_version=None,
                    error=None,
                )

            highest = max(versions)
            remote_str = tag_map[highest]

            if is_newer(remote_str, local):
                return UpdateResult(
                    available=True,
                    local_version=local,
                    remote_version=remote_str,
                    error=None,
                )

            return UpdateResult(
                available=False,
                local_version=local,
                remote_version=remote_str,
                error=None,
            )

        except (httpx.HTTPError, httpx.TimeoutException, httpx.ConnectError) as exc:
            return UpdateResult(
                available=False,
                local_version=local,
                remote_version=None,
                error=str(exc),
            )
        except Exception as exc:
            return UpdateResult(
                available=False,
                local_version=local,
                remote_version=None,
                error=f"Unexpected error: {exc}",
            )

    # ------------------------------------------------------------------
    # Install method detection
    # ------------------------------------------------------------------

    def detect_install_method(self) -> str:
        """Detect whether RDT was installed via uv, pipx, or something else.

        Returns ``"uv"``, ``"pipx"``, or ``"unknown"``.
        """
        # Try uv first
        try:
            result = subprocess.run(
                ["uv", "tool", "list"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0 and _PACKAGE_NAME in result.stdout:
                return "uv"
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

        # Try pipx
        try:
            result = subprocess.run(
                ["pipx", "list"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0 and _PACKAGE_NAME in result.stdout:
                return "pipx"
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

        return "unknown"

    # ------------------------------------------------------------------
    # Perform update
    # ------------------------------------------------------------------

    def perform_update(self) -> UpdateOutcome:
        """Run the appropriate upgrade command as a subprocess.

        Returns an :class:`UpdateOutcome` with the result.
        """
        method = self.detect_install_method()

        if method == "unknown":
            return UpdateOutcome(
                success=False,
                method=method,
                new_version=None,
                error=(
                    "Could not detect install method. "
                    "Please update manually with:\n"
                    f"  uv tool upgrade {_PACKAGE_NAME}\n"
                    "  or\n"
                    f"  pipx upgrade {_PACKAGE_NAME}"
                ),
            )

        cmd_map = {
            "uv": ["uv", "tool", "upgrade", _PACKAGE_NAME],
            "pipx": ["pipx", "upgrade", _PACKAGE_NAME],
        }
        cmd = cmd_map[method]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,
            )
            if result.returncode == 0:
                return UpdateOutcome(
                    success=True,
                    method=method,
                    new_version=None,  # caller can re-check if needed
                    error=None,
                )
            return UpdateOutcome(
                success=False,
                method=method,
                new_version=None,
                error=result.stderr or result.stdout or "Unknown error",
            )
        except Exception as exc:
            return UpdateOutcome(
                success=False,
                method=method,
                new_version=None,
                error=str(exc),
            )
