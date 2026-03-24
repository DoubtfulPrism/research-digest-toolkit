# Test Suite for Research Digest Toolkit

This directory contains automated tests for the Research Digest Toolkit. The test suite uses `pytest` for test execution and `pytest-cov` for coverage reporting.

## Test Statistics

- **Total Tests:** 388
- **Test Modules:** 23
- **Coverage:** 80%+ overall

## Test Organization

### Test Modules

| Module | Description |
|--------|-------------|
| `test_analysis.py` | Trend analysis with Polars/scikit-learn |
| `test_config_service.py` | ConfigService YAML/Pydantic integration |
| `test_credentials.py` | Credential management |
| `test_database.py` | Database deduplication and state tracking |
| `test_db_init.py` | Database initialization |
| `test_file_converter.py` | Document format conversion |
| `test_file_splitter.py` | File splitting for NotebookLM |
| `test_http_client.py` | HTTPX + DiskCache transport (100%) |
| `test_plugin_loading.py` | Plugin discovery and orchestration |
| `test_retry_utils.py` | Tenacity retry decorators (100%) |
| `test_rich_utils.py` | Rich console output helpers (100%) |
| `test_rss_scraper.py` | RSS/Atom feed scraper |
| `test_runner_service.py` | Scraper subprocess runner |
| `test_scheduler.py` | Schedule library wrapper |
| `test_scheduler_service.py` | SchedulerService configuration |
| `test_scrapers.py` | Base scraper class and plugin contract |
| `test_tui_integration.py` | TUI app integration (37 tests) |
| `test_tui_screens.py` | TUI screen unit tests |
| `test_tui_services.py` | TUI service layer tests |
| `test_tui_widgets.py` | ScraperCard widget tests (8 tests) |
| `test_utils.py` | Utility functions (100%) |

### Test Categories

Tests are organized by pytest markers:

- `@pytest.mark.unit` - Unit tests for individual functions
- `@pytest.mark.integration` - Integration tests for workflows
- `@pytest.mark.database` - Database-specific tests
- `@pytest.mark.tui` - TUI screen, widget, and interaction tests
- `@pytest.mark.slow` - Long-running tests (0 currently)

## Running Tests

### Basic Usage

```bash
# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run specific test file
pytest tests/test_database.py

# Run specific test class
pytest tests/test_database.py::TestDatabaseInit

# Run specific test
pytest tests/test_database.py::TestDatabaseInit::test_init_db_creates_table
```

### Coverage Reports

```bash
# Run tests with coverage report
pytest tests/ --cov=. --cov-report=term-missing

# Generate HTML coverage report
pytest tests/ --cov=. --cov-report=html
# Open htmlcov/index.html in browser

# Combine terminal and HTML reports
pytest tests/ --cov=. --cov-report=term-missing --cov-report=html
```

### Filter by Markers

```bash
# Run only unit tests
pytest tests/ -m unit

# Run only integration tests
pytest tests/ -m integration

# Run only database tests
pytest tests/ -m database

# Exclude slow tests
pytest tests/ -m "not slow"
```

### Other Useful Options

```bash
# Stop on first failure
pytest tests/ -x

# Show local variables in tracebacks
pytest tests/ -l

# Run tests in parallel (requires pytest-xdist)
pytest tests/ -n auto

# Quiet mode (less verbose)
pytest tests/ -q

# Show test durations
pytest tests/ --durations=10
```

## Test Coverage by Module

### Core Modules

