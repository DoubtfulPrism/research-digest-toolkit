# Test-Driven Development Workflow

This document defines our **mandatory** development workflow to ensure high code quality and comprehensive test coverage.

## 🎯 Core Principles

1. **Tests First, Always** - Write tests before implementation
2. **Red-Green-Refactor** - Follow TDD cycle religiously
3. **Quality Gates** - Code must pass all checks before commit
4. **No Exceptions** - Even "small" changes require tests

---

## 📋 Development Workflow (Mandatory)

### Before Writing Any Code

```bash
# 1. Create a feature branch
git checkout -b feature/your-feature-name

# 2. Run existing tests to ensure clean slate
pytest tests/ -v

# 3. Ensure code is formatted
black . && isort . --profile black
```

### TDD Cycle: Red → Green → Refactor

#### Step 1: RED - Write Failing Test First

**Rule:** Write the test for the feature you want to implement BEFORE writing any implementation code.

```python
# tests/test_new_feature.py
import pytest
from my_module import new_function

def test_new_function_basic_case():
    """Test that new_function works with basic input."""
    result = new_function("input")
    assert result == "expected_output"
```

**Run the test - it should FAIL:**
```bash
pytest tests/test_new_feature.py -v
# Expected: FAILED (because new_function doesn't exist yet)
```

#### Step 2: GREEN - Write Minimal Code to Pass

**Rule:** Write the MINIMUM code needed to make the test pass.

```python
# my_module.py
def new_function(input_str):
    """Implement minimum functionality to pass test."""
    return "expected_output"
```

**Run the test - it should PASS:**
```bash
pytest tests/test_new_feature.py -v
# Expected: PASSED
```

#### Step 3: REFACTOR - Improve While Keeping Tests Green

**Rule:** Refactor only after tests pass. Tests must remain green during refactoring.

```python
# my_module.py - Improved implementation
def new_function(input_str):
    """
    Process input string and return formatted output.

    Args:
        input_str: Input string to process

    Returns:
        Formatted output string
    """
    # Proper implementation with edge cases
    if not input_str:
        raise ValueError("Input cannot be empty")

    return input_str.upper()
```

**Run tests after each refactor:**
```bash
pytest tests/test_new_feature.py -v
```

#### Step 4: Add Edge Cases

**Rule:** Continue RED-GREEN-REFACTOR cycle for edge cases.

```python
# tests/test_new_feature.py - Add edge case tests
def test_new_function_empty_input():
    """Test error handling for empty input."""
    with pytest.raises(ValueError):
        new_function("")

def test_new_function_special_characters():
    """Test handling of special characters."""
    result = new_function("hello@world!")
    assert result == "HELLO@WORLD!"
```

---

## ✅ Pre-Commit Quality Checklist

**MUST complete ALL steps before committing:**

### 1. Run Full Test Suite
```bash
pytest tests/ -v --tb=short
```
✅ All tests must pass (100% pass rate required)

### 2. Check Code Coverage
```bash
pytest tests/ --cov=. --cov-report=term-missing
```
✅ New code must have ≥90% coverage
✅ Don't reduce overall project coverage

### 3. Format Code (Auto-fix)
```bash
black .
isort . --profile black
```
✅ All files must be formatted

### 4. Lint Code
```bash
ruff check . --select E,F,W,I --ignore E501
```
✅ Zero linting errors allowed
✅ Fix all warnings

### 5. Type Checking (Optional but Recommended)
```bash
mypy . --ignore-missing-imports
```
✅ No type errors for new code

### 6. Security Scan
```bash
bandit -r . -ll  # Only high/medium severity
```
✅ No new security issues

---

## 🚫 What NOT to Do

### ❌ **Never** Commit Without Tests
```python
# BAD: Implementing without tests
def new_feature():
    return "implemented"

# GOOD: Test first, then implement
def test_new_feature():
    result = new_feature()
    assert result == "implemented"
```

### ❌ **Never** Skip Tests "Because It's Simple"
```python
# BAD: "It's just a getter, doesn't need tests"
def get_name(self):
    return self.name

# GOOD: Even simple code has tests
def test_get_name():
    obj = MyClass(name="Test")
    assert obj.get_name() == "Test"
```

### ❌ **Never** Write Tests After Implementation
```python
# BAD ORDER:
# 1. Write implementation
# 2. Write tests to match

# GOOD ORDER:
# 1. Write tests defining behavior
# 2. Write implementation to pass tests
```

### ❌ **Never** Commit Failing Tests
```bash
# BAD:
git commit -m "Add feature (tests still failing)"

# GOOD:
# Fix tests first, then commit
git commit -m "Add feature with passing tests"
```

---

## 📝 Example: Adding a New Feature (Complete)

### Scenario: Add email validation to utils.py

