import unittest
from pathlib import Path

class TestPackageStructure(unittest.TestCase):
    """Smoke tests for the new RDT package structure."""

    def test_shared_imports(self):
        """Verify that shared modules can be imported from rdt.shared."""
        try:
            from rdt.shared import database
            from rdt.shared import utils
            from rdt.shared import config_models
            from rdt.shared import rich_utils
            from rdt.shared import http_client
            from rdt.shared import scheduler_utils
            from rdt.shared import obsidian
            from rdt.shared import credentials
            from rdt.shared import db_init
            from rdt.shared import retry_utils
            from rdt.shared import analysis
        except ImportError as e:
            self.fail(f"Shared module import failed: {e}")

    def test_tui_imports(self):
        """Verify that TUI modules can be imported from rdt.tui."""
        try:
            from rdt.tui import app
            from rdt.tui import screens
            from rdt.tui import services
        except ImportError as e:
            self.fail(f"TUI module import failed: {e}")

    def test_orchestrator_import(self):
        """Verify that the orchestrator can be imported from rdt.digest."""
        try:
            from rdt import digest
            from rdt.digest import ResearchDigest
        except ImportError as e:
            self.fail(f"Orchestrator import failed: {e}")

    def test_cli_import(self):
        """Verify that the CLI can be imported from rdt.cli."""
        try:
            from rdt.cli import main
        except ImportError as e:
            self.fail(f"CLI import failed: {e}")

if __name__ == "__main__":
    unittest.main()
