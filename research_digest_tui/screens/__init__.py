#!/usr/bin/env python3
"""TUI screens for the Research Digest application."""

from .configuration import Configuration
from .dashboard import Dashboard
from .history import History
from .logs import Logs
from .scheduler import Scheduler
from .scraper_management import ScraperManagement

__all__ = [
    "Configuration",
    "Dashboard",
    "History",
    "Logs",
    "Scheduler",
    "ScraperManagement",
]
