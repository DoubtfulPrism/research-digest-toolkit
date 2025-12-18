# Development Environment Setup

This guide will help you set up a development environment with all quality tools and pre-commit hooks.

## 📋 Prerequisites

- Python 3.9 or higher
- Git
- pip

## 🚀 Quick Setup

### 1. Clone Repository
```bash
git clone https://github.com/YOUR_USERNAME/Scripts.git
cd Scripts
```

### 2. Create Virtual Environment (Recommended)
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
# Core dependencies
pip install -r requirements.txt

# Development dependencies
pip install pre-commit black isort ruff bandit mypy pydocstyle
```

### 4. Install Pre-Commit Hooks
```bash
# Install pre-commit hooks
pre-commit install

# Test the hooks
pre-commit run --all-files
```

### 5. Verify Setup
```bash
# Run tests
pytest tests/ -v

# Check formatting
black --check .
isort --check-only . --profile black

# Run linting
ruff check .

# Check security
bandit -r . -ll
```

If all checks pass, you're ready to develop! ✅

---

## 🛠️ Development Tools

### Code Formatting

**Black** - Uncompromising code formatter
```bash
# Format all files
black .

# Check without modifying
black --check .

# Format specific file
black path/to/file.py
```

**isort** - Import statement organizer
```bash
# Sort imports
isort . --profile black

# Check without modifying
isort --check-only . --profile black
```

### Code Linting

**Ruff** - Fast Python linter
```bash
# Check all files
ruff check .

# Auto-fix issues
ruff check . --fix

# Check specific rules
ruff check . --select E,F,W,I
```

### Testing

**Pytest** - Testing framework
```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_database.py -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html

# Run only unit tests
pytest tests/ -m unit

# Run fast (skip slow tests)
pytest tests/ -m "not slow"

# Stop on first failure
pytest tests/ -x

# Show local variables on failure
pytest tests/ -l
```

### Security

**Bandit** - Security issue scanner
```bash
# Scan for security issues
bandit -r .

# Only show medium/high severity
bandit -r . -ll

# Skip tests directory
bandit -r . --exclude tests/
```

### Type Checking (Optional)

**mypy** - Static type checker
```bash
# Check all files
mypy . --ignore-missing-imports

# Check specific file
mypy path/to/file.py
```

---

## 📝 Pre-Commit Hooks

Pre-commit hooks automatically run quality checks before each commit.

### What Hooks Run

On every **commit**:
1. ✅ **black** - Format code
2. ✅ **isort** - Sort imports
3. ✅ **ruff** - Lint code
4. ✅ **trailing-whitespace** - Remove trailing spaces
5. ✅ **end-of-file-fixer** - Ensure files end with newline
6. ✅ **check-yaml** - Validate YAML syntax
7. ✅ **bandit** - Security scan
8. ✅ **pytest** - Run quick tests

On **push**:
1. ✅ **pytest with coverage** - Full test suite with coverage check

### Managing Hooks

```bash
# Install hooks
pre-commit install

# Run all hooks manually
pre-commit run --all-files

# Run specific hook
pre-commit run black --all-files

# Skip hooks (NOT RECOMMENDED)
git commit --no-verify -m "message"

# Update hooks to latest versions
pre-commit autoupdate

# Uninstall hooks
pre-commit uninstall
```

### Hook Configuration

Hooks are configured in `.pre-commit-config.yaml`. You can:
- Enable/disable specific hooks
- Adjust hook arguments
- Add custom local hooks

---

## 🔄 Development Workflow

### Daily Workflow

```bash
# 1. Pull latest changes
git pull origin main

# 2. Create feature branch
git checkout -b feature/my-feature

# 3. Write tests first (TDD!)
# Edit: tests/test_my_feature.py

# 4. Run tests (should fail)
pytest tests/test_my_feature.py -v

# 5. Implement feature
# Edit: my_module.py

# 6. Run tests (should pass)
pytest tests/test_my_feature.py -v

# 7. Run all quality checks
pytest tests/ -v --cov=. --cov-report=term-missing
black .
isort . --profile black
ruff check .

# 8. Commit (pre-commit hooks run automatically)
git add tests/test_my_feature.py my_module.py
git commit -m "feat: Add my feature with tests"

