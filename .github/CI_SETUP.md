# GitHub Actions CI/CD Setup Guide

This document explains the Continuous Integration and Continuous Deployment (CI/CD) setup for the Research Digest Toolkit.

## Overview

The project uses GitHub Actions for automated testing, code quality checks, and security scanning. Three main workflows are configured:

1. **Full Test Suite** (`test.yml`) - Comprehensive testing on multiple Python versions
2. **Quick Check** (`quick-check.yml`) - Fast tests for feature branches
3. **Scheduled Tests** (`scheduled-tests.yml`) - Weekly regression testing

## Workflows

### 1. Full Test Suite (`test.yml`)

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`
- Manual trigger via workflow_dispatch

**What it does:**
- Tests on Python 3.9, 3.10, 3.11, and 3.12
- Installs system dependencies (pandoc, poppler-utils)
- Runs full test suite with coverage
- Uploads coverage to Codecov (Python 3.12 only)
- Archives test results as artifacts
- Runs code quality checks (black, isort, ruff)
- Performs security scans (bandit, safety)

**Jobs:**
```yaml
1. test (matrix: Python 3.9-3.12)
   - Run pytest with coverage
   - Upload coverage reports

2. lint
   - Check code formatting
   - Check import sorting
   - Lint with ruff

3. security
   - Scan dependencies for vulnerabilities
   - Run bandit security linter
