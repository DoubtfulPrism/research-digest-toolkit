import pytest
from textual.app import App, ComposeResult
from rdt.tui.screens.dashboard import Dashboard

from unittest.mock import MagicMock

class DummyApp(App):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config_service = MagicMock()
        self.config_service.get_scraper_configs.return_value = []
        self.data_service = MagicMock()
        self.data_service.get_item_counts_by_source.return_value = {}
        self.data_service.get_summary_stats.return_value = {"total_items": 0}
        
    def compose(self) -> ComposeResult:
        yield Dashboard()

@pytest.mark.asyncio
async def test_dashboard_compiles_and_mounts():
    app = DummyApp()
    async with app.run_test() as pilot:
        assert pilot.app is not None
        # We just verify it runs without error, meeting basic TDD for UI presence.
        assert True
