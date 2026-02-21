#!/usr/bin/env python3
"""Research Digest - Automated research aggregation pipeline.

Discovers, scrapes, and organizes research content from multiple sources.
"""

import argparse
import importlib
import inspect
import pkgutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import yaml

# Local imports
import scrapers
import typer
from pydantic import ValidationError
import signal

from config_models import ResearchDigestConfig
from scheduler_utils import setup_schedule, run_scheduler, SignalHandler, ScheduleError
from rich_utils import (
    create_summary_table,
    get_console,
    print_error,
    print_header,
    print_info,
    print_section,
    print_success,
)
from scrapers.base import ScraperBase

app = typer.Typer(help="Automated research aggregation pipeline.")


class ResearchDigest:
    """Main orchestrator for the research digest pipeline."""

    def __init__(self, config_file: str, verbose: bool = True):
        """Initialize with config file and load scraper plugins."""
        self.verbose = verbose
        self.config = self._load_config(config_file)
        self.scrapers = self._discover_plugins()
        self.stats = {}

    def _load_config(self, config_file: str) -> ResearchDigestConfig:
        """Loads the YAML config file and validates it with Pydantic."""
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                config_data = yaml.safe_load(f)
            config = ResearchDigestConfig(**config_data)
            config.config_path = config_file
            return config
        except ValidationError as e:
            console = get_console(self.verbose)
            console.print(f"[error]Configuration error in '{config_file}':[/error]")
            for error in e.errors():
                loc = " -> ".join(map(str, error["loc"]))
                console.print(f"  - [b]{loc}[/b]: {error['msg']}")
            sys.exit(1)
        except Exception as e:
            console = get_console(self.verbose)
            console.print(
                f"[error]Error loading config file '{config_file}': {e}[/error]"
            )
            sys.exit(1)

    def _discover_plugins(self) -> list:
        """Dynamically discovers and loads scraper plugins from the 'scrapers' package."""
        loaded_scrapers = []
        print_section("🔎 Discovering scraper plugins", self.verbose)

        for _, name, _ in pkgutil.iter_modules(scrapers.__path__):
            if name == "base":
                continue  # Skip the base class module

            try:
                module = importlib.import_module(f"scrapers.{name}")
                for _, obj in inspect.getmembers(module, inspect.isclass):
                    if issubclass(obj, ScraperBase) and obj is not ScraperBase:
                        loaded_scrapers.append(obj(verbose=self.verbose))
                        print_info(f"Found plugin: {obj.__name__}", self.verbose)
            except Exception as e:
                print_error(f"Error loading plugin '{name}': {e}", self.verbose)

        return loaded_scrapers

    def get_output_dir(self) -> Path:
        """Determines the output directory, creating it if it doesn't exist."""
        base_dir = Path(self.config.output.base_dir)
        if self.config.output.use_date_folders:
            date_folder = datetime.now().strftime("%Y-%m-%d")
            output_dir = base_dir / date_folder
        else:
            output_dir = base_dir

        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir

    def run_scrapers(self, output_dir: Path):
        """Runs all discovered and enabled scraper plugins."""
        scraper_configs = self.config.scrapers
        raw_output_dir = output_dir / "raw"

        for scraper in self.scrapers:
            scraper_name_lower = scraper.name.lower()
            if hasattr(scraper_configs, scraper_name_lower):
                scraper_config = getattr(scraper_configs, scraper_name_lower)
                # Handle both Pydantic models and dicts (for extra fields)
                is_enabled = (
                    scraper_config.enabled
                    if hasattr(scraper_config, "enabled")
                    else scraper_config.get("enabled", False)
                )
                if is_enabled:
                    try:
                        scraper.run(scraper_config, raw_output_dir)
                    except Exception as e:
                        print_error(f"Error running scraper '{scraper.name}': {e}", self.verbose)
                else:
                    print_info(f"Skipping disabled scraper: {scraper.name}", self.verbose)
            else:
                print_info(f"Skipping scraper with no config: {scraper.name}", self.verbose)


    def run_command(self, cmd: list, description: str) -> tuple:
        """Runs an external shell command."""
        print_info(description, self.verbose)
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            if result.returncode != 0:
                print_error(f"Error: {result.stderr.strip()}", self.verbose)
                return False, result.stderr
            return True, result.stdout
        except Exception as e:
            print_error(f"Error running command: {e}", self.verbose)
            return False, str(e)

    def process_for_obsidian(self, output_dir: Path):
        """Processes all raw scraped content for Obsidian."""
        if not self.config.processing.format_for_obsidian:
            return

        raw_dir = output_dir / "raw"
        obsidian_dir = output_dir / "obsidian"
        if not raw_dir.exists():
            return

        cmd = ["./obsidian_prep.py", "-i", str(raw_dir), "-r", "-o", str(obsidian_dir)]
        if self.config.processing.auto_tag:
            cmd.append("--auto-tag")

        self.run_command(cmd, "\n✨ Formatting for Obsidian...")

    def generate_report(self, output_dir: Path):
        """Generates a summary report of the digest."""
        if not self.config.report.generate_summary:
            return

        obsidian_dir = output_dir / "obsidian"
        if obsidian_dir.exists():
            all_files = list(obsidian_dir.rglob("*.md"))
            self.stats["HackerNews"] = sum(1 for f in all_files if "hn_" in f.name)
            self.stats["RSS"] = sum(1 for f in all_files if "rss_" in f.name)
            self.stats["Reddit"] = sum(1 for f in all_files if "reddit_" in f.name)

        total_items = sum(self.stats.values())

        summary_lines = [
            f"- **{source}:** {count} posts"
            for source, count in self.stats.items()
            if count > 0
        ]

        report = f"""# Research Digest Report
**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Output:** {output_dir}

## Summary of New Items
{chr(10).join(summary_lines)}

**Total New Items:** {total_items}

*Note: Deduplication is handled at the source via a persistent database. Counts reflect new items found during this run.*

## Next Steps
1. Review content in Obsidian: `{output_dir}/obsidian/`
2. Upload to NotebookLM for analysis.
---
Generated by Research Digest
"""
        report_path = output_dir / "REPORT.md"
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report)

        if self.verbose:
            console = get_console(self.verbose)
            console.print("\n[muted]" + "=" * 60 + "[/muted]")
            console.print(report)
            print_success(f"Report saved to: {report_path}", self.verbose)

    def run(self):
        """Runs the complete research digest pipeline."""
        print_header(
            "🔬 Research Digest",
            f"Config: {self.config.config_path}",
            self.verbose,
        )

        output_dir = self.get_output_dir()
        print_info(f"Output: {output_dir}", self.verbose)

        # Run scrapers
        self.run_scrapers(output_dir)

        # Process content
        self.process_for_obsidian(output_dir)

        # Generate final report
        self.generate_report(output_dir)

        print_success("Research digest complete!", self.verbose)


