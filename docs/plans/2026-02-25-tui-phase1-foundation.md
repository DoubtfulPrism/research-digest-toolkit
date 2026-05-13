# TUI Phase 1 Foundation Implementation Plan

Created: 2026-02-25
Status: VERIFIED
Approved: Yes
Iterations: 0
Worktree: Yes
Type: Feature

> **Status Lifecycle:** PENDING → COMPLETE → VERIFIED
> **Iterations:** Tracks implement→verify cycles (incremented by verify phase)
>
> - PENDING: Initial state, awaiting implementation
> - COMPLETE: All tasks implemented
> - VERIFIED: All checks passed
>
> **Approval Gate:** Implementation CANNOT proceed until `Approved: Yes`
> **Worktree:** Set at plan creation (from dispatcher). `Yes` uses git worktree isolation; `No` works directly on current branch (default)
> **Type:** `Feature` or `Bugfix` — set at planning time, used by dispatcher for routing

## Summary

**Goal:** Implement Phase 1 (Foundation) of the TUI migration - create a navigable Textual application with 6 placeholder screens (Dashboard, Scraper Management, Configuration, Logs, History/Analytics, Scheduler) and basic CLI integration via `--tui` flag.

**Architecture:** Build on existing TUI code from the previous worktree (`spec-tui-migration-phase1-8537b4f`), which has 3 of 6 screens implemented. Add the missing 3 screens (Logs, History, Scheduler), update navigation for all 6 screens, and integrate with the main CLI.

**Tech Stack:**
- Textual 0.85.0 (TUI framework built on Rich)
- Existing Rich theme from `rich_utils.py`
- Typer CLI integration via `--tui` flag

## Scope

### In Scope

- Copy existing TUI implementation (Dashboard, Scraper Management, Configuration, ScraperCard widget)
- Create 3 new placeholder screens (Logs, History/Analytics, Scheduler)
- Update app.py navigation to include all 6 screens
- Add keyboard shortcuts for all screens (d, s, c, l, h, u)
- Add `--tui` flag to `rdt/digest.py`
- CSS styling for new screens
- Unit tests for all new screens
- `__main__.py` entry point for `python -m research_digest_tui`

### Out of Scope

- Backend integration (Phase 2)
- Real-time data updates (Phase 3)
- Configuration editing (Phase 4)
- Schedule management logic (Phase 5)
- Polars analytics integration (Phase 2)

## Prerequisites

- Textual 0.85.0 installed via `uv pip install textual==0.85.0`
- Existing worktree at `.worktrees/spec-tui-phase1-foundation-8537b4f/`

## Context for Implementer

> This section is critical for cross-session continuity. Write it for an implementer who has never seen the codebase.

- **Patterns to follow:** Copy the screen structure from existing screens in `spec-tui-migration-phase1-8537b4f/research_digest_tui/screens/dashboard.py` — each screen extends `Screen`, has `BINDINGS`, and implements `compose()` → `ComposeResult`
- **Conventions:**
  - Screens: One file per screen, `{name}.py` + `{name}.tcss`
  - Widgets: Extend `Container` or `Widget`, use reactive properties
  - CSS: Colors match Rich theme (success=green, error=red, warning=yellow, info=blue, header=cyan)
  - Keyboard shortcuts: Single lowercase letter (d=Dashboard, s=Scrapers, c=Config, l=Logs, h=History, u=Scheduler)
  - **Why 'u' for Scheduler:** The TUI spec doesn't specify scheduler shortcut. 's' is taken by Scrapers, 'h' by History. 'u' chosen as mnemonic for "sched**U**ler" — avoids confusion with 'x' which some TUI apps use for exit/close.
- **Key files:**
  - `research_digest_tui/app.py` - Main application with SCREENS dict and BINDINGS
  - `research_digest_tui/screens/__init__.py` - Screen exports
  - `rich_utils.py` - Rich theme constants (reference for TUI colors)
- **Gotchas:**
  - Textual CSS uses `$` variables for theming (e.g., `$primary`, `$background`, `$text-muted`)
  - Screen classes must be registered in `app.SCREENS` dict
  - Footer shows current bindings automatically
- **Domain context:** The TUI is a dashboard for managing research scraper runs. Phase 1 is purely navigation with placeholder content.

