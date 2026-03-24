## TUI Architecture (Textual)

**6-screen Textual application for managing research digest workflows.**

### Application Structure

```
research_digest_tui/
├── app.py           # ResearchDigestApp — main App subclass
├── app.tcss         # Global styles
├── __main__.py      # Entry: python -m research_digest_tui
├── screens/         # One Screen subclass per view
│   ├── dashboard.py, configuration.py, scraper_management.py
│   ├── logs.py, history.py, scheduler.py
│   └── *.tcss       # Per-screen stylesheets
└── widgets/         # Reusable Widget subclasses
    └── scraper_card.py
```

### Screen Navigation

Keyboard shortcuts switch between screens:

| Key | Screen | Class |
|-----|--------|-------|
| `d` | Dashboard | `Dashboard` |
| `s` | Scrapers | `ScraperManagement` |
| `c` | Config | `Configuration` |
| `l` | Logs | `Logs` |
| `h` | History | `History` |
| `u` | Scheduler | `Scheduler` |
| `q` | Quit | — |

Navigation uses `self.switch_screen("name")` in App action methods. Screens are registered in `SCREENS` dict on `ResearchDigestApp`.

### Screen Pattern

```python
from textual.screen import Screen
from textual.widgets import Header, Footer, Static

class MyScreen(Screen):
    BINDINGS = [...]  # Screen-specific bindings

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("Content")
        yield Footer()
```

### Styling

- **Global styles:** `app.tcss` — loaded via `CSS_PATH` on App
- **Per-screen styles:** `screens/{name}.tcss` — also in `CSS_PATH`
- Textual CSS uses CSS-like syntax with widget selectors

### Running

```bash
python -m research_digest_tui     # Module entry point
# Or directly:
python research_digest_tui/app.py
```

### Testing

TUI tests use `App.run_test()` async context manager:

```python
@pytest.mark.tui
async def test_screen_navigation():
    async with ResearchDigestApp().run_test() as pilot:
        await pilot.press("s")  # Switch to scrapers
        assert pilot.app.screen.__class__.__name__ == "ScraperManagement"
```

Use `pytest.importorskip("textual")` at top of TUI test files.

### Phase 2 (In Progress)

Service layer integration: `ConfigService` (YAML/Pydantic), `DataService` (Polars database queries), wired into App and screens for real data display. See `docs/specs/tui-migration.md` for the full 5-phase plan.
