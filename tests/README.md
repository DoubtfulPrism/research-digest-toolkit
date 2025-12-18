# Test Suite for Research Digest Toolkit

This directory contains automated tests for the Research Digest Toolkit. The test suite uses `pytest` for test execution and `pytest-cov` for coverage reporting.

## Test Statistics

- **Total Tests:** 86
- **Test Modules:** 4
- **Coverage:** 42% overall (core modules: 89-100%)

## Test Organization

### Test Modules

| Module | Tests | Coverage | Description |
|--------|-------|----------|-------------|
| `test_database.py` | 15 | 89% | Database deduplication and state tracking |
| `test_utils.py` | 35 | 100% | Utility functions (filename, HTML, saving) |
| `test_scrapers.py` | 20 | 100% | Base scraper class and plugin contract |
| `test_plugin_loading.py` | 16 | 99% | Plugin discovery and orchestration |

### Test Categories

Tests are organized by pytest markers:

- `@pytest.mark.unit` - Unit tests for individual functions (67 tests)
- `@pytest.mark.integration` - Integration tests for workflows (7 tests)
- `@pytest.mark.database` - Database-specific tests (6 tests)
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

### Core Modules (High Priority)

| Module | Coverage | Notes |
|--------|----------|-------|
| `database.py` | 89% | Missing: Error handling edge cases |
| `utils.py` | 83% | Missing: Error paths in save_document |
| `scrapers/base.py` | 100% | Fully covered |
| `research_digest.py` | 48% | Missing: CLI and processing pipelines |

### Scraper Plugins (Lower Priority)

| Module | Coverage | Notes |
|--------|----------|-------|
| `scrapers/arxiv_scraper.py` | 37% | Needs integration tests |
| `scrapers/hn_scraper.py` | 31% | Needs integration tests |
| `scrapers/reddit_scraper.py` | 23% | Needs integration tests |
| `scrapers/rss_scraper.py` | 20% | Needs integration tests |

### Utility Tools (Not Currently Tested)

- `file_converter.py` - 0% coverage
- `file_splitter.py` - 0% coverage
- `obsidian_prep.py` - 0% coverage
- `thread_reader.py` - 0% coverage
- `web_scraper.py` - 0% coverage
- `youtube_transcript.py` - 0% coverage

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

**Last Updated:** 2025-12-18
**Test Framework:** pytest 9.0.2
**Python Version:** 3.14.2