## Progress Tracking

**MANDATORY: Update this checklist as tasks complete. Change `[ ]` to `[x]`.**

- [x] Task 1: Copy existing TUI implementation
- [x] Task 2: Create Logs placeholder screen
- [x] Task 3: Create History/Analytics placeholder screen
- [x] Task 4: Create Scheduler placeholder screen
- [x] Task 5: Update app navigation for all 6 screens
- [x] Task 6: Integrate TUI with CLI (`--tui` flag)
- [x] Task 7: Add tests for new screens

**Total Tasks:** 7 | **Completed:** 7 | **Remaining:** 0

## Implementation Tasks

### Task 1: Copy Existing TUI Implementation

**Objective:** Copy the working TUI code from the previous worktree to bootstrap the new implementation.

**Dependencies:** None

**Files:**

- Copy: `research_digest_tui/` (entire directory from `spec-tui-migration-phase1-8537b4f`)
- Copy: `tests/test_tui_screens.py`
- Copy: `tests/test_tui_widgets.py`

**Key Decisions / Notes:**

- Source: `.worktrees/spec-tui-migration-phase1-8537b4f/research_digest_tui/`
- Destination: `.worktrees/spec-tui-phase1-foundation-8537b4f/research_digest_tui/`
- This includes: `app.py`, `app.tcss`, `__init__.py`, `__main__.py`, `screens/`, `widgets/`
- **Dependency installation:** After copying files, must install Textual in the target worktree before verification
- After dependency install, verify the TUI launches with `python -m research_digest_tui`

**Definition of Done:**

- [ ] All TUI files copied to new worktree
- [ ] Tests copied to new worktree
- [ ] Textual dependency installed in target worktree
- [ ] TUI launches successfully with `python -m research_digest_tui`
- [ ] Existing tests pass

**Verify:**

- Copy files: `cp -r .worktrees/spec-tui-migration-phase1-8537b4f/research_digest_tui .worktrees/spec-tui-phase1-foundation-8537b4f/`
- Copy tests: `cp .worktrees/spec-tui-migration-phase1-8537b4f/tests/test_tui_*.py .worktrees/spec-tui-phase1-foundation-8537b4f/tests/`
- Install dependencies: `cd .worktrees/spec-tui-phase1-foundation-8537b4f && uv pip install textual==0.85.0`
- Launch: `cd .worktrees/spec-tui-phase1-foundation-8537b4f && python -m research_digest_tui` — app launches

---

### Task 2: Create Logs Placeholder Screen

**Objective:** Create a placeholder Logs screen with static content indicating future functionality.

**Dependencies:** Task 1

**Files:**

- Create: `research_digest_tui/screens/logs.py`
- Create: `research_digest_tui/screens/logs.tcss`
- Modify: `research_digest_tui/screens/__init__.py` (add export)

**Key Decisions / Notes:**

- Follow pattern from `configuration.py` (placeholder screen)
- Show placeholder message: "Log viewing will be available in Phase 3"
- Include log level filter buttons (disabled): INFO, WARN, ERROR
- Include mock log area with Static widget
- **CSS scoping:** Use screen-specific selectors prefixed with screen ID (e.g., `#logs-screen .placeholder-message`) to prevent CSS cascade conflicts with other screens

**Definition of Done:**

- [ ] `logs.py` screen created with compose() method
- [ ] `logs.tcss` styling created with scoped selectors
- [ ] Screen exported in `__init__.py`
- [ ] Screen can be instantiated without errors

**Verify:**

- `uv run pytest tests/test_tui_screens.py::test_logs_screen_creation -q` — passes

---

### Task 3: Create History/Analytics Placeholder Screen

**Objective:** Create a placeholder History/Analytics screen showing where Polars-powered analytics will go.

**Dependencies:** Task 1

**Files:**

- Create: `research_digest_tui/screens/history.py`
- Create: `research_digest_tui/screens/history.tcss`
- Modify: `research_digest_tui/screens/__init__.py` (add export)

**Key Decisions / Notes:**

