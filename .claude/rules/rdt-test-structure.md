## Test Structure Pattern

**Pytest markers, shared fixtures, and coverage requirements.**

### Test Organization

```
tests/
├── conftest.py              # Shared fixtures (session-scoped)
├── test_database.py         # Database deduplication tests
├── test_file_converter.py   # File conversion tests
├── test_file_splitter.py    # File splitting tests
├── test_plugin_loading.py   # Plugin architecture tests
├── test_rss_scraper.py      # RSS scraper tests
├── test_scheduler.py        # Scheduler tests
├── test_scrapers.py         # Multi-scraper tests
├── test_tui_integration.py  # TUI app integration tests
├── test_tui_screens.py      # TUI screen rendering tests
├── test_tui_widgets.py      # TUI widget tests
├── test_utils.py            # Utility function tests
└── README.md
```

### Pytest Markers

Defined in `pytest.ini`:

- `@pytest.mark.unit` — Fast, no I/O
- `@pytest.mark.integration` — DB, network, file system
- `@pytest.mark.database` — Tests requiring database
- `@pytest.mark.slow` — Tests taking >5 seconds
- `@pytest.mark.tui` — TUI screen and widget tests

### Running Tests

```bash
uv run pytest -q                              # All tests (163)
uv run pytest -m "unit" -q                    # Unit tests only
uv run pytest -m "tui" -q                     # TUI tests only
uv run pytest -q --cov=. --cov-fail-under=80  # With coverage
```

### TUI Tests

TUI tests use `pytest.importorskip("textual")` to skip gracefully if Textual isn't installed. Async mode is `asyncio_mode = auto` in pytest.ini.

```python
import pytest
textual = pytest.importorskip("textual")

@pytest.mark.tui
async def test_dashboard_renders():
    """Test that dashboard screen mounts correctly."""
    from research_digest_tui import ResearchDigestApp
    async with ResearchDigestApp().run_test() as pilot:
        assert pilot.app.screen is not None
```

### Coverage

**Minimum:** 80% (`--cov-fail-under=80`). Coverage config in `pytest.ini` under `[coverage:run]` and `[coverage:report]`.

### Test Naming

```python
# Format: test_{function}_{scenario}_{expected}
def test_generate_filename_spaces_replaced_with_underscores():
    assert generate_safe_filename("Hello World") == "hello_world"
```

### Mocking Rules

**Mock external dependencies only:** HTTP requests, file I/O, database calls, external APIs.
**Don't mock:** Pure functions, internal logic, plugin loading.

```python
from unittest.mock import patch, MagicMock

@pytest.mark.unit
@patch("scrapers.hn_scraper.requests.get")
def test_fetch_hn_item_retry(mock_get):
    mock_get.side_effect = [requests.Timeout, MagicMock(status_code=200)]
```

### Common Mistakes

- Not marking tests — can't filter by type
- Not using `tmp_path` — pollutes project directory
- Mocking internal functions — brittle tests
- Testing implementation, not behavior — fragile tests
