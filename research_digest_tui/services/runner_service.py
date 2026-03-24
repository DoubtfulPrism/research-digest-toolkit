#!/usr/bin/env python3
"""RunnerService — executes scrapers as subprocesses and streams output."""

import subprocess
from collections.abc import Callable
from pathlib import Path
from subprocess import PIPE, STDOUT


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
        scraper_key: str,
        on_line: Callable[[str], None],
        on_complete: Callable[[bool], None],
    ) -> None:
        """Run a single scraper subprocess and stream its output.

        Args:
            scraper_key: Config key for the scraper (e.g. "hackernews", "rss").
            on_line: Called for each output line from the scraper process.
            on_complete: Called with True on success, False on failure.
        """
        cmd = [
            "python",
            "research_digest.py",
            "--config",
            str(self._config_path),
            "--scraper",
            scraper_key,
        ]
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
