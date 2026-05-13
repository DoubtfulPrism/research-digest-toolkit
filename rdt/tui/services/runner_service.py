#!/usr/bin/env python3
"""RunnerService — executes scrapers as subprocesses and streams output."""

import shutil
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path
from subprocess import PIPE, STDOUT


def _build_scraper_cmd(config_path: Path, scraper_key: str | None) -> list[str]:
    """Build the subprocess command for running a scraper.

    Prefers the installed ``research-digest`` console script when available.
    Falls back to ``sys.executable rdt/digest.py`` for dev usage.

    Args:
        config_path: Path to the config YAML file.
        scraper_key: Config key for the scraper (e.g. ``"hackernews"``), or None for all.

    Returns:
        Command list suitable for ``subprocess.Popen``.
    """
    installed = shutil.which("research-digest")
    if installed:
        interpreter: list[str] = [installed]
    else:
        # Resolve repo root relative to this file's location
        repo_root = Path(__file__).resolve().parent.parent.parent.parent
        interpreter = [sys.executable, str(repo_root / "rdt" / "digest.py")]

    cmd = interpreter + ["--config", str(config_path)]
    if scraper_key:
        cmd.extend(["--scraper", scraper_key])
    return cmd


class RunnerService:
    """Wraps subprocess execution for TUI scraper runs.

    Designed to be called from a Textual @work(thread=True) worker.
    The on_line and on_complete callbacks should use app.call_from_thread()
    to safely schedule UI updates from the background thread.
    """

    _config_path: Path

    def __init__(self, config_path: Path) -> None:
        self._config_path = Path(config_path)

    def run_scraper(
        self,
        scraper_key: str | None,
        on_line: Callable[[str], None],
        on_complete: Callable[[bool], None],
    ) -> None:
        """Run a single scraper subprocess and stream its output.

        Args:
            scraper_key: Config key for the scraper (e.g. "hackernews", "rss").
            on_line: Called for each output line from the scraper process.
            on_complete: Called with True on success, False on failure.
        """
        cmd = _build_scraper_cmd(self._config_path, scraper_key)
        try:
            proc = subprocess.Popen(cmd, stdout=PIPE, stderr=STDOUT, text=True)
            if proc.stdout is not None:
                for line in proc.stdout:
                    on_line(line.rstrip())
            returncode = proc.wait()
            on_complete(returncode == 0)
        except Exception as e:
            on_line(f"Error: {e}")
            on_complete(False)
