# Contributing to Research Digest Toolkit

Thanks for your interest in contributing! This project was vibecoded (AI-assisted development), and we welcome contributions from both humans and human+AI collaborations.

## 🚨 **MANDATORY: Development Standards**

All contributions **MUST** follow our quality standards:

1. ✅ **Test-Driven Development (TDD)** - Tests written BEFORE implementation
2. ✅ **100% Test Pass Rate** - All tests must pass
3. ✅ **Code Quality** - Black formatting, isort imports, ruff linting
4. ✅ **Coverage Requirements** - ≥90% coverage for new code
5. ✅ **Pre-commit Hooks** - Automated quality checks

**📚 Required Reading:**
- [TDD Workflow](.github/TDD_WORKFLOW.md) - **Mandatory workflow for ALL code changes**
- [Development Setup](.github/DEVELOPMENT_SETUP.md) - Setup guide with tools
- [CI/CD Documentation](.github/CI_SETUP.md) - Understanding automated checks

**No exceptions. Quality is non-negotiable.**

---

## 🤖 Vibecoding Welcome

This project was built with AI assistance, and we **encourage** contributors to use AI tools if helpful:
- Claude, ChatGPT, GitHub Copilot, etc.
- Just be clear about what's AI-assisted vs. human-written
- **Test thoroughly - AI can make mistakes!**
- AI-generated code still requires TDD workflow

## 🎯 How to Contribute

### Reporting Issues

**Found a bug?**
1. Check if it's already reported
2. Include:
   - Your OS and Python version
   - Steps to reproduce
   - Expected vs. actual behavior
   - Error messages (if any)

**Have a feature idea?**
1. Open an issue first to discuss
2. Explain the use case
3. Why it fits this project's scope

### Pull Requests

**Setup (First Time Only):**
```bash
# 1. Fork the repository on GitHub
# 2. Clone your fork
git clone https://github.com/YOUR_USERNAME/Scripts.git
cd Scripts

# 3. Install development dependencies
pip install -r requirements.txt
pip install pre-commit black isort ruff bandit pytest pytest-cov

# 4. Install pre-commit hooks (REQUIRED)
pre-commit install

# 5. Verify setup
pytest tests/ -v
```

**Before starting:**
1. Read [TDD_WORKFLOW.md](.github/TDD_WORKFLOW.md) - **MANDATORY**
2. Open an issue to discuss major changes
3. Create a branch: `git checkout -b feature/your-feature`

**While developing (TDD Cycle):**
1. ✅ **RED** - Write failing test first
2. ✅ **GREEN** - Write minimal code to pass test
3. ✅ **REFACTOR** - Improve code while tests stay green
4. ✅ **REPEAT** - Continue for all features and edge cases

**Pre-commit checklist (REQUIRED):**
```bash
# Run full quality checks
pytest tests/ -v --cov=. --cov-report=term-missing
black .
isort . --profile black
ruff check .

# All must pass before committing
```

**When submitting:**
```bash
# Pre-commit hooks run automatically
git add .
git commit -m "feat: Add Mastodon scraping with tests"

# Push (triggers more checks)
git push origin feature/your-feature

# Create PR on GitHub
# CI must pass before merge
```

**PR Requirements:**
- ✅ All tests pass (100% pass rate)
- ✅ New code has ≥90% test coverage
- ✅ No linting errors
- ✅ Code formatted with black/isort
- ✅ Documentation updated
- ✅ CI/CD checks pass

## 📝 Code Style

### Python
- Follow PEP 8
- Use type hints where helpful
- Docstrings for all public functions
- Error handling with specific exceptions

**Example:**
```python
def process_content(url: str, verbose: bool = True) -> dict:
    """
    Process content from URL.

    Args:
        url: Source URL
        verbose: Whether to print progress

    Returns:
        Dictionary with processed data

    Raises:
        ValueError: If URL is invalid
        RequestException: If fetch fails
    """
    # Implementation
```

### Shell Scripts
- Use `set -e` for safety
- Check for required commands
- Provide helpful error messages

### Documentation
- Update README.md if adding features
- Add examples to AUTOMATION_GUIDE.md
- Keep PROJECT_README.md current

## 🔍 Areas for Contribution

### High Priority
- [ ] New source integrations (Mastodon, GitHub Trending, etc.)
- [ ] Increase test coverage (currently 42% overall, core modules 85%+)
- [ ] Bug fixes with test cases
- [ ] Documentation improvements
- [ ] Auto-tagging improvements for specific domains

### Medium Priority
- [ ] Integration tests for scraper plugins
- [ ] Performance optimizations with benchmarks
- [ ] Better error messages
- [ ] Additional output formats

### Low Priority
- [ ] Web UI
- [ ] Docker container
- [ ] Additional language support

## 🧪 Testing (MANDATORY)

**⚠️ CRITICAL: Tests must be written BEFORE implementation (TDD)**

See [TDD_WORKFLOW.md](.github/TDD_WORKFLOW.md) for complete workflow.

