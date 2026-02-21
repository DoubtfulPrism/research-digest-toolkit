## Test Structure Pattern

**Pytest markers, shared fixtures, and coverage requirements for the Research Digest Toolkit.**

### Test Organization

```
tests/
├── conftest.py              # Shared fixtures (session-scoped)
├── test_database.py         # Database deduplication tests
├── test_plugin_loading.py   # Plugin architecture tests
├── test_utils.py            # Utility function tests
└── README.md                # Test documentation
```

### Pytest Markers

Use markers to categorize tests by type and execution speed:

```python
import pytest

@pytest.mark.unit
def test_filename_generation():
    """Fast, isolated test with no external dependencies."""
    result = generate_safe_filename("Test Article")
    assert result == "test_article"

@pytest.mark.integration
@pytest.mark.database
def test_url_deduplication(tmp_path):
    """Test requiring database or external resources."""
    db = Database(tmp_path / "test.db")
    assert db.is_new_item("https://example.com", "Title")

@pytest.mark.slow
def test_full_pipeline():
    """End-to-end test that takes >5 seconds."""
    result = run_full_digest()
    assert result.success
```

**Available markers (defined in pytest.ini):**
- `@pytest.mark.unit` - Unit tests (fast, no I/O)
- `@pytest.mark.integration` - Integration tests (DB, network)
- `@pytest.mark.database` - Tests requiring database
- `@pytest.mark.slow` - Tests taking >5 seconds

### Shared Fixtures (conftest.py)

```python
# tests/conftest.py
import pytest
from pathlib import Path

@pytest.fixture(scope="session")
def project_root():
    """Returns the project root directory."""
    return Path(__file__).parent.parent

@pytest.fixture
def sample_html():
    """Reusable HTML content for testing HTML cleaning."""
    return """
    <div class="article">
        <h1>Test Article</h1>
        <p>Content with <a href="https://example.com">link</a>.</p>
    </div>
    """

@pytest.fixture
def sample_markdown():
    """Reusable markdown content for testing."""
    return """# Test Article

## Introduction
...
"""
```

**Fixture scopes:**
- `scope="session"` - Created once per test session (expensive setup)
- `scope="module"` - Created once per test module
- `scope="function"` - Created per test (default)

### Running Tests

```bash
# All tests
pytest -q

# Unit tests only (fast)
pytest -m "unit" -q

# Integration tests
pytest -m "integration" -q

# Skip slow tests
pytest -m "not slow" -q

# With coverage (minimum 80%)
pytest -q --cov=. --cov-fail-under=80
```

### Coverage Requirements

**Minimum coverage:** 80% (enforced by `--cov-fail-under=80`)

**Coverage configuration (pyproject.toml):**

```toml
[tool.coverage.run]
omit = [
    "tests/*",
    "venv/*",
    "__pycache__/*",
    "research_digest/*",  # Output directory
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
    "@abstractmethod",
]
```

**Current coverage (as of last run):**
- `database.py` - 89%
- `utils.py` - 83%
- `scrapers/base.py` - 100%
- Overall: 89%+

### Test Naming Convention

```python
# Format: test_{function}_{scenario}_{expected}
def test_generate_filename_spaces_replaced_with_underscores():
    """Test filename generation with spaces."""
    assert generate_safe_filename("Hello World") == "hello_world"

def test_is_new_item_duplicate_url_returns_false(tmp_path):
    """Test deduplication with duplicate URL."""
    db = Database(tmp_path / "test.db")
    db.add_item("https://example.com", "Title")
    assert db.is_new_item("https://example.com", "Different Title") is False
```

### Mock External Dependencies in Unit Tests

```python
from unittest.mock import patch, MagicMock

@pytest.mark.unit
@patch("scrapers.hn_scraper.requests.get")
def test_fetch_hn_item_retry_on_timeout(mock_get):
    """Unit test with mocked network call."""
    mock_get.side_effect = [requests.Timeout, MagicMock(status_code=200)]
    # Test retry logic without actual network I/O
```

**What to mock in unit tests:**
- HTTP requests (`requests.get`, `httpx.Client.get`)
- File I/O (`open`, `Path.read_text`)
- Database calls (use `tmp_path` fixture or mock)
- External APIs

**What NOT to mock:**
- Pure functions (filename generation, HTML cleaning)
- Internal logic (retry decorators, plugin loading)

### Integration Tests

Integration tests use real resources (databases, file systems) but avoid external APIs:

```python
@pytest.mark.integration
@pytest.mark.database
def test_database_deduplication(tmp_path):
    """Integration test with real SQLite database."""
    db_path = tmp_path / "test.db"
    db = Database(db_path)

    # Add item
    db.add_item("https://example.com", "Title")

    # Verify deduplication
    assert db.is_new_item("https://example.com", "Title") is False
    assert db.is_new_item("https://different.com", "Title") is True
```

### Pytest Configuration

**pytest.ini:**

```ini
[tool.pytest.ini_options]
minversion = "7.0"
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "-v",
    "--strict-markers",
    "--tb=short",
    "--cov=.",
    "--cov-report=term-missing",
    "--cov-report=html",
]
markers = [
    "unit: Unit tests for individual functions",
    "integration: Integration tests for workflows",
    "slow: Tests that take longer to run",
    "database: Tests that interact with database",
]
```

### Common Mistakes

- Not marking tests with `@pytest.mark.unit` or `@pytest.mark.integration` - can't filter by type
- Not using `tmp_path` for temporary files - pollutes project directory
- Mocking internal functions instead of external dependencies - brittle tests
- Not cleaning up resources in integration tests - test pollution
- Testing implementation instead of behavior - fragile tests

### Test Output

```bash
# Minimal output (preferred for CI)
pytest -q
.......                                                              [100%]
7 passed in 0.23s

# Verbose output (for debugging)
pytest -v
tests/test_database.py::test_is_new_item_new_url_returns_true PASSED  [ 14%]
tests/test_database.py::test_is_new_item_duplicate_url_returns_false PASSED  [ 28%]
...
```
