## Rich Console Output Pattern

**Beautiful terminal output with progress bars, color-coded messages, and formatted tables.**

### When to Apply

- CLI tools with user-facing output
- Progress tracking for long-running operations
- Status messages (success, warning, error, info)
- Structured data display (tables, lists)

### The Pattern

**1. Use helper functions from rich_utils.py:**

```python
from rich_utils import (
    print_success,
    print_error,
    print_warning,
    print_info,
    print_progress,
)

# Status messages
print_success("Content saved successfully", verbose=True)
print_error("Failed to fetch URL", verbose=True)
print_warning("Rate limit approaching", verbose=True)
print_info("Starting scraper...", verbose=True)

# Progress indication
print_progress("Processing item 3/10", verbose=True)
```

**2. Create progress bars for iteration:**

```python
from rich.progress import Progress, SpinnerColumn, TextColumn

with Progress(
    SpinnerColumn(),
    TextColumn("[progress.description]{task.description}"),
) as progress:
    task = progress.add_task("Fetching items...", total=len(items))
    for item in items:
        process_item(item)
        progress.update(task, advance=1)
```

**3. Display tables:**

```python
from rich.console import Console
from rich.table import Table

console = Console()
table = Table(title="Scraped Items")
table.add_column("Source", style="cyan")
table.add_column("Count", style="magenta")
table.add_row("HackerNews", "15")
table.add_row("RSS Feeds", "23")
console.print(table)
```

### Rich Console Colors

| Function | Color | Use When |
|----------|-------|----------|
| `print_success()` | Green | Operation completed successfully |
| `print_error()` | Red | Fatal error, operation failed |
| `print_warning()` | Yellow | Non-fatal issue, degraded performance |
| `print_info()` | Blue | Informational status update |
| `print_progress()` | Cyan | Progress indication |

### Why

- **User experience** - Colored output is easier to scan
- **Visibility** - Progress bars show long operations aren't hanging
- **Professionalism** - Rich formatting looks polished vs plain text
- **Debugging** - Color-coded log levels highlight important messages

### Common Mistakes

- Not respecting `verbose` flag - floods console in quiet mode
- Using `print()` instead of Rich helpers - loses color/formatting
- Not cleaning up progress bars - leaves terminal in bad state
- Overusing colors - too many colors is distracting

### Examples

**Good:**

```python
from rich_utils import print_info, print_success, print_error

def scrape_feed(url, verbose=True):
    print_info(f"Fetching {url}", verbose)
    try:
        response = fetch(url)
        print_success(f"Fetched {len(response)} items", verbose)
        return response
    except Exception as e:
        print_error(f"Failed: {e}", verbose)
        raise
```

**Bad:**

```python
# Plain print statements - no color, no formatting
def scrape_feed(url):
    print(f"Fetching {url}")
    try:
        response = fetch(url)
        print(f"Fetched {len(response)} items")
        return response
    except Exception as e:
        print(f"ERROR: {e}")
        raise
```

### Progress Bar Patterns

**Spinner for unknown total:**

```python
from rich.progress import Progress, SpinnerColumn

with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
    task = progress.add_task("Processing...", total=None)
    while not_done():
        do_work()
    progress.update(task, completed=True)
```

**Bar for known total:**

```python
from rich.progress import Progress, BarColumn, TaskProgressColumn

with Progress(
    TextColumn("[progress.description]{task.description}"),
    BarColumn(),
    TaskProgressColumn(),
) as progress:
    task = progress.add_task("Downloading...", total=100)
    for i in range(100):
        download_chunk(i)
        progress.update(task, advance=1)
```

### Console Logging with Cache Hits

The `http_client.py` uses Rich console for cache hit logging:

```python
from rich.console import Console

console = Console()

if cached_response:
    console.log(f"[cyan]Cache hit for {request.url}[/cyan]")
    return cached_response
```

Output:
```
[12:34:56] Cache hit for https://api.example.com/data
```

### Table Formatting

```python
from rich.console import Console
from rich.table import Table

console = Console()

table = Table(title="Research Digest Summary")
table.add_column("Source", justify="left", style="cyan", no_wrap=True)
table.add_column("Items", justify="right", style="magenta")
table.add_column("Status", justify="center", style="green")

table.add_row("HackerNews", "15", "✓")
table.add_row("RSS Feeds", "23", "✓")
table.add_row("Reddit", "8", "⚠")

console.print(table)
```

Output:
```
    Research Digest Summary
┏━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━┓
┃ Source     ┃ Items ┃ Status ┃
┡━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━┩
│ HackerNews │    15 │   ✓    │
│ RSS Feeds  │    23 │   ✓    │
│ Reddit     │     8 │   ⚠    │
└────────────┴───────┴────────┘
```

### Verbose Flag Pattern

All Rich console output respects the `verbose` flag:

```python
def print_info(message: str, verbose: bool = True):
    """Print informational message if verbose is True."""
    if verbose:
        console.print(f"[blue]ℹ[/blue] {message}")
```

**Usage:**

```python
# Verbose mode (default)
scraper = HNScraper(verbose=True)
scraper.run(config, output_dir)  # Prints progress, status

# Quiet mode
scraper = HNScraper(verbose=False)
scraper.run(config, output_dir)  # No console output
```

### Color Markup Syntax

```python
from rich.console import Console

console = Console()

# Basic colors
console.print("[red]Error[/red] message")
console.print("[green]Success[/green] message")
console.print("[yellow]Warning[/yellow] message")

# Styles
console.print("[bold]Bold text[/bold]")
console.print("[italic]Italic text[/italic]")
console.print("[bold red]Bold red text[/bold red]")

# Links
console.print("[link=https://example.com]Click here[/link]")
```

### Integration with Retry Logic

Retry decorators use Rich console for retry logging:

```python
from rich_utils import print_warning

def log_retry_attempt(retry_state):
    if verbose:
        attempt = retry_state.attempt_number
        exception = retry_state.outcome.exception()
        wait_time = retry_state.next_action.sleep
        print_warning(
            f"Attempt {attempt} failed: {exception}. Retrying in {wait_time:.1f}s...",
            verbose,
        )
```

Output:
```
⚠️  Attempt 2 failed: HTTPError: 503 Server Error. Retrying in 2.0s...
```

### Performance Considerations

Rich console has minimal overhead, but for very high-frequency logging:

```python
# Bad - creates new Console() each call
def log_many_items():
    for i in range(10000):
        Console().print(f"Item {i}")  # Slow

# Good - reuse Console instance
console = Console()
def log_many_items():
    for i in range(10000):
        console.print(f"Item {i}")  # Fast
```

Or use `verbose=False` for batch operations:

```python
# Disable verbose logging for batch processing
for item in large_batch:
    process_item(item, verbose=False)
```