| Module | Coverage | Notes |
|--------|----------|-------|
| `utils.py`, `retry_utils.py`, `rich_utils.py` | 100% | Fully covered |
| `http_client.py` | 100% | Sync and async cache transports |
| `scrapers/base.py` | 100% | Plugin architecture |
| `scheduler_utils.py` | 99% | Schedule parsing and validation |
| `scraper_management.py` | 99% | TUI scraper management screen |
| `scheduler.py` (TUI) | 98% | TUI scheduler screen |
| `history.py` (TUI) | 96% | TUI history screen |
| `analysis.py` | 96% | Trend analysis |
| `config_models.py` | 96% | Pydantic configuration models |
| `database.py` | 89% | Deduplication and state tracking |
| `scrapers/reddit_scraper.py` | 88% | Reddit scraper |
| `scrapers/hn_scraper.py` | 84% | HackerNews scraper |
| `file_splitter.py` | 86% | File splitting for NotebookLM |
| `scrapers/rss_scraper.py` | 94% | RSS/Atom feed scraper |
| `research_digest.py` | 50% | CLI orchestrator (subprocess-heavy) |
| `file_converter.py` | 47% | Document format conversion |

## Test Fixtures

Common fixtures are defined in `conftest.py`:

- `project_root` - Returns the project root directory
- `sample_html` - Sample HTML for testing HTML cleaning
- `sample_markdown` - Sample markdown content

Module-specific fixtures:

- `temp_db` (test_database.py) - Temporary database for testing
- `temp_config` (test_plugin_loading.py) - Temporary YAML config
- `tmp_path` (pytest built-in) - Temporary directory for each test

## Writing New Tests

### Test Structure

```python
import pytest
from pathlib import Path

@pytest.mark.unit
class TestMyFeature:
    """Tests for my feature."""

    def test_basic_functionality(self):
        """Test basic functionality with happy path."""
        # Arrange
        input_data = "test"

        # Act
        result = my_function(input_data)

        # Assert
        assert result == "expected"

    def test_edge_case(self):
        """Test edge case handling."""
        # Test edge cases, error handling, etc.
        pass

@pytest.mark.integration
class TestMyWorkflow:
    """Integration tests for complete workflows."""

    def test_end_to_end(self, tmp_path):
        """Test complete workflow."""
        # Test realistic scenarios
        pass
```

### Test Naming Conventions

- Test files: `test_<module_name>.py`
- Test classes: `Test<FeatureName>`
- Test functions: `test_<what_it_tests>`

### Best Practices

1. **Isolation** - Each test should be independent
2. **Fixtures** - Use fixtures for setup/teardown
3. **Temp Files** - Use `tmp_path` fixture for file operations
4. **Markers** - Tag tests with appropriate markers
5. **Docstrings** - Include clear docstrings explaining what's tested
6. **Assertions** - One logical assertion per test (when practical)
7. **Edge Cases** - Test error conditions, empty inputs, edge cases

## Continuous Integration

The test suite is designed to run in CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Install dependencies
  run: pip install -r requirements.txt

- name: Run tests
  run: pytest tests/ --cov=. --cov-report=xml

- name: Upload coverage
  uses: codecov/codecov-action@v3
```

## Known Issues and Warnings

1. **DeprecationWarning (Python 3.12+)**: SQLite datetime adapter deprecation
   - Impact: Minimal (warnings only)
   - Solution: Will be addressed in future update

## Future Test Improvements

1. **Increase Coverage**
   - Add integration tests for scraper plugins
   - Test CLI argument parsing
   - Test processing pipeline (obsidian_prep)

2. **Performance Tests**
   - Add benchmarks for database operations
   - Test with large datasets (1000+ items)

3. **Mocking External Services**
   - Mock HTTP requests for scrapers
   - Mock API calls (ArXiv, Reddit, HN)

4. **Edge Case Coverage**
   - Network failures
   - Malformed API responses
   - Corrupted database recovery

## Bug Discoveries

The test suite has already found real bugs:

1. **Missing `import sys` in database.py** - Fixed
   - Error handling used `sys.stderr` without importing `sys`
   - Discovered by: `test_item_exists_handles_database_errors_gracefully`

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Pytest Coverage Plugin](https://pytest-cov.readthedocs.io/)
- [Python Testing Best Practices](https://docs.python-guide.org/writing/tests/)

---

**Last Updated:** 2026-03-24
**Test Framework:** pytest 9.0.2
**Python Version:** 3.14.3
