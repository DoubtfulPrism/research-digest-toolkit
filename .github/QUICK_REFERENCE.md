# Quick Reference: TDD & Quality Standards

## 🎯 The Golden Rules

1. **Tests First, Always** - No exceptions
2. **Red → Green → Refactor** - Follow the cycle
3. **100% Test Pass Rate** - All tests must pass
4. **≥90% Coverage** - For all new code
5. **Quality Checks Pass** - Before every commit

---

## 🚀 Quick Commands

### Before You Start
```bash
# Ensure clean slate
pytest tests/ -v && black . && isort . --profile black
```

### During Development
```bash
# Run single test file
pytest tests/test_module.py -v

# Run with coverage
pytest tests/test_module.py --cov=module --cov-report=term-missing
```

### Before Commit (MANDATORY)
```bash
# One-liner quality check
pytest tests/ -v && black . && isort . --profile black && ruff check . && echo "✅ Ready to commit!"
```

### Commit
```bash
# Hooks run automatically
git add .
git commit -m "feat: Description with tests"
```

---

## 📝 TDD Cycle (30 seconds)

```python
# 1. RED - Write failing test
def test_new_function():
    assert new_function() == "result"
# Run: pytest tests/test_module.py -v
# Status: FAILED ✓ (expected)

# 2. GREEN - Minimal implementation
def new_function():
    return "result"
# Run: pytest tests/test_module.py -v
# Status: PASSED ✓

# 3. REFACTOR - Improve
def new_function():
    """Proper implementation with docs."""
    return calculate_result()
# Run: pytest tests/test_module.py -v
# Status: PASSED ✓
```

---

## ✅ Quality Checklist

Before EVERY commit:

- [ ] Tests written FIRST (TDD)
- [ ] All tests pass (`pytest tests/ -v`)
- [ ] Coverage ≥90% for new code
- [ ] Code formatted (`black .`)
- [ ] Imports sorted (`isort . --profile black`)
- [ ] No linting errors (`ruff check .`)
- [ ] Documentation updated

---

## 🚫 Never Do This

❌ Implement without tests
❌ Commit failing tests
❌ Skip pre-commit hooks
❌ Reduce test coverage
❌ Commit unformatted code

---

## 📊 Current Standards

| Metric | Requirement | Current |
|--------|-------------|---------|
| Test Pass Rate | 100% | 100% ✅ |
| New Code Coverage | ≥90% | - |
| Core Module Coverage | ≥85% | 89%+ ✅ |
| Linting Errors | 0 | 0 ✅ |

---

## 🛠️ Tool Quick Reference

```bash
# Black - Format code
black .                    # Format all
black --check .           # Check only

# isort - Sort imports
isort . --profile black   # Sort all
isort --check-only .      # Check only

# Ruff - Lint code
ruff check .              # Check all
ruff check . --fix        # Auto-fix

# Pytest - Run tests
pytest tests/ -v          # Verbose
pytest tests/ -q          # Quiet
pytest tests/ -x          # Stop on first fail
pytest tests/ -k name     # Run matching tests

# Coverage
pytest tests/ --cov=module --cov-report=term-missing
```

---

## 📚 Documentation

- **Full TDD Workflow:** [TDD_WORKFLOW.md](TDD_WORKFLOW.md)
- **Development Setup:** [DEVELOPMENT_SETUP.md](DEVELOPMENT_SETUP.md)
- **CI/CD Guide:** [CI_SETUP.md](CI_SETUP.md)
- **Contributing:** [CONTRIBUTING.md](../CONTRIBUTING.md)

---

## 💡 Pro Tips

1. **Run tests frequently** - After every small change
2. **Use markers** - `@pytest.mark.unit`, `@pytest.mark.integration`
3. **Keep tests fast** - Unit tests should be <1s
4. **Test edge cases** - Empty inputs, None, errors
5. **Use fixtures** - Share setup code
6. **Watch coverage** - `pytest --cov=. --cov-report=html`

---

## 🆘 Quick Fixes

**Tests failing?**
```bash
pytest tests/ -v --tb=short  # See error details
```

**Format issues?**
```bash
black . && isort . --profile black
```

**Linting errors?**
```bash
ruff check . --fix
```

**Coverage too low?**
```bash
pytest tests/ --cov=. --cov-report=html
# Open htmlcov/index.html to see uncovered lines
```

**Pre-commit failing?**
```bash
pre-commit run --all-files  # See what failed
# Fix issues, then commit again
```

---

**Remember: Quality is not optional. TDD is mandatory.**

*Last Updated: 2025-12-18*
