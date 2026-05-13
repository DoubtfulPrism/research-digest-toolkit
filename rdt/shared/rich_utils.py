#!/usr/bin/env python3
"""Rich utilities for consistent console output across the toolkit.

Provides shared console instances, themes, and helper functions for
formatted terminal output using the rich library.
"""

from rich.console import Console
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.table import Table
from rich.theme import Theme

# Custom theme for consistent styling
TOOLKIT_THEME = Theme(
    {
        "success": "bold green",
        "error": "bold red",
        "warning": "bold yellow",
        "info": "bold blue",
        "muted": "dim",
        "header": "bold cyan",
        "subheader": "cyan",
    }
)

# Shared console instance for stdout
console = Console(theme=TOOLKIT_THEME)

# Console for stderr (errors and warnings)
console_err = Console(stderr=True, theme=TOOLKIT_THEME)

# Console for quiet mode (suppressed output)
quiet_console = Console(quiet=True, theme=TOOLKIT_THEME)
quiet_console_err = Console(quiet=True, stderr=True, theme=TOOLKIT_THEME)


def get_console(verbose: bool = True, use_stderr: bool = False) -> Console:
    """Get the appropriate console based on verbosity setting.

    Args:
        verbose: If True, return normal console; if False, return quiet console.
        use_stderr: If True, return console that writes to stderr.

    Returns:
        Console instance.
    """
    if use_stderr:
        return console_err if verbose else quiet_console_err
    return console if verbose else quiet_console


def print_success(message: str, verbose: bool = True):
    """Print a success message with green checkmark.

    Args:
        message: The message to print.
        verbose: Whether to actually print (respects quiet mode).
    """
    c = get_console(verbose)
    c.print(f"[success]✓[/success] {message}")


def print_error(message: str, verbose: bool = True):
    """Print an error message with red X to stderr.

    Args:
        message: The message to print.
        verbose: Whether to actually print (respects quiet mode).
    """
    c = get_console(verbose, use_stderr=True)
    c.print(f"[error]✗[/error] {message}")


def print_warning(message: str, verbose: bool = True):
    """Print a warning message with yellow warning symbol to stderr.

    Args:
        message: The message to print.
        verbose: Whether to actually print (respects quiet mode).
    """
    c = get_console(verbose, use_stderr=True)
    c.print(f"[warning]⚠[/warning] {message}")


def print_info(message: str, verbose: bool = True):
    """Print an info message with blue info symbol.

    Args:
        message: The message to print.
        verbose: Whether to actually print (respects quiet mode).
    """
    c = get_console(verbose)
    c.print(f"[info]ℹ[/info] {message}")


def print_header(title: str, subtitle: str = "", verbose: bool = True):
    """Print a formatted header panel.

    Args:
        title: Main title text.
        subtitle: Optional subtitle text.
        verbose: Whether to actually print (respects quiet mode).
    """
    c = get_console(verbose)
    content = f"[header]{title}[/header]"
    if subtitle:
        content += f"\n[muted]{subtitle}[/muted]"
    c.print(Panel(content, border_style="cyan"))


def print_section(title: str, verbose: bool = True):
    """Print a section header.

    Args:
        title: Section title.
        verbose: Whether to actually print (respects quiet mode).
    """
    c = get_console(verbose)
    c.print(f"\n[subheader]{title}[/subheader]")


def create_progress_bar(verbose: bool = True) -> Progress:
    """Create a progress bar with standard configuration.

    Args:
        verbose: Whether to actually display the progress bar.

    Returns:
        Configured Progress instance.
    """
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        TimeElapsedColumn(),
        console=get_console(verbose),
        disable=not verbose,
    )


def create_summary_table(title: str, headers: list[str]) -> Table:
    """Create a formatted table for summaries.

    Args:
        title: Table title.
        headers: List of column headers.

    Returns:
        Configured Table instance.
    """
    table = Table(title=title, show_header=True, header_style="bold cyan")
    for header in headers:
        table.add_column(header)
    return table


def print_separator(verbose: bool = True):
    """Print a visual separator line.

    Args:
        verbose: Whether to actually print (respects quiet mode).
    """
    c = get_console(verbose)
    c.print("[muted]" + "─" * 60 + "[/muted]")
