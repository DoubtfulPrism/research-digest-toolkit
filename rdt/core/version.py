#!/usr/bin/env python3
"""Version parsing and comparison utilities for RDT.

Pure logic — no network, no side-effects. Safe to call from any context.
"""

from __future__ import annotations

import re
from pathlib import Path
from importlib.metadata import version as metadata_version


_SEMVER_RE = re.compile(r"^v?(\d+)\.(\d+)\.(\d+)$")


def parse_semver(tag: str) -> tuple[int, int, int]:
    """Parse a semver string into a (major, minor, patch) tuple.

    Accepts optional leading ``v`` (e.g. ``"v1.2.3"``).
    Raises ``ValueError`` for non-conforming strings such as ``"beta"``
    or incomplete versions like ``"1.2"``.
    """
    m = _SEMVER_RE.match(tag.strip())
    if m is None:
        raise ValueError(f"Not a valid semver string: {tag!r}")
    return int(m.group(1)), int(m.group(2)), int(m.group(3))


def is_newer(remote: str, local: str) -> bool:
    """Return ``True`` if *remote* is a higher version than *local*."""
    return parse_semver(remote) > parse_semver(local)


def _find_pyproject_toml() -> Path | None:
    """Walk up from this file to find the project's ``pyproject.toml``."""
    current = Path(__file__).resolve().parent
    for _ in range(5):  # max 5 levels up
        candidate = current / "pyproject.toml"
        if candidate.exists():
            return candidate
        current = current.parent
    return None


def get_local_version() -> str:
    """Return the locally installed RDT version string.

    Resolution order:
    1. ``importlib.metadata`` (works when pip/uv/pipx installed).
    2. Parse ``version`` field from the nearest ``pyproject.toml`` (dev installs).
    3. Fall back to ``"0.0.0"`` if nothing works.
    """
    try:
        return metadata_version("research-digest-toolkit")
    except Exception:
        pass

    pyproject = _find_pyproject_toml()
    if pyproject is not None:
        try:
            text = pyproject.read_text()
            m = re.search(r'version\s*=\s*"([^"]+)"', text)
            if m:
                return m.group(1)
        except Exception:
            pass

    return "0.0.0"
