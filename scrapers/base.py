#!/usr/bin/env python3
"""Base class for all scraper plugins."""

from pathlib import Path


class ScraperBase:
    """All scrapers should inherit from this class."""

    def __init__(self, verbose: bool = True):
        """Initializes the scraper.

        Args:
            verbose: Flag for enabling detailed output.
        """
        self.name = "Base"
        self.verbose = verbose

    def run(self, config: dict, output_dir: Path):
        """The main method to run the scraper. This must be implemented by subclasses.

        Args:
            config: The scraper-specific configuration dictionary.
            output_dir: The base directory Path object for raw output.
        """
        raise NotImplementedError(
            "The 'run' method must be implemented by the scraper plugin."
        )