- Follow pattern from `configuration.py` (placeholder screen)
- Show placeholder message: "History & Analytics will be available in Phase 2"
- Include mock chart area (ASCII bar chart placeholder)
- Include time range selector buttons (disabled): 7 Days, 30 Days, All Time
- **CSS scoping:** Use screen-specific selectors prefixed with screen ID (e.g., `#history-screen .chart-area`) to prevent CSS cascade conflicts with other screens

**Definition of Done:**

- [ ] `history.py` screen created with compose() method
- [ ] `history.tcss` styling created with scoped selectors
- [ ] Screen exported in `__init__.py`
- [ ] Screen can be instantiated without errors

**Verify:**

- `uv run pytest tests/test_tui_screens.py::test_history_screen_creation -q` — passes

---

### Task 4: Create Scheduler Placeholder Screen

**Objective:** Create a placeholder Scheduler screen showing where schedule management will go.

**Dependencies:** Task 1

**Files:**

- Create: `research_digest_tui/screens/scheduler.py`
- Create: `research_digest_tui/screens/scheduler.tcss`
- Modify: `research_digest_tui/screens/__init__.py` (add export)

**Key Decisions / Notes:**

- Follow pattern from `configuration.py` (placeholder screen)
- Show placeholder message: "Schedule management will be available in Phase 5"
- Show mock schedule list (e.g., "Daily Digest: every day at 06:00")
- Include Add Schedule button (disabled)
- **CSS scoping:** Use screen-specific selectors prefixed with screen ID (e.g., `#scheduler-screen .schedule-list`) to prevent CSS cascade conflicts with other screens

**Definition of Done:**

- [ ] `scheduler.py` screen created with compose() method
- [ ] `scheduler.tcss` styling created with scoped selectors
- [ ] Screen exported in `__init__.py`
- [ ] Screen can be instantiated without errors

**Verify:**

- `uv run pytest tests/test_tui_screens.py::test_scheduler_screen_creation -q` — passes

---

### Task 5: Update App Navigation for All 6 Screens

**Objective:** Update `app.py` to register all 6 screens and add keyboard bindings.

**Dependencies:** Tasks 2, 3, 4

**Files:**

- Modify: `research_digest_tui/app.py`

**Key Decisions / Notes:**

- Add imports for Logs, History, Scheduler screens
- Update SCREENS dict to include all 6 screens
- Update BINDINGS to include:
  - `d` - Dashboard
  - `s` - Scrapers
  - `c` - Config
  - `l` - Logs
  - `h` - History
  - `u` - Scheduler (using 'u' for "sched**U**ler" to avoid confusion with 'x' = exit in some TUI apps)
- Add CSS_PATH entries for new screen CSS files
- Add action methods: `action_show_logs()`, `action_show_history()`, `action_show_scheduler()`
- **Navigation pattern:** Use `switch_screen()` for all top-level navigation from keyboard shortcuts. This replaces the current screen (no stack buildup). Don't use `push_screen()` for primary navigation — that's for modal dialogs or sub-views where ESC should return to the previous screen.

**Definition of Done:**

- [ ] All 6 screens registered in SCREENS dict
- [ ] All keyboard bindings working (d, s, c, l, h, u)
- [ ] Navigation works between all screens using switch_screen()
- [ ] Footer shows all binding options

**Verify:**

- `uv run pytest tests/test_tui_screens.py::test_app_has_screens_registered -q` — shows 6 screens
- `python -m research_digest_tui` — can navigate to all screens with keyboard

---

### Task 6: Integrate TUI with CLI (`--tui` Flag)

**Objective:** Add `--tui` flag to `rdt/digest.py` to launch the TUI application.

**Dependencies:** Task 5

**Files:**

- Modify: `rdt/digest.py`

**Key Decisions / Notes:**

- Add `--tui` boolean flag to the Typer app
- When `--tui` is passed, import and run `ResearchDigestApp`
- Skip normal CLI flow when TUI is active
- Ensure TUI can be launched with: `python rdt/digest.py --tui`

**Definition of Done:**

- [ ] `--tui` flag added to rdt/digest.py
- [ ] TUI launches when flag is passed
- [ ] Normal CLI behavior preserved when flag is not passed
- [ ] Help text shows `--tui` option

**Verify:**

- `python rdt/digest.py --help` — shows `--tui` option
- `python rdt/digest.py --tui` — launches TUI

