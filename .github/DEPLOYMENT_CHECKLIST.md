# GitHub Deployment Checklist

This checklist will help you deploy the Research Digest Toolkit to GitHub with full CI/CD enabled.

## ✅ Pre-Deployment Checklist

### 1. Update Repository URLs

Before pushing, update these files with your actual GitHub username and repository name:

**README.md** - Line 3:
```markdown
[![Tests](https://github.com/YOUR_USERNAME/Scripts/actions/workflows/test.yml/badge.svg)](https://github.com/YOUR_USERNAME/Scripts/actions/workflows/test.yml)
```

Replace `YOUR_USERNAME` with your GitHub username.

### 2. Review Workflow Files

All workflow files are ready in `.github/workflows/`:
- ✅ `test.yml` - Full test suite
- ✅ `quick-check.yml` - Fast validation
- ✅ `scheduled-tests.yml` - Weekly regression tests

### 3. Review Dependabot Configuration

- ✅ `.github/dependabot.yml` - Configured for weekly updates

## 📤 Deployment Steps

### Step 1: Initialize Git (if not already done)

```bash
# Check if git is initialized
git status

# If not, initialize
git init
git branch -M main
```

### Step 2: Add All Files

```bash
# Add all files including CI configuration
git add .
git add .github/

# Verify what will be committed
git status
```

### Step 3: Create Initial Commit

```bash
git commit -m "feat: Add comprehensive test suite and CI/CD pipelines

- Add 86 automated tests (89%+ coverage on core modules)
- Configure GitHub Actions workflows:
  - Full test suite (Python 3.9-3.12)
  - Quick checks for PRs
  - Scheduled weekly regression tests
  - Code quality and security scanning
- Add Dependabot for dependency management
- Update documentation with testing info

Tests:
- test_database.py: 15 tests (89% coverage)
- test_utils.py: 35 tests (100% coverage)
- test_scrapers.py: 20 tests (100% coverage)
- test_plugin_loading.py: 16 tests (99% coverage)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

### Step 4: Connect to GitHub

```bash
# Create repository on GitHub first, then:
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git

# Verify remote
git remote -v
```

### Step 5: Push to GitHub

```bash
# Push to main branch
git push -u origin main
```

### Step 6: Verify Workflows Started

1. Go to GitHub repository
2. Click on **Actions** tab
3. You should see workflows running:
   - ✅ Tests
   - ✅ Quick Check

### Step 7: Review First Run

1. Click on the running workflow
2. Monitor the progress
3. Ensure all jobs pass (green checkmarks)

## 🔧 Post-Deployment Configuration

### Optional: Enable Codecov

1. Go to [codecov.io](https://codecov.io)
2. Sign in with GitHub
3. Add your repository
4. Copy the Codecov token
5. Add to GitHub Secrets:
   - Repository → Settings → Secrets and variables → Actions
   - New secret: `CODECOV_TOKEN`
   - Paste token value

### Optional: Branch Protection Rules

Protect the main branch:

1. Repository → Settings → Branches
2. Add branch protection rule for `main`:
   - ✅ Require pull request reviews
   - ✅ Require status checks to pass
   - ✅ Require branches to be up to date
   - Select required checks:
     - `Test on Python 3.12`
     - `Code Quality Checks`
     - `Security Scan`

### Optional: GitHub Pages (for coverage reports)

If you want to publish coverage reports:

1. Settings → Pages
2. Source: GitHub Actions
3. Create workflow to publish htmlcov/

## 🎯 Validation Checklist

After deployment, verify:

- [ ] Repository shows up on GitHub
- [ ] Actions tab shows workflow runs
- [ ] All workflows complete successfully
- [ ] README badges display correctly
- [ ] Test results are viewable in Actions
- [ ] Dependabot creates PRs for outdated dependencies
- [ ] Codecov (if enabled) shows coverage reports

## 🚨 Troubleshooting

### Workflows Don't Appear

**Solution:**
1. Ensure `.github/workflows/*.yml` files are committed
2. Check YAML syntax is valid
3. Verify repository has Actions enabled (Settings → Actions)

### Tests Fail in CI But Pass Locally

**Common causes:**
1. Different Python version - CI tests multiple versions
2. Missing dependencies - Check requirements.txt
3. Path issues - Use absolute imports
4. File permissions - CI runs as different user

**Debug:**
```bash
# Test locally with exact CI command
pytest tests/ -v --tb=short --cov=. --cov-report=xml --cov-report=term-missing
```

### Badge Shows "Unknown"

**Solutions:**
1. Wait for first workflow run to complete
2. Verify URL in README matches your repository
3. Clear browser cache
4. Check workflow file name matches badge URL

### Dependabot Not Creating PRs

**Solutions:**
1. Wait up to a week (runs Monday 9 AM UTC)
2. Manually trigger: Settings → Code security → Dependabot
3. Check `.github/dependabot.yml` syntax
4. Verify Dependabot is enabled for repository

## 📋 Files Created

### Testing Infrastructure
```
tests/
├── __init__.py
├── conftest.py
├── README.md
├── test_database.py      (15 tests)
├── test_plugin_loading.py (16 tests)
├── test_scrapers.py       (20 tests)
└── test_utils.py          (35 tests)

pytest.ini                  (pytest configuration)
```

### CI/CD Configuration
```
.github/
├── workflows/
│   ├── test.yml           (Full test suite)
│   ├── quick-check.yml    (Fast validation)
│   └── scheduled-tests.yml (Weekly regression)
├── dependabot.yml         (Dependency updates)
├── CI_SETUP.md           (CI documentation)
└── DEPLOYMENT_CHECKLIST.md (This file)
```

### Updated Documentation
```
README.md                  (Updated with badges and testing info)
TODO.md                    (Marked testing tasks complete)
requirements.txt           (Added pytest, pytest-cov)
database.py                (Fixed missing import bug)
```

## 🎉 Success Criteria

Deployment is successful when:

1. ✅ All workflows run and pass
2. ✅ README badges are green
3. ✅ Tests can be triggered manually
4. ✅ Dependabot is active
5. ✅ Coverage reports are generated
6. ✅ Security scans complete without critical issues

## 📞 Next Steps

After successful deployment:

1. **Monitor first week** - Watch for issues
2. **Review Dependabot PRs** - Keep dependencies updated
3. **Add integration tests** - Expand test coverage
4. **Configure notifications** - Slack/email for failures
5. **Set up branch protection** - Require tests to pass

---

**Prepared:** 2025-12-18
**For:** Research Digest Toolkit v1.0
**CI/CD Platform:** GitHub Actions