@app.command()
def main(
    config: str = typer.Option(
        "research_config.yaml",
        "--config",
        "-c",
        help="Config file path",
    ),
    quiet: bool = typer.Option(
        False,
        "--quiet",
        "-q",
        help="Quiet mode, minimal output",
    ),
    schedule_str: str = typer.Option(
        None,
        "--schedule",
        "-s",
        help="Run the digest on a schedule (e.g., 'every 4 hours', 'every day at 10:30').",
    ),
    run_once: bool = typer.Option(
        False,
        "--run-once",
        help="Run the digest once and then exit. This is the default behavior if --schedule is not provided.",
    ),
):
    """Run the automated research aggregation pipeline."""
    # Check if config exists
    if not Path(config).exists():
        console = get_console(True)
        console.print(f"[error]Error: Config file '{config}' not found.[/error]")
        raise typer.Exit(1)

    digest = ResearchDigest(config, verbose=not quiet)

    if schedule_str:
        print_info(f"Scheduling digest to run {schedule_str}...", verbose=not quiet)
        try:
            # Use secure scheduler instead of eval
            setup_schedule(schedule_str, digest.run)
        except ScheduleError as e:
            print_error(f"Invalid schedule string: {e}", verbose=True)
            raise typer.Exit(1)

        # Set up signal handler for graceful shutdown
        signal_handler = SignalHandler()
        signal.signal(signal.SIGINT, signal_handler.handle_signal)
        signal.signal(signal.SIGTERM, signal_handler.handle_signal)

        run_scheduler(signal_handler)
    else:
        digest.run()


if __name__ == "__main__":
    app()