---

### Task 7: Add Tests for New Screens

**Objective:** Add unit tests for the 3 new screens (Logs, History, Scheduler).

**Dependencies:** Tasks 2, 3, 4, 5

**Files:**

- Modify: `tests/test_tui_screens.py`

**Key Decisions / Notes:**

- Follow existing test pattern in `test_tui_screens.py`
- Test screen creation, compose() method, and app registration
- Test keyboard bindings include all 6 screens
- **Parametrized tests:** Use `@pytest.mark.parametrize` to test all 6 screens with a single test function (e.g., `test_screen_can_instantiate(screen_class)`) to reduce duplication. Create separate tests only for screen-specific behavior (e.g., Dashboard has ScraperCard widgets, others don't).

**Definition of Done:**

- [ ] Test for Logs screen creation
- [ ] Test for History screen creation
- [ ] Test for Scheduler screen creation
- [ ] Test that app has all 6 screens registered
- [ ] Test keyboard bindings include all 6 screens (d, s, c, l, h, u)
- [ ] All tests pass

**Verify:**

- `uv run pytest tests/test_tui_screens.py -q` — all tests pass
- `uv run pytest -q` — full test suite passes

---

## Runtime Environment

**Start TUI (standalone):**
```bash
cd .worktrees/spec-tui-phase1-foundation-8537b4f
python -m research_digest_tui
```

**Start TUI (via CLI flag):**
```bash
cd .worktrees/spec-tui-phase1-foundation-8537b4f
python rdt/digest.py --tui
```

**Expected behavior:**
- TUI launches in full-screen terminal mode
- Dashboard screen displays by default
- Footer shows keyboard bindings: [D] Dashboard [S] Scrapers [C] Config [L] Logs [H] History [U] Scheduler [Q] Quit
- Keyboard shortcuts navigate between screens
- Q quits (note: since we use switch_screen for navigation, ESC behavior is not used for returning to previous screen in Phase 1)

## Testing Strategy

- **Unit tests:** Test screen instantiation, app creation, keyboard bindings
- **Integration tests:** Manual testing of navigation between all 6 screens
- **Manual verification:**
  1. Launch TUI with `python -m research_digest_tui`
  2. Press each keyboard shortcut (d, s, c, l, h, u)
  3. Verify correct screen displays
  4. Press q to quit
  5. Test in 80-column terminal to verify footer doesn't overflow with 7+ bindings

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
| ---- | ---------- | ------ | ---------- |
| Textual version incompatibility | Low | Medium | Pin to exact version 0.85.0 in requirements |
| CSS conflicts between screens | Low | Low | Use screen-specific CSS files with scoped selectors (e.g., `#logs-screen .class`) |
| Keyboard shortcut confusion | Low | Low | Use mnemonic shortcuts (u=schedUler, l=Logs, h=History) and test all bindings |
| Footer overflow in narrow terminals | Low | Low | Test in 80-col terminal; use short binding descriptions if needed |
| Worktree missing Textual dependency | Medium | High | Explicitly install textual==0.85.0 before verification in Task 1 |

## Goal Verification

> Derived from the plan's goal using goal-backward methodology. The spec-reviewer-goal agent verifies these criteria during verification.

### Truths (what must be TRUE for the goal to be achieved)

- Users can launch the TUI with `python rdt/digest.py --tui`
- Users can navigate to all 6 screens using keyboard shortcuts
- All screens display placeholder content indicating future functionality
- Footer shows all available keyboard bindings

### Artifacts (what must EXIST to support those truths)

- `research_digest_tui/` package with `app.py`, `__init__.py`, `__main__.py`
- `research_digest_tui/screens/` with 6 screen files
- `research_digest_tui/widgets/` with ScraperCard widget
- `tests/test_tui_screens.py` with tests for all screens

### Key Links (critical connections that must be WIRED)

- `--tui` flag in `rdt/digest.py` → imports and runs `ResearchDigestApp`
- Keyboard bindings in `app.BINDINGS` → action methods `action_show_*`
- `app.SCREENS` dict → all 6 screen classes
- Screen `__init__.py` exports → screen classes used by `app.py`

## Open Questions

- None - all decisions made during planning
