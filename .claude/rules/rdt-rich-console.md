## Rich Console Output Pattern

**Use `rich_utils.py` helpers for all user-facing output. Always respect the `verbose` flag.**

### The Pattern

```python
from rich_utils import print_success, print_error, print_warning, print_info, print_progress

print_success("Content saved", verbose=True)      # Green
print_error("Failed to fetch URL", verbose=True)   # Red
print_warning("Rate limit approaching", verbose=True)  # Yellow
print_info("Starting scraper...", verbose=True)     # Blue
print_progress("Item 3/10", verbose=True)           # Cyan
```

### Progress Bars

```python
from rich.progress import Progress, SpinnerColumn, TextColumn

with Progress(SpinnerColumn(), TextColumn("{task.description}")) as progress:
    task = progress.add_task("Fetching...", total=len(items))
    for item in items:
        process_item(item)
        progress.update(task, advance=1)
```

### Tables

```python
from rich.console import Console
from rich.table import Table

console = Console()
table = Table(title="Scraped Items")
table.add_column("Source", style="cyan")
table.add_column("Count", style="magenta")
table.add_row("HackerNews", "15")
console.print(table)
```

### Rules

- **Always pass `verbose` parameter** — all `rich_utils` functions gate output on it
- **Reuse Console instances** — don't create `Console()` inside loops
- **Use `verbose=False` for batch operations** — prevents console flooding
- **Use `rich_utils` helpers, not raw `print()`** — consistent formatting across project

### Common Mistakes

- Not respecting `verbose` flag — floods console in quiet mode
- Using `print()` instead of Rich helpers — loses color/formatting
- Creating new `Console()` per call in hot loops — slow
