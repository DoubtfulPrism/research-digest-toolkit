#!/usr/bin/env python3
"""CLI entry point for the Research Digest Toolkit.

Provides XDG-style config discovery and the ``main()`` function referenced by
the ``Research_Toolkit`` console script in pyproject.toml.
"""

import shutil
from pathlib import Path


def _cwd_config() -> Path:
    """Return the config path relative to the current working directory."""
    return Path.cwd() / "research_config.yaml"


def _home_config() -> Path:
    """Return the config path in the user's home directory."""
    return Path.home() / ".research_digest" / "research_config.yaml"


def _bundled_default() -> Path:
    """Return the path to the bundled default config inside the package."""
    return Path(__file__).parent / "data" / "research_config.default.yaml"


def _find_or_create_config() -> Path:
    """Locate or create the user's research_config.yaml.

    Discovery order:
    1. ``./research_config.yaml`` (CWD — dev/project-local override)
    2. ``~/.research_digest/research_config.yaml`` (user home)
    3. First run: copy bundled default to home location and return that path

    Returns:
        Path to the config file to use.
    """
    cwd = _cwd_config()
    if cwd.exists():
        return cwd

    home = _home_config()
    if home.exists():
        return home

    # First run — seed from bundled default
    home.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(_bundled_default(), home)
    return home


def main() -> None:
    """Launch the Research Digest TUI with auto-discovered config."""
    from rdt.tui.app import ResearchDigestApp

    config_path = _find_or_create_config()
    app = ResearchDigestApp(config_path=config_path)
    app.run()