# 9. Push (more hooks run)
git push origin feature/my-feature
```

### Quick Quality Check

Before committing, run this one-liner:
```bash
pytest tests/ -q && black . && isort . --profile black && ruff check . && echo "✅ All checks passed!"
```

Or create an alias:
```bash
# Add to ~/.bashrc or ~/.zshrc
alias quality-check='pytest tests/ -q && black . && isort . --profile black && ruff check . && echo "✅ All checks passed!"'
```

---

## 🎯 Editor Integration

### VS Code

Install extensions:
- **Python** (ms-python.python)
- **Pylance** (ms-python.vscode-pylance)
- **Black Formatter** (ms-python.black-formatter)
- **isort** (ms-python.isort)
- **Ruff** (charliermarsh.ruff)

**settings.json:**
```json
{
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "python.testing.pytestEnabled": true,
  "python.testing.unittestEnabled": false,
  "[python]": {
    "editor.codeActionsOnSave": {
      "source.organizeImports": true
    }
  }
}
```

### PyCharm

1. **Enable Black:**
   - Settings → Tools → Black → Enable Black
   - Settings → Tools → Actions on Save → Reformat code (Black)

2. **Enable isort:**
   - Settings → Tools → External Tools → Add isort

3. **Enable Pytest:**
   - Settings → Tools → Python Integrated Tools → Default test runner → pytest

4. **File Watchers:**
   - Settings → Tools → File Watchers → Add Black, isort

### Vim/Neovim

**vim-plug:**
```vim
Plug 'psf/black'
Plug 'fisadev/vim-isort'
Plug 'vim-test/vim-test'
```

**Auto-format on save:**
```vim
autocmd BufWritePre *.py execute ':Black'
autocmd BufWritePre *.py execute ':Isort'
```

---

## 🧪 Testing Best Practices

### Test Structure

```
tests/
├── __init__.py
├── conftest.py              # Shared fixtures
├── test_module_name.py      # Tests for module_name.py
├── test_integration/        # Integration tests
│   └── test_workflow.py
└── fixtures/                # Test data files
    └── sample_data.json
```

### Writing Good Tests

```python
# Good test naming
def test_function_name_behavior_expected_result():
    """Clear docstring explaining what is tested."""
    # Arrange
    input_data = "test input"

    # Act
    result = function_name(input_data)

    # Assert
    assert result == "expected output"
```

### Test Markers

```python
import pytest

@pytest.mark.unit
def test_simple_function():
    """Unit test for isolated function."""
    pass

@pytest.mark.integration
def test_full_workflow():
    """Integration test for complete workflow."""
    pass

@pytest.mark.slow
def test_long_running():
    """Test that takes >5 seconds."""
    pass
```

---

## 📊 Coverage Reports

### Generate HTML Report

```bash
pytest tests/ --cov=. --cov-report=html
# Open htmlcov/index.html in browser
```

### Coverage Config

Coverage settings in `pytest.ini`:
```ini
[coverage:run]
omit =
    tests/*
    */venv/*
    setup.py

[coverage:report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise NotImplementedError
```

---

## 🐛 Debugging

### Debug with pytest

```bash
# Show print statements
pytest tests/ -s

# Drop into debugger on failure
pytest tests/ --pdb

# Show local variables
pytest tests/ -l

# Verbose traceback
pytest tests/ --tb=long
```

### Debug with pdb

```python
def my_function():
    import pdb; pdb.set_trace()  # Breakpoint
    # Code here
```

---

## 🔧 Troubleshooting

### Pre-commit hooks fail

```bash
# See what failed
pre-commit run --all-files

# Fix formatting issues
black .
isort . --profile black

# Fix linting issues
ruff check . --fix

# Skip hooks if necessary (NOT RECOMMENDED)
git commit --no-verify
```

### Tests fail in CI but pass locally

1. Check Python version: `python --version`
2. Run with same Python version: `python3.12 -m pytest tests/`
3. Check for environment-specific issues
4. Verify all dependencies: `pip install -r requirements.txt`

### Import errors in tests

```bash
# Ensure PYTHONPATH includes project root
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Or use pytest discovery
pytest tests/
```

---

## 📚 Additional Resources

- **Black Documentation:** https://black.readthedocs.io/
- **isort Documentation:** https://pycqa.github.io/isort/
- **Ruff Documentation:** https://docs.astral.sh/ruff/
- **Pytest Documentation:** https://docs.pytest.org/
- **Pre-commit Documentation:** https://pre-commit.com/

---

## 🎓 Learning TDD

### Recommended Reading

1. **Test Driven Development: By Example** - Kent Beck
2. **Python Testing with pytest** - Brian Okken
3. **Clean Code** - Robert C. Martin

### Online Courses

- Real Python: Testing Your Code
- Test Driven Development with Python
- Pytest Tutorial (Official Docs)

---

**Last Updated:** 2025-12-18
**Maintained By:** Project Contributors
**Questions?** See CONTRIBUTING.md or open an issue
