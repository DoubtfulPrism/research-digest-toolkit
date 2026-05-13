# Installable Package Implementation Plan

Created: 2026-04-28
Author: dougbuck@protonmail.com
Status: VERIFIED
Approved: Yes
Iterations: 2
Worktree: No
Type: Feature

## Summary

**Goal:** Package the Research Digest Toolkit TUI as a pip-installable Python package with a `Research_Toolkit` console command, using a duplicate-first strategy that keeps existing scripts working throughout.

**Architecture:** Copy the three shared modules (`config_models`, `rich_utils`, `scheduler_utils`) into `research_digest_tui/` as package-internal modules. Update only the two internal TUI service files to import from the package copies. Leave original top-level files untouched. Create a new `cli.py` entry point with XDG-style config discovery. Build and verify the wheel in an isolated venv before any cleanup.

**Tech Stack:** Python >=3.9, Textual 8.1.1, hatchling build backend, uv for package management.

**PRD:** `docs/prd/2026-04-28-installable-package.md`

## Scope

### In Scope

- Revert uncommitted working-tree changes (Task 0 — prerequisite)
- Copy 3 shared modules into `research_digest_tui/` package (originals untouched)
- Update 2 internal service imports to use package-qualified paths
- Create `research_digest_tui/cli.py` with config discovery + `main()` entry point
- Create bundled default config at `research_digest_tui/data/research_config.default.yaml`
- Fix `RunnerService` to prefer installed `research-digest` script, fallback to dev path
- Update `research_digest_tui/__main__.py` to delegate to `cli.main()`
- Remove untested `research-digest` console script from `pyproject.toml`
- Build wheel, install in clean venv, smoke-test entry point
- Create `INSTALL.md` and update `README.md` Installation section

### Out of Scope

- Pre-existing test failures in `test_http_client.py` and `test_scheduler.py` — separate issue
- The `research-digest` CLI orchestrator entry point — removed from pyproject.toml, can re-add later
- Replacing top-level originals with shims — cleanup for a follow-up after the package is proven
- Updating test imports to use `research_digest_tui.*` paths — tests keep using top-level modules
- Release branch and git tag — deferred from PRD scope (user-acknowledged deferral). PRD includes this in scope, but plan defers it as a follow-up after the wheel is proven in use. INSTALL.md will use `pip install git+https://github.com/...@main` (not a release tag) until the release branch is created

## Approach

**Chosen:** Duplicate-first with late-stage cleanup

**Why:** Keeps every existing script working at all times. If the packaging work fails at any point, the original codebase is completely unaffected. Temporary code duplication (3 files) is the explicit trade-off for safety.

**Alternatives considered:**
- *Shim-based move (old plan):* Replace originals with import shims immediately. Rejected — a broken shim breaks all existing scripts at once.
- *Separate pkg/ build directory:* Full isolation but too much infrastructure for 3 shared files.

## Context for Implementer

> Write for an implementer who has never seen the codebase.

- **Patterns to follow:** `research_digest_tui/services/config_service.py` shows the existing service pattern — class with `__init__(config_path)`, property-based lazy loading, `reload()` cache invalidation.
- **Conventions:** Absolute imports throughout (`from research_digest_tui.X import Y`). Pydantic models for config validation. Rich for console output. pytest with `@pytest.mark.unit` / `@pytest.mark.tui` markers.
- **Key files:**
  - `pyproject.toml` — already has `[build-system]`, `[project]`, `[project.scripts]`, and `[tool.hatch.build.targets.wheel]` (committed in `cdda8c0`)
  - `research_digest_tui/app.py:31-41` — `ResearchDigestApp.__init__` accepts optional `config_path` and `db_path` params
  - `research_digest_tui/__main__.py` — current entry point creates `ResearchDigestApp()` with no args
  - `research_digest_tui/services/runner_service.py:36-43` — hardcodes `["python", "rdt/digest.py", ...]`
  - `config_models.py` (137 lines) — self-contained Pydantic models, no local imports
  - `rich_utils.py` (173 lines) — Rich console helpers, no local imports
  - `scheduler_utils.py` (223 lines) — schedule library wrapper, one local import: `from rich_utils import print_info`