#### 1. Write Test First (RED)
```python
# tests/test_utils.py
def test_validate_email_valid():
    """Test validation of valid email addresses."""
    assert validate_email("user@example.com") is True
    assert validate_email("test.user@domain.co.uk") is True

def test_validate_email_invalid():
    """Test rejection of invalid email addresses."""
    assert validate_email("invalid") is False
    assert validate_email("@example.com") is False
    assert validate_email("user@") is False

def test_validate_email_empty():
    """Test handling of empty input."""
    assert validate_email("") is False
    assert validate_email(None) is False
```

```bash
# Run tests - SHOULD FAIL
$ pytest tests/test_utils.py::test_validate_email_valid -v
# ImportError: cannot import name 'validate_email' ✓ Expected!
```

#### 2. Implement Minimum Code (GREEN)
```python
# utils.py
import re

def validate_email(email):
    """Validate email address format."""
    if not email:
        return False

    # Simple regex for email validation
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))
```

```bash
# Run tests - SHOULD PASS
$ pytest tests/test_utils.py -k validate_email -v
# ======================== 3 passed ======================== ✓
```

#### 3. Refactor with Tests Green
```python
# utils.py - Improved with constants and documentation
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

def validate_email(email: str) -> bool:
    """
    Validate email address format.

    Args:
        email: Email address to validate

    Returns:
        True if email is valid format, False otherwise

    Examples:
        >>> validate_email("user@example.com")
        True
        >>> validate_email("invalid")
        False
    """
    if not email or not isinstance(email, str):
        return False

    return bool(EMAIL_REGEX.match(email))
```

#### 4. Run Full Quality Checks
```bash
# All tests
pytest tests/ -v
# ======================== 89 passed ======================== ✓

# Coverage
pytest tests/ --cov=utils --cov-report=term-missing
# utils.py                  100%   ✓

# Format
black . && isort . --profile black
# All done! ✨ 🍰 ✨ ✓

# Lint
ruff check .
# All checks passed! ✓
```

#### 5. Commit
```bash
git add tests/test_utils.py utils.py
git commit -m "feat: Add email validation to utils

- Add validate_email() function with regex validation
- Test valid email formats
- Test invalid email formats
- Test edge cases (empty, None, non-string)
- 100% test coverage on new code

Tests: 89 passed (+3)
Coverage: utils.py 100%"
```

---

## 🔄 Integration with CI/CD

All quality checks run automatically on GitHub:
- ✅ Tests must pass on Python 3.9-3.12
- ✅ Code must be formatted (black, isort)
- ✅ No linting errors (ruff)
- ✅ No security issues (bandit)
- ✅ Coverage reports generated

**Pull requests cannot merge if CI fails.**

---

## 📊 Quality Metrics to Maintain

| Metric | Target | Current |
|--------|--------|---------|
| Test Pass Rate | 100% | 100% (86/86) |
| Core Module Coverage | ≥90% | 89-100% |
| Overall Coverage | ≥80% | 42% (improving) |
| Linting Errors | 0 | 0 |
| Security Issues | 0 | 0 |

---

## 🛠️ Quick Reference Commands

```bash
# Before starting work
pytest tests/ -v && black . && isort . --profile black

# During development (run frequently)
pytest tests/test_your_module.py -v

# Before committing (MANDATORY)
pytest tests/ -v --cov=. --cov-report=term-missing && \
black . && \
isort . --profile black && \
ruff check .

# Quick check (fast validation)
pytest tests/ -q --tb=no && echo "✓ Tests pass"
```

---

## 📚 Additional Resources

### Pytest Best Practices
- Use descriptive test names: `test_function_behavior_expected_result`
- One assertion per test (generally)
- Use fixtures for setup/teardown
- Mark tests appropriately (`@pytest.mark.unit`, `@pytest.mark.integration`)

### Coverage Best Practices
- Focus on critical paths first
- Test edge cases and error conditions
- Don't just aim for 100% - aim for meaningful tests
- Exclude non-testable code (scripts, main blocks)

### Code Quality Best Practices
- Follow PEP 8 (enforced by black/ruff)
- Use type hints for function signatures
- Write docstrings for all public functions
- Keep functions small and focused (≤20 lines ideal)

---

## 🚨 Enforcement

### Pre-Commit Hooks
Pre-commit hooks automatically run quality checks. See `.pre-commit-config.yaml`.

### CI/CD Checks
GitHub Actions runs all checks on every push. Failed checks block merging.

### Code Review Checklist
Reviewers will verify:
- [ ] Tests written before implementation
- [ ] All tests pass
- [ ] Coverage ≥90% for new code
- [ ] Code formatted and linted
- [ ] No security issues
- [ ] Documentation updated

---

## ✍️ Commitment

**As developers on this project, we commit to:**

1. ✅ Write tests BEFORE implementation (TDD)
2. ✅ Maintain 100% test pass rate
3. ✅ Never reduce code coverage
4. ✅ Fix all linting errors before commit
5. ✅ Format all code with black/isort
6. ✅ Run full quality checks before push
7. ✅ Request code review for all changes

**No exceptions. Quality is non-negotiable.**

---

**Last Updated:** 2025-12-18
**Version:** 1.0
**Status:** Mandatory for all development
