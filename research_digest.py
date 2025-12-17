#!/usr/bin/env python3
"""
Research Digest - Automated research aggregation pipeline
Discovers, scrapes, and organizes research content from multiple sources.
"""

import argparse
import sys
import re
import subprocess
from pathlib import Path
from datetime import datetime
import yaml
import importlib
import pkgutil
import inspect

# Local imports
import scrapers
from scrapers.base import ScraperBase


class ResearchDigest:
    """Main orchestrator for the research digest pipeline."""

    def __init__(self, config_file: str, verbose: bool = True):
        """Initialize with config file and load scraper plugins."""
        self.verbose = verbose
        self.config = self._load_config(config_file)
        self.scrapers = self._discover_plugins()
        self.stats = {}

    def _load_config(self, config_file: str) -> dict:
        """Loads the YAML config file."""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Error loading config file '{config_file}': {e}", file=sys.stderr)
            sys.exit(1)

    def _discover_plugins(self) -> list:
        """Dynamically discovers and loads scraper plugins from the 'scrapers' package."""
        loaded_scrapers = []
        if self.verbose:
            print("🔎 Discovering scraper plugins...")

        for _, name, _ in pkgutil.iter_modules(scrapers.__path__):
            if name == 'base': continue # Skip the base class module
            
            try:
                module = importlib.import_module(f'scrapers.{name}')
                for _, obj in inspect.getmembers(module, inspect.isclass):
                    if issubclass(obj, ScraperBase) and obj is not ScraperBase:
                        loaded_scrapers.append(obj(verbose=self.verbose))
                        if self.verbose:
                            print(f"  - Found plugin: {obj.__name__}")
            except Exception as e:
                print(f"  ✗ Error loading plugin '{name}': {e}", file=sys.stderr)
        
        return loaded_scrapers

    def get_output_dir(self) -> Path:
        """Determines the output directory, creating it if it doesn't exist."""
        base_dir = Path(self.config.get('output', {}).get('base_dir', 'research_digest'))
        if self.config.get('output', {}).get('use_date_folders', True):
            date_folder = datetime.now().strftime('%Y-%m-%d')
            output_dir = base_dir / date_folder
        else:
            output_dir = base_dir
        
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir

    def run_scrapers(self, output_dir: Path):
        """Runs all discovered and enabled scraper plugins."""
        scraper_configs = self.config.get('scrapers', {})
        raw_output_dir = output_dir / 'raw'

        for scraper in self.scrapers:
            scraper_name_lower = scraper.name.lower()
            if scraper_name_lower in scraper_configs and scraper_configs[scraper_name_lower].get('enabled', False):
                scraper_config = scraper_configs[scraper_name_lower]
                try:
                    scraper.run(scraper_config, raw_output_dir)
                except Exception as e:
                    if self.verbose:
                        print(f"  ✗ Error running scraper '{scraper.name}': {e}", file=sys.stderr)
            elif self.verbose:
                print(f"  - Skipping disabled scraper: {scraper.name}")

    def run_command(self, cmd: list, description: str) -> tuple:
        """Runs an external shell command."""
        if self.verbose:
            print(description)
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            if result.returncode != 0:
                if self.verbose:
                    print(f"  ✗ Error: {result.stderr.strip()}", file=sys.stderr)
                return False, result.stderr
            return True, result.stdout
        except Exception as e:
            if self.verbose:
                print(f"  ✗ Error running command: {e}", file=sys.stderr)
            return False, str(e)

    def process_for_obsidian(self, output_dir: Path):
        """Processes all raw scraped content for Obsidian."""
        if not self.config.get('processing', {}).get('format_for_obsidian', True):
            return
        
        raw_dir = output_dir / 'raw'
        obsidian_dir = output_dir / 'obsidian'
        if not raw_dir.exists(): return

        cmd = ['./obsidian_prep.py', '-i', str(raw_dir), '-r', '-o', str(obsidian_dir)]
        if self.config.get('processing', {}).get('auto_tag', True):
            cmd.append('--auto-tag')
        
        self.run_command(cmd, "\n✨ Formatting for Obsidian...")

    def generate_report(self, output_dir: Path):
        """Generates a summary report of the digest."""
        if not self.config.get('report', {}).get('generate_summary', True):
            return

        obsidian_dir = output_dir / 'obsidian'
        if obsidian_dir.exists():
            all_files = list(obsidian_dir.rglob('*.md'))
            self.stats['HackerNews'] = sum(1 for f in all_files if 'hn_' in f.name)
            self.stats['RSS'] = sum(1 for f in all_files if 'rss_' in f.name)
            self.stats['Reddit'] = sum(1 for f in all_files if 'reddit_' in f.name)
        
        total_items = sum(self.stats.values())
        
        summary_lines = [f"- **{source}:** {count} posts" for source, count in self.stats.items() if count > 0]

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
        report_path = output_dir / 'REPORT.md'
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)

        if self.verbose:
            print("\n" + "="*60)
            print(report)
            print(f"Report saved to: {report_path}")

    def run(self):
        """Runs the complete research digest pipeline."""
        if self.verbose:
            print("🔬 Research Digest")
            print("="*60)
            print(f"Config: {self.config.get('config_path', 'research_config.yaml')}")

        output_dir = self.get_output_dir()
        if self.verbose:
            print(f"Output: {output_dir}")

        # Run scrapers
        self.run_scrapers(output_dir)

        # Process content
        self.process_for_obsidian(output_dir)
        
        # Generate final report
        self.generate_report(output_dir)

        if self.verbose:
            print("\n✅ Research digest complete!")

def main():
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(description='Automated research aggregation pipeline.')
    parser.add_argument('-c', '--config', default='research_config.yaml', help='Config file path')
    parser.add_argument('-q', '--quiet', action='store_true', help='Quiet mode, minimal output')
    args = parser.parse_args()

    # Check if config exists
    if not Path(args.config).exists():
        print(f"Error: Config file '{args.config}' not found.", file=sys.stderr)
        sys.exit(1)

    digest = ResearchDigest(args.config, verbose=not args.quiet)
    digest.run()

if __name__ == '__main__':
    main()