**Test requirements:**
```bash
# 1. Write test first (RED)
# tests/test_new_feature.py
def test_new_feature():
    result = new_feature("input")
    assert result == "expected"

# 2. Run test - should FAIL
pytest tests/test_new_feature.py -v
# FAILED (as expected)

# 3. Implement minimal code (GREEN)
# my_module.py
def new_feature(input_str):
    return "expected"

# 4. Run test - should PASS
pytest tests/test_new_feature.py -v
# PASSED

# 5. Add edge cases and refactor
```

**Coverage requirements:**
- ✅ New code: ≥90% coverage required
- ✅ Core modules: Maintain ≥85% coverage
- ✅ Overall project: Don't reduce existing coverage

**Test types:**
```python
@pytest.mark.unit       # Unit tests (most common)
@pytest.mark.integration # Integration tests
@pytest.mark.slow       # Tests taking >5 seconds
```

**Quality gates (all must pass):**
```bash
# Run before EVERY commit
pytest tests/ -v                          # All tests pass
pytest tests/ --cov=. --cov-report=term   # Check coverage
black . && isort . --profile black        # Format code
ruff check .                              # No lint errors
```

## 📚 Adding New Sources

Thanks to the new plugin architecture, adding a new scraper is the easiest way to contribute.

**1. Create Your Plugin File:**
- Create a new file in the `scrapers/` directory (e.g., `scrapers/mastodon_scraper.py`).

**2. Build the Scraper Class:**
- Your class must inherit from `scrapers.base.ScraperBase`.
- It must have a `name` attribute (which will be the key used in the config file).
- It must have a `run(self, config, output_dir)` method.

**⚠️ IMPORTANT: Write tests FIRST before implementing plugin!**

**Step 1: Write Tests First (tests/test_my_scraper.py):**
```python
import pytest
from pathlib import Path
from scrapers.my_scraper import MyScraper

@pytest.mark.unit
def test_my_scraper_initialization():
    """Test MyScraper initializes correctly."""
    scraper = MyScraper(verbose=False)
    assert scraper.name == "MySource"
    assert scraper.verbose is False

@pytest.mark.integration
def test_my_scraper_run(tmp_path):
    """Test MyScraper.run() processes items correctly."""
    scraper = MyScraper(verbose=False)
    config = {"api_key": "test_key", "enabled": True}
    output_dir = tmp_path / "output"

    scraper.run(config, output_dir)

    # Verify files created
    assert (output_dir / "mysource").exists()
    # Add more assertions...
```

**Step 2: Run Tests (should FAIL):**
```bash
pytest tests/test_my_scraper.py -v
# FAILED - MyScraper doesn't exist yet
```

**Step 3: Implement Plugin (scrapers/my_scraper.py):**
```python
from .base import ScraperBase
from pathlib import Path
import utils
import database

class MyScraper(ScraperBase):
    """Scraper for MySource API."""

    def __init__(self, verbose: bool = True):
        super().__init__(verbose)
        self.name = "MySource"

    def run(self, config: dict, output_dir: Path):
        """
        Scrape content from MySource.

        Args:
            config: Configuration dict with api_key, etc.
            output_dir: Base output directory
        """
        if self.verbose:
            print(f"🔥 Scraping {self.name}...")

        # Implementation...
        api_key = config.get("api_key")
        # Fetch, process, save...
```

**Step 4: Run Tests (should PASS):**
```bash
pytest tests/test_my_scraper.py -v
# PASSED ✓
```

**Step 5: Check Coverage:**
```bash
pytest tests/test_my_scraper.py --cov=scrapers.my_scraper --cov-report=term-missing
# Must be ≥90% coverage
```

**3. Add Configuration to `research_config.yaml`:**
- Add a new entry under the `scrapers` key in `research_config.yaml`. The key name must be the lowercase version of your class's `name`.

```yaml
scrapers:
  mysource:  # Corresponds to `name = "MySource"`
    enabled: true
    api_key: "your_secret_key"
  # ... other scrapers
```

That's it! The `research_digest.py` script will automatically discover and run your new plugin.

## 🔐 Security

**If you find a security issue:**
- Do NOT open a public issue
- Email: [maintainer email] (replace with yours)
- Include details and potential impact

**For code submissions:**
- No credentials in code
- Use environment variables for sensitive data
- Validate all user inputs
- Be careful with `subprocess` calls

## 📋 Commit Messages

Use clear, descriptive messages:

```
Add: New feature description
Fix: Bug description
Update: Documentation improvements
Refactor: Code restructuring
```

Examples:
```
Add: Mastodon instance scraping support
Fix: PDF conversion failing on non-ASCII filenames
Update: AUTOMATION_GUIDE with systemd examples
Refactor: Extract common HTTP handling to utils
```

## 🤝 Code of Conduct

**Be respectful:**
- Respectful communication
- Constructive feedback
- Assume good intentions
- Help beginners

**Vibecoding specific:**
- It's OK to use AI tools
- Be transparent about AI assistance
- AI-generated code still needs human review
- Test thoroughly - don't trust AI blindly

## ❓ Questions?

- Open an issue for general questions
- Check existing documentation first
- Be specific about your use case

## 🙏 Recognition

Contributors will be:
- Listed in PROJECT_README.md
- Credited in release notes
- Appreciated! 🎉

---

**Development Approach**: This project embraces vibecoding (AI-assisted development). Whether you code solo, with AI, or collaborate with others, quality contributions are welcome!