```

**Viewing Results:**
- Go to Actions tab → Test workflow run
- Download artifacts: test-results-{version}, security-reports
- View coverage on Codecov (if configured)

### 2. Quick Check (`quick-check.yml`)

**Triggers:**
- Push to any branch except `main`
- Pull requests

**What it does:**
- Fast validation on Python 3.12 only
- Skips slow tests (`-m "not slow"`)
- Fails fast after 3 failures (`--maxfail=3`)
- Provides quick feedback for development

**Purpose:**
- Give developers rapid feedback
- Catch obvious failures early
- Conserve CI minutes

### 3. Scheduled Tests (`scheduled-tests.yml`)

**Triggers:**
- Every Monday at 9 AM UTC (cron schedule)
- Manual trigger via workflow_dispatch

**What it does:**
- Comprehensive weekly regression testing
- Checks for outdated dependencies
- Archives coverage reports (90-day retention)
- Alerts on failures

**Purpose:**
- Catch regressions from dependency updates
- Ensure long-term stability
- Monitor dependency health

## Dependabot Configuration

Dependabot is configured to automatically:
- Check for Python dependency updates weekly
- Check for GitHub Actions updates weekly
- Create pull requests with updates
- Label PRs appropriately

**Configuration:** `.github/dependabot.yml`

## Setting Up CI/CD

### Initial Setup

1. **Push workflows to GitHub:**
   ```bash
   git add .github/
   git commit -m "Add GitHub Actions CI/CD workflows"
   git push origin main
   ```

2. **Verify workflows are active:**
   - Go to repository → Actions tab
   - You should see: Tests, Quick Check, Scheduled Tests

3. **Check first run:**
   - Workflows trigger automatically on push
   - Monitor the first run for any issues

### Optional: Codecov Integration

To enable coverage reporting on Codecov.io:

1. **Sign up at [codecov.io](https://codecov.io) with your GitHub account**

2. **Add repository to Codecov:**
   - Authorize Codecov to access your repos
   - Select the Research Digest Toolkit repository

3. **Add Codecov token to GitHub secrets:**
   - Copy your Codecov token from codecov.io
   - Go to GitHub repo → Settings → Secrets and variables → Actions
   - Create new secret: `CODECOV_TOKEN` = `<your-token>`

4. **Coverage will now upload automatically** after each test run

### Optional: Status Badges

Add status badges to your README.md:

```markdown
![Tests](https://github.com/YOUR_USERNAME/YOUR_REPO/actions/workflows/test.yml/badge.svg)
![Coverage](https://codecov.io/gh/YOUR_USERNAME/YOUR_REPO/branch/main/graph/badge.svg)
```

Replace `YOUR_USERNAME` and `YOUR_REPO` with your actual values.

## Understanding Test Results

### Successful Run
- ✅ Green checkmark in Actions tab
- All jobs passed
- Coverage reports uploaded
- No security vulnerabilities found

### Failed Run
- ❌ Red X in Actions tab
- Click on the failed job to see details
- Review the error logs
- Common issues:
  - Test failures
  - Import errors
  - Dependency conflicts
  - Linting violations

### Artifact Downloads

After each run, artifacts are available:
```
test-results-3.12/
├── coverage.xml       # Machine-readable coverage
└── htmlcov/          # Human-readable HTML report

security-reports/
└── bandit-report.json # Security scan results
```

Download from: Actions → Workflow run → Artifacts section

## Local Testing

Before pushing, test locally to avoid CI failures:

```bash
# Run full test suite (like CI does)
pytest tests/ -v --tb=short --cov=. --cov-report=term-missing

# Run quick tests (like quick-check.yml)
pytest tests/ -v --tb=short -m "not slow" --maxfail=3

# Check code formatting
black --check .
isort --check-only .
ruff check .

# Security scan
pip install bandit safety
bandit -r .
safety check
```

## Workflow Customization

### Change Python Versions

Edit `.github/workflows/test.yml`:
```yaml
strategy:
  matrix:
    python-version: ["3.9", "3.10", "3.11", "3.12"]
```

### Change Test Coverage Threshold

Add to `.github/workflows/test.yml`:
```yaml
- name: Check coverage threshold
  run: |
    coverage report --fail-under=80
```

### Add Slack/Discord Notifications

Add notification step:
```yaml
- name: Notify on Slack
  if: failure()
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

### Skip CI for Specific Commits

Add to commit message:
```bash
git commit -m "docs: Update README [skip ci]"
```

## Troubleshooting

### Tests Pass Locally But Fail in CI

**Common causes:**
1. **Different Python version** - CI tests on multiple versions
2. **Missing system dependencies** - Add to workflow:
   ```yaml
   - name: Install system deps
     run: sudo apt-get install -y your-package
   ```
3. **Environment variables** - Set in workflow:
   ```yaml
   env:
     MY_VAR: value
   ```
4. **File permissions** - GitHub Actions uses different user

### Workflow Doesn't Trigger

**Check:**
1. Workflow file is in `.github/workflows/`
2. YAML syntax is valid
3. Branch names match triggers
4. Repository has Actions enabled (Settings → Actions)

### Coverage Upload Fails

**Solutions:**
1. Check `CODECOV_TOKEN` secret is set
2. Verify token is correct on codecov.io
3. Check internet connectivity in workflow
4. Review Codecov integration status

### Rate Limiting / Quota Issues

GitHub Actions free tier:
- 2,000 minutes/month for private repos
- Unlimited for public repos

**Reduce usage:**
1. Use `quick-check.yml` for PRs
2. Run full suite only on main
3. Reduce test matrix size
4. Use caching for dependencies

## Best Practices

1. **Keep workflows fast** - CI should complete in < 5 minutes
2. **Test before pushing** - Run tests locally first
3. **Use caching** - Cache pip packages to speed up runs
4. **Monitor failures** - Address failing tests immediately
5. **Update dependencies** - Review Dependabot PRs weekly
6. **Security alerts** - Address security issues promptly
7. **Coverage trends** - Monitor coverage over time

## Workflow Files Summary

| File | Purpose | Trigger | Duration |
|------|---------|---------|----------|
| `test.yml` | Full test suite + quality checks | Push to main/develop, PRs | ~5-8 min |
| `quick-check.yml` | Fast validation | Push to feature branches | ~2-3 min |
| `scheduled-tests.yml` | Weekly regression testing | Every Monday 9 AM UTC | ~5-8 min |
| `dependabot.yml` | Dependency updates | Weekly | N/A |

## Monitoring and Maintenance

### Weekly Tasks
- Review Dependabot PRs
- Check scheduled test results
- Monitor coverage trends

### Monthly Tasks
- Review security scan results
- Update outdated dependencies
- Review and update workflows

### When Tests Fail
1. Check the error logs in Actions tab
2. Reproduce locally
3. Fix the issue
4. Push the fix
5. Verify green CI

## Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Pytest Documentation](https://docs.pytest.org/)
- [Codecov Documentation](https://docs.codecov.com/)
- [Dependabot Documentation](https://docs.github.com/en/code-security/dependabot)

---

**Last Updated:** 2025-12-18
**Workflow Version:** 1.0
**Python Versions:** 3.9, 3.10, 3.11, 3.12