- **Gotchas:**
  - `test_scheduler.py` hangs due to `SignalHandler` blocking on signals — always run with `--ignore=tests/test_scheduler.py` or use `--timeout=60`
  - `pytest.ini` injects `--cov` into every run via `addopts` — use `--no-cov --override-ini="addopts="` for fast iteration
  - The two TUI service files (`config_service.py`, `scheduler_service.py`) currently import from top-level modules (`from config_models import ...`). In the committed state, these work because `sys.path` includes the repo root. After updating to package imports, they work because the modules exist inside the package.
  - `test_runner_service.py:37` asserts `"rdt/digest.py" in cmd` — this test must be updated when RunnerService changes

## Assumptions

- hatchling can build a wheel from the existing `pyproject.toml` once all referenced files exist — supported by the `[tool.hatch.build.targets.wheel]` config already present
- The three modules (`config_models`, `rich_utils`, `scheduler_utils`) can be copied into the package without changes (except `scheduler_utils`'s one local import) — supported by reading each file and confirming they only import from stdlib/third-party
- `ResearchDigestApp` already accepts `config_path` and `db_path` — confirmed at `app.py:31-41`. Tasks 3-4 depend on this.
- The `research_config.yaml` in the repo root is a good template for the bundled default config — Task 4 depends on this
- The runner_service test at `test_runner_service.py:37` is the only test that will break when RunnerService changes — Task 5 depends on this. Verified by grep: only `test_runner_service.py` tests `RunnerService`.

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Import conflict: top-level `config_models.py` and `research_digest_tui/config_models.py` both resolve on sys.path | Low | High | The package-internal imports use absolute paths (`from research_digest_tui.config_models import X`), which always resolve to the package copy. Top-level imports continue resolving to the original. |
| hatchling build includes wrong files or misses `.tcss` stylesheets | Medium | Medium | Task 7 explicitly verifies wheel contents with zipfile inspection before venv install. |
| RunnerService `shutil.which("research-digest")` finds a stale or wrong binary | Low | Medium | Test both paths (installed and dev fallback) in Task 5. Dev fallback uses `sys.executable` to match the running Python. |
| test_scheduler.py hang blocks CI/local dev during this work | Medium | Low | Always exclude with `--ignore=tests/test_scheduler.py`. Noted in every task's Verify section. |

## Goal Verification

### Truths

1. After `pip install` of the built wheel into a clean venv, `Research_Toolkit` resolves as a command
2. `from research_digest_tui.cli import main` succeeds in the clean venv
3. `from research_digest_tui.config_models import ResearchDigestConfig` succeeds in the clean venv
4. All currently-passing tests still pass (excluding pre-existing failures in test_http_client and test_scheduler)
5. The original top-level `config_models.py`, `rich_utils.py`, `scheduler_utils.py` are byte-identical to HEAD — untouched
6. `research_config.yaml` (repo root) is unchanged
7. The `INSTALL.md` file exists with Linux/macOS/Windows instructions

### Artifacts

1. `research_digest_tui/cli.py` — entry point with `_find_or_create_config()` and `main()`
2. `research_digest_tui/config_models.py` — package-internal copy
3. `research_digest_tui/rich_utils.py` — package-internal copy
4. `research_digest_tui/scheduler_utils.py` — package-internal copy (with fixed import)
5. `research_digest_tui/data/research_config.default.yaml` — bundled starter config
6. `tests/test_cli_entry.py` — tests for config discovery and entry point
7. `INSTALL.md` — cross-platform installation guide

## Progress Tracking

- [x] Task 0: Revert uncommitted changes
- [x] Task 1: Copy shared modules into TUI package
- [x] Task 2: Update TUI service imports
- [x] Task 3: Create cli.py entry point (TDD)
- [x] Task 4: Bundle default config
- [x] Task 5: Fix RunnerService for installed environments (TDD)
- [x] Task 6: Update __main__.py
- [x] Task 7: Remove research-digest entry point from pyproject.toml
- [x] Task 8: Build and verify wheel
- [x] Task 9: Documentation (INSTALL.md + README)
      **Total Tasks:** 10 | **Completed:** 10 | **Remaining:** 0

## Implementation Tasks

---

### Task 0: Revert uncommitted changes

**Objective:** Restore the working tree to the committed state so all three top-level modules are intact originals and no package-internal copies exist yet.

**Dependencies:** None

**Files:**

- Restore: `config_models.py` (from shim back to original)
- Restore: `rich_utils.py` (from shim back to original)
- Restore: `scheduler_utils.py` (from shim back to original)
- Restore: `research_digest_tui/services/config_service.py` (revert import change)
- Restore: `research_digest_tui/services/scheduler_service.py` (revert import change)
- Remove: `research_digest_tui/config_models.py` (untracked copy)
- Remove: `research_digest_tui/rich_utils.py` (untracked copy)
- Remove: `research_digest_tui/scheduler_utils.py` (untracked copy)
- Restore: `.gitignore` (minor change)

**Key Decisions / Notes:**

- The three `research_digest_tui/*.py` files are staged (`A` in git status), not untracked. `git clean -f` only removes untracked files and silently skips staged ones. Correct sequence: (1) `git checkout -- .gitignore config_models.py rich_utils.py scheduler_utils.py research_digest_tui/services/config_service.py research_digest_tui/services/scheduler_service.py` to restore tracked files, (2) `git reset HEAD research_digest_tui/config_models.py research_digest_tui/rich_utils.py research_digest_tui/scheduler_utils.py` to unstage the new files, (3) `rm research_digest_tui/config_models.py research_digest_tui/rich_utils.py research_digest_tui/scheduler_utils.py` to delete the now-untracked files.
- The 9 files in the uncommitted diff are: `.gitignore` (M), `config_models.py` (M), `rich_utils.py` (M), `scheduler_utils.py` (M), `research_digest_tui/services/config_service.py` (M), `research_digest_tui/services/scheduler_service.py` (M), `research_digest_tui/config_models.py` (A), `research_digest_tui/rich_utils.py` (A), `research_digest_tui/scheduler_utils.py` (A)

**Definition of Done:**

- [ ] `git status` shows clean working tree (no modified or untracked files except docs/plans/ and docs/prd/)
- [ ] `git diff HEAD` shows no changes to tracked files
- [ ] `config_models.py` line 1 is `#!/usr/bin/env python3` and line 3 is `"""Pydantic models for configuration validation."""` (original, not shim)

**Verify:**

```bash
git status
git diff HEAD --stat
head -3 config_models.py
```

---

### Task 1: Copy shared modules into TUI package

**Objective:** Duplicate `config_models.py`, `rich_utils.py`, and `scheduler_utils.py` into `research_digest_tui/` as package-internal modules. Fix the one local import in `scheduler_utils.py`.

**Dependencies:** Task 0

**Files:**

- Create: `research_digest_tui/config_models.py`
- Create: `research_digest_tui/rich_utils.py`
- Create: `research_digest_tui/scheduler_utils.py`
- Test: `tests/test_package_imports.py`

**Key Decisions / Notes:**

- TDD: Write a test that imports from `research_digest_tui.config_models`, `research_digest_tui.rich_utils`, `research_digest_tui.scheduler_utils` — expect `ImportError` (RED). Then copy files (GREEN).
- `config_models.py` and `rich_utils.py` are pure copies — no changes needed.
- `scheduler_utils.py` has one local import to fix: `from rich_utils import print_info` → `from research_digest_tui.rich_utils import print_info`
- The originals at the repo root must remain byte-identical to HEAD after this task.

**Definition of Done:**

- [ ] `from research_digest_tui.config_models import ResearchDigestConfig` succeeds
- [ ] `from research_digest_tui.rich_utils import get_console` succeeds
- [ ] `from research_digest_tui.scheduler_utils import ScheduleError` succeeds
- [ ] Original top-level files are unchanged (`git diff config_models.py rich_utils.py scheduler_utils.py` shows nothing)
- [ ] New test file passes

**Verify:**

```bash
uv run pytest tests/test_package_imports.py -q --no-cov --override-ini="addopts="
git diff config_models.py rich_utils.py scheduler_utils.py
```

---

### Task 2: Update TUI service imports

**Objective:** Change `config_service.py` and `scheduler_service.py` to import from the package-internal copies instead of the top-level modules.

**Dependencies:** Task 1

**Files:**

- Modify: `research_digest_tui/services/config_service.py` (line 9: `from config_models import ...` → `from research_digest_tui.config_models import ...`)
- Modify: `research_digest_tui/services/scheduler_service.py` (line 8: `from scheduler_utils import ...` → `from research_digest_tui.scheduler_utils import ...`)

**Key Decisions / Notes:**

- Use absolute imports (`from research_digest_tui.X import Y`) not relative (`from ..X import Y`) — consistent with existing codebase style.
- **Intentional revert-then-reapply:** The working tree before Task 0 already has these imports at the package-qualified form. Task 0 intentionally reverts them to the original top-level form (from HEAD). Task 2 re-applies the change after the package-internal modules exist (Task 1), ensuring the import chain is valid. This is not a mistake — it is the duplicate-first strategy in action.
- Existing service tests in `tests/test_config_service.py`, `tests/test_scheduler_service.py`, and `tests/test_tui_services.py` should still pass since the modules contain identical code.

**Definition of Done:**

- [ ] `config_service.py` line 9 reads `from research_digest_tui.config_models import ResearchDigestConfig`
- [ ] `scheduler_service.py` line 8 reads `from research_digest_tui.scheduler_utils import ScheduleError, parse_schedule_string`
- [ ] All service tests pass

**Verify:**

```bash
uv run pytest tests/test_config_service.py tests/test_scheduler_service.py tests/test_tui_services.py -q --no-cov --override-ini="addopts="
```

---

### Task 3: Create cli.py entry point (TDD)

**Objective:** Create `research_digest_tui/cli.py` with XDG-style config discovery (`_find_or_create_config`) and a `main()` function that launches the TUI with the discovered config.

**Dependencies:** Task 1 (package modules must exist), Task 2 (services use package imports)

**Files:**

- Create: `research_digest_tui/cli.py`
- Create: `tests/test_cli_entry.py`

**Key Decisions / Notes:**

- TDD: Write tests FIRST for `_find_or_create_config()`:
  1. Config in CWD → returns CWD path
  2. Config in `~/.research_digest/` → returns home path
  3. No config anywhere → copies bundled default to `~/.research_digest/`, returns that path
  4. Return value is always a `Path` object
- Config discovery helpers (`_cwd_config()`, `_home_config()`) are extracted as separate functions for testability — tests patch these instead of `Path.cwd()` / `Path.home()`.
- `main()` calls `_find_or_create_config()`, constructs `ResearchDigestApp(config_path=..., db_path=...)`, calls `app.run()`.
- `_bundled_default()` returns `Path(__file__).parent / "data" / "research_config.default.yaml"` — the bundled file created in Task 4.
- Tests for `_find_or_create_config()` don't need Task 4's bundled file — they test the logic, not the file copy. The "first run" test creates the directory and verifies the copy operation using a mock or tmp_path.
- This is the module that `pyproject.toml` already references: `Research_Toolkit = "research_digest_tui.cli:main"`.

**Definition of Done:**

- [ ] `from research_digest_tui.cli import _find_or_create_config, main` succeeds
- [ ] All 4+ config discovery tests pass
- [ ] `_find_or_create_config()` returns correct path for CWD, home, and first-run scenarios
- [ ] `main()` function exists and is callable

**Verify:**

```bash
uv run pytest tests/test_cli_entry.py -q --no-cov --override-ini="addopts="
```

---

### Task 4: Bundle default config

**Objective:** Create the bundled default config file that `cli.py` copies to `~/.research_digest/` on first run.

**Dependencies:** Task 3 (cli.py references this file via `_bundled_default()`)

**Files:**

- Create: `research_digest_tui/data/__init__.py`
- Create: `research_digest_tui/data/research_config.default.yaml`

**Key Decisions / Notes:**

- The bundled config is a minimal starter version of `research_config.yaml` with all scrapers disabled by default.
- Must include commented examples showing how to enable each scraper.
- The `research_digest_tui/data/` directory needs an `__init__.py` to be included in the wheel by hatchling.
- After creating, verify `_bundled_default().exists()` returns True.
- **Pre-flight hatchling check:** After creating the .yaml file, immediately run `uv run python -m hatchling build` and inspect the wheel to verify the .yaml is included. If absent, add `"research_digest_tui/data/*.yaml"` to the `include` list in `[tool.hatch.build.targets.wheel]`. This catches inclusion gaps at Task 4 rather than waiting until Task 8.

**Definition of Done:**

- [ ] `research_digest_tui/data/research_config.default.yaml` exists and contains `scrapers` section
- [ ] `research_digest_tui/data/__init__.py` exists (can be empty)
- [ ] `from research_digest_tui.cli import _bundled_default; assert _bundled_default().exists()`
- [ ] The bundled config has all scrapers set to `enabled: false`

**Verify:**

```bash
uv run python -c "from research_digest_tui.cli import _bundled_default; p = _bundled_default(); assert p.exists(), f'Not found: {p}'; print(f'OK: {p}')"
# Pre-flight: verify hatchling includes .yaml in wheel
rm -rf dist/
uv run python -m hatchling build 2>&1 | tail -3
uv run python -c "import zipfile, glob; z=zipfile.ZipFile(sorted(glob.glob('dist/*.whl'))[-1]); yaml_files=[f for f in z.namelist() if f.endswith('.yaml')]; print(f'YAML files in wheel: {yaml_files}'); assert any('default.yaml' in f for f in yaml_files), 'Bundled config NOT in wheel — add to hatch include list'"
```

---

### Task 5: Fix RunnerService for installed environments (TDD)

**Objective:** Update `RunnerService.run_scraper()` to prefer the installed `research-digest` console script when available, falling back to `sys.executable rdt/digest.py` for dev usage.

**Dependencies:** Task 2

**Files:**

- Modify: `research_digest_tui/services/runner_service.py`
- Modify: `tests/test_runner_service.py` (update existing test, add new tests)

**Key Decisions / Notes:**

- TDD: Write tests FIRST for a new `_build_scraper_cmd(config_path, scraper_key)` function:
  1. When `shutil.which("research-digest")` returns a path → use it as cmd[0]
  2. When `shutil.which` returns None → use `[sys.executable, "<repo_root>/rdt/digest.py", ...]`
- Extract command building into `_build_scraper_cmd()` so `run_scraper()` just calls it.
- The existing test at `test_runner_service.py:37` checks `"rdt/digest.py" in cmd` — update this to mock `shutil.which` returning None (dev fallback path) so the assertion remains valid.
- **Pre-existing defect fix:** The current implementation uses bare `"python"` which may not resolve in all venv configurations. The dev fallback path fixes this by using `sys.executable`, which always points to the active interpreter. This is a pre-existing defect fix bundled with the installed-path feature — do not revert or soften the `sys.executable` change thinking it is scope creep.
- Dev fallback uses `Path(__file__).resolve().parent.parent` to find repo root, then appends `rdt/digest.py`.

**Definition of Done:**

- [ ] `_build_scraper_cmd()` returns installed path when `shutil.which` finds it
- [ ] `_build_scraper_cmd()` returns `sys.executable + rdt/digest.py` when not installed
- [ ] All runner service tests pass (existing + new)
- [ ] No changes to `RunnerService.__init__` signature

**Verify:**

```bash
uv run pytest tests/test_runner_service.py -q --no-cov --override-ini="addopts="
```

---

### Task 6: Update __main__.py

**Objective:** Change `research_digest_tui/__main__.py` to delegate to `cli.main()` so `python -m research_digest_tui` uses the same config discovery as the `Research_Toolkit` command.

**Dependencies:** Task 3 (cli.py must exist)

**Files:**

- Modify: `research_digest_tui/__main__.py`

**Key Decisions / Notes:**

- Replace current content (which creates `ResearchDigestApp()` with no args) with a delegation to `cli.main()`.
- New content:
  ```python
  #!/usr/bin/env python3
  """Entry point for `python -m research_digest_tui`."""
  from research_digest_tui.cli import main
  if __name__ == "__main__":
      main()
  ```
- Existing TUI integration tests use `ResearchDigestApp().run_test()` directly — they don't go through `__main__.py`, so they're unaffected.

**Definition of Done:**

- [ ] `python -c "import research_digest_tui.__main__; print('OK')"` succeeds
- [ ] `__main__.py` imports from `research_digest_tui.cli`
- [ ] Existing TUI tests still pass

**Verify:**

```bash
uv run python -c "import research_digest_tui.__main__; print('OK')"
uv run pytest tests/test_tui_integration.py -q --no-cov --override-ini="addopts=" -x --timeout=30
```

---

### Task 7: Remove research-digest entry point from pyproject.toml

**Objective:** Remove the untested `research-digest` console script entry point from `pyproject.toml`.

**Dependencies:** None (can be done any time)

**Files:**

- Modify: `pyproject.toml`

**Key Decisions / Notes:**

- Remove the line `research-digest = "research_digest:app"` from `[project.scripts]`.
- The `Research_Toolkit` entry point stays.
- Also keep the `rdt/digest.py` in the `[tool.hatch.build.targets.wheel] include` list — it's still used by RunnerService's dev fallback.
- Update the comment on the `include` block from `# Top-level runtime modules: shims + CLI orchestrator` to `# Top-level runtime modules included for dev-fallback in RunnerService`.

**Definition of Done:**

- [ ] `pyproject.toml` `[project.scripts]` has only `Research_Toolkit`
- [ ] pyproject.toml include block comment reads `# Top-level runtime modules included for dev-fallback in RunnerService`
- [ ] TOML is valid

**Verify:**

```bash
uv run python -c "import tomllib; d=tomllib.load(open('pyproject.toml','rb')); scripts=d['project']['scripts']; assert 'Research_Toolkit' in scripts; assert 'research-digest' not in scripts; print('OK:', scripts)"
```

---

### Task 8: Build and verify wheel

**Objective:** Build the wheel with hatchling, install into a clean venv, verify the entry point resolves and key imports work.

**Dependencies:** Tasks 0-7

**Files:** None new — validation only.

**Key Decisions / Notes:**

- Build: `uv run python -m hatchling build`
- Inspect wheel contents with zipfile to verify key files are present:
  - `research_digest_tui/cli.py`
  - `research_digest_tui/config_models.py`
  - `research_digest_tui/rich_utils.py`
  - `research_digest_tui/scheduler_utils.py`
  - `research_digest_tui/data/research_config.default.yaml`
  - `.tcss` files (stylesheets must be in the wheel)
- Create temp venv, install wheel, verify:
  - `Research_Toolkit` entry point exists
  - `from research_digest_tui.cli import main` succeeds
  - `from research_digest_tui.config_models import ResearchDigestConfig` succeeds
- Clean up temp venv and dist/ after verification.
- If the build fails, check hatchling configuration — the `packages` and `include` lists in `[tool.hatch.build.targets.wheel]` must match the actual file layout.

**Definition of Done:**

- [ ] Wheel builds successfully in `dist/`
- [ ] Wheel contains all key files (cli.py, config_models.py, rich_utils.py, scheduler_utils.py, default config)
- [ ] Wheel contains at least 7 .tcss files (app.tcss + dashboard.tcss, scraper_management.tcss, configuration.tcss, logs.tcss, history.tcss, scheduler.tcss)
- [ ] Entry point resolves in clean venv
- [ ] Key imports work in clean venv
- [ ] Full test suite passes from repo root (excluding pre-existing failures)

**Verify:**

```bash
uv run python -m hatchling build
# Then verify wheel contents and install test (scripted in implementation)
uv run pytest -q --no-cov --override-ini="addopts=" --ignore=tests/test_scheduler.py --ignore=tests/test_http_client.py
```

---

### Task 9: Documentation (INSTALL.md + README)

**Objective:** Create `INSTALL.md` with cross-platform install instructions and add an Installation section to `README.md`.

**Dependencies:** Task 8 (wheel must be verified first)

**Files:**

- Create: `INSTALL.md`
- Modify: `README.md`

**Key Decisions / Notes:**

- `INSTALL.md` covers: Linux (uv + pip), macOS (Homebrew Python + pip/uv), Windows (winget Python + pip).
- First-run config path: `~/.research_digest/research_config.yaml` on all platforms.
- Development install: `uv pip install -e ".[dev]"` from cloned repo.
- `README.md` gets a short `## Installation` section between Key Features and The Toolkit, linking to `INSTALL.md` for details.
- Remove the `research-digest` references from install examples since that entry point was removed in Task 7.

**Definition of Done:**

- [ ] `INSTALL.md` exists with Linux/macOS/Windows sections
- [ ] `README.md` has an Installation section
- [ ] No dead links in README (grep for `.md` links, verify files exist)

**Verify:**

```bash
test -f INSTALL.md && echo "INSTALL.md exists" || echo "MISSING"
grep -c "Installation" README.md
```

---

## Open Questions

None — all decisions resolved during planning.

### Deferred Ideas

- **Replace top-level modules with shims** — after the package is proven in use, the originals can be replaced with `from research_digest_tui.X import *` shims. This was the old plan's approach but is intentionally deferred.
- **Re-add `research-digest` CLI entry point** — once the CLI orchestrator is verified to work from an installed wheel.
- **Fix pre-existing test failures** — `test_http_client.py` (4 failures), `test_scheduler.py` (8 failures + hang). Separate issue.
- **Release branch + git tag** — create `release/v1.0.0` branch after all tasks verified and committed.
