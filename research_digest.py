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
import json
import hashlib


class ResearchDigest:
    """Main orchestrator for research digest pipeline."""

    def __init__(self, config_file: str, verbose: bool = True):
        """Initialize with config file."""
        self.verbose = verbose
        self.config = self.load_config(config_file)
        self.stats = {
            'hackernews': 0,
            'rss': 0,
            'reddit': 0,
            'twitter': 0,
            'total': 0,
            'duplicates': 0,
        }
        self.seen_urls = set()
        self.seen_titles = set()

    def load_config(self, config_file: str) -> dict:
        """Load YAML config file."""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Error loading config: {e}", file=sys.stderr)
            sys.exit(1)

    def get_output_dir(self) -> Path:
        """Get output directory with optional date folder."""
        base_dir = Path(self.config['output']['base_dir'])

        if self.config['output']['use_date_folders']:
            date_folder = datetime.now().strftime('%Y-%m-%d')
            return base_dir / date_folder
        else:
            return base_dir

    def run_command(self, cmd: list) -> tuple:
        """
        Run a shell command and return results.

        Args:
            cmd: Command as list

        Returns:
            Tuple of (success, output)
        """
        try:
            if self.verbose:
                print(f"  Running: {' '.join(cmd[:3])}...")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes
            )

            return result.returncode == 0, result.stdout

        except subprocess.TimeoutExpired:
            print(f"  ✗ Command timed out", file=sys.stderr)
            return False, ""
        except Exception as e:
            print(f"  ✗ Error: {e}", file=sys.stderr)
            return False, ""

    def scrape_hackernews(self, output_dir: Path):
        """Scrape HackerNews based on config."""
        if not self.config.get('hackernews', {}).get('enabled', False):
            return

        if self.verbose:
            print("\n📰 HackerNews")
            print("="*60)

        hn_config = self.config['hackernews']
        hn_dir = output_dir / 'raw' / 'hackernews'

        # Search for each topic
        for topic in hn_config.get('search_topics', []):
            cmd = [
                './hn_scraper.py',
                '--search', topic,
                '--min-points', str(hn_config.get('min_points', 50)),
                '--min-comments', str(hn_config.get('min_comments', 20)),
                '--format', 'obsidian',
                '-o', str(hn_dir),
                '-q'
            ]

            success, output = self.run_command(cmd)
            if success:
                # Count files
                count = len(list(hn_dir.glob('*.md'))) if hn_dir.exists() else 0
                self.stats['hackernews'] += count

    def scrape_rss(self, output_dir: Path):
        """Scrape RSS feeds based on config."""
        feeds = self.config.get('rss_feeds', [])
        if not feeds:
            return

        if self.verbose:
            print("\n📡 RSS Feeds")
            print("="*60)

        rss_dir = output_dir / 'raw' / 'rss'
        days_back = self.config.get('days_back', 7)

        for feed in feeds:
            url = feed.get('url')
            name = feed.get('name', '')
            tags = feed.get('tags', [])

            if not url:
                continue

            cmd = [
                './rss_reader.py',
                url,
                '--name', name,
                '--days', str(days_back),
                '--format', 'obsidian',
                '-o', str(rss_dir),
                '-q'
            ]

            if tags:
                cmd.extend(['--tags'] + tags)

            success, output = self.run_command(cmd)
            if success:
                if self.verbose:
                    print(f"  ✓ {name}")

        # Count files
        if rss_dir.exists():
            count = len(list(rss_dir.glob('*.md')))
            self.stats['rss'] = count

    def scrape_reddit(self, output_dir: Path):
        """Scrape Reddit based on config."""
        if not self.config.get('reddit', {}).get('enabled', False):
            return

        if self.verbose:
            print("\n🗨️  Reddit")
            print("="*60)

        reddit_config = self.config['reddit']
        reddit_dir = output_dir / 'raw' / 'reddit'

        for sub_config in reddit_config.get('subreddits', []):
            subreddit = sub_config.get('name')
            min_upvotes = sub_config.get('min_upvotes', 50)
            tags = sub_config.get('tags', [])

            if not subreddit:
                continue

            cmd = [
                './reddit_scraper.py',
                subreddit,
                '--time', 'week',
                '--min-upvotes', str(min_upvotes),
                '--format', 'obsidian',
                '-o', str(reddit_dir),
                '-q'
            ]

            if tags:
                cmd.extend(['--tags'] + tags)

            success, output = self.run_command(cmd)
            if success:
                if self.verbose:
                    print(f"  ✓ r/{subreddit}")

        # Count files
        if reddit_dir.exists():
            count = len(list(reddit_dir.glob('*.md')))
            self.stats['reddit'] = count

    def convert_documents(self, output_dir: Path):
        """Convert PDFs and DOCX using native tools (pandoc, pdftotext)."""
        if not self.config['processing'].get('convert_documents', True):
            return

        if self.verbose:
            print("\n📄 Converting Documents (using native tools)")
            print("="*60)

        raw_dir = output_dir / 'raw'

        if not raw_dir.exists():
            return

        # Check if native tools are available
        import shutil
        if not shutil.which('pandoc') or not shutil.which('pdftotext'):
            if self.verbose:
                print("  ⚠ Skipping: pandoc or pdftotext not found")
                print("  Install with: sudo dnf install pandoc poppler-utils")
            return

        # Use native shell script for conversion
        cmd = [
            './convert_documents.sh',
            str(raw_dir),
            str(raw_dir)  # Convert in place
        ]

        success, output = self.run_command(cmd)

        if success and self.verbose:
            print(f"  ✓ Converted documents using native tools")

    def process_for_obsidian(self, output_dir: Path):
        """Process all scraped content for Obsidian."""
        if not self.config['processing'].get('format_for_obsidian', True):
            return

        if self.verbose:
            print("\n✨ Formatting for Obsidian")
            print("="*60)

        raw_dir = output_dir / 'raw'
        obsidian_dir = output_dir / 'obsidian'

        if not raw_dir.exists():
            return

        cmd = [
            './obsidian_prep.py',
            '-i', str(raw_dir),
            '-r',
            '-o', str(obsidian_dir),
        ]

        if self.config['processing'].get('auto_tag', True):
            cmd.append('--auto-tag')

        success, output = self.run_command(cmd)

        if success and self.verbose:
            print(f"  ✓ Formatted files in: {obsidian_dir}")

    def split_large_files(self, output_dir: Path):
        """Split files that exceed NotebookLM limit."""
        if not self.config['processing'].get('split_large_files', True):
            return

        if self.verbose:
            print("\n✂️  Splitting large files")
            print("="*60)

        obsidian_dir = output_dir / 'obsidian'

        if not obsidian_dir.exists():
            return

        max_size = self.config['processing'].get('max_file_size', 400000)

        cmd = [
            './file_splitter.py',
            '-i', str(obsidian_dir),
            '-r',
            '-m', str(max_size),
            '--in-place',
            '-q'
        ]

        success, output = self.run_command(cmd)

        if success and self.verbose:
            print(f"  ✓ Split files exceeding {max_size:,} characters")

    def deduplicate(self, output_dir: Path):
        """Remove duplicate content."""
        if not self.config['processing'].get('check_duplicates', True):
            return

        if self.verbose:
            print("\n🔍 Checking for duplicates")
            print("="*60)

        obsidian_dir = output_dir / 'obsidian'

        if not obsidian_dir.exists():
            return

        # Simple deduplication by title and URL
        duplicates = []

        for file_path in obsidian_dir.rglob('*.md'):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Extract title and URL from frontmatter
                title_match = re.search(r'^title:\s*(.+)$', content, re.MULTILINE)
                url_match = re.search(r'^url:\s*(.+)$', content, re.MULTILINE)

                title = title_match.group(1) if title_match else None
                url = url_match.group(1) if url_match else None

                # Check for duplicates
                is_duplicate = False

                if self.config['processing'].get('dedupe_by_url', True) and url:
                    if url in self.seen_urls:
                        is_duplicate = True
                    else:
                        self.seen_urls.add(url)

                if self.config['processing'].get('dedupe_by_title', True) and title:
                    title_hash = hashlib.md5(title.encode()).hexdigest()
                    if title_hash in self.seen_titles:
                        is_duplicate = True
                    else:
                        self.seen_titles.add(title_hash)

                if is_duplicate:
                    duplicates.append(file_path)
                    file_path.unlink()  # Delete duplicate

            except Exception as e:
                continue

        self.stats['duplicates'] = len(duplicates)

        if self.verbose:
            print(f"  ✓ Removed {len(duplicates)} duplicate(s)")

    def generate_report(self, output_dir: Path):
        """Generate summary report."""
        if not self.config.get('report', {}).get('generate_summary', True):
            return

        report = f"""# Research Digest Report
**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Output:** {output_dir}

## Summary

- **HackerNews:** {self.stats['hackernews']} posts
- **RSS Feeds:** {self.stats['rss']} articles
- **Reddit:** {self.stats['reddit']} posts
- **Duplicates Removed:** {self.stats['duplicates']}

**Total New Items:** {self.stats['hackernews'] + self.stats['rss'] + self.stats['reddit']}

## Next Steps

1. Review content in Obsidian: `{output_dir}/obsidian/`
2. Upload to NotebookLM for analysis
3. Update your notes and create connections

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
        """Run the complete digest pipeline."""
        if self.verbose:
            print("🔬 Research Digest")
            print("="*60)
            print(f"Config: research_config.yaml")
            print(f"Days back: {self.config.get('days_back', 7)}")

        # Get output directory
        output_dir = self.get_output_dir()
        output_dir.mkdir(parents=True, exist_ok=True)

        if self.verbose:
            print(f"Output: {output_dir}")

        # Run scrapers
        self.scrape_hackernews(output_dir)
        self.scrape_rss(output_dir)
        self.scrape_reddit(output_dir)

        # Process content
        self.convert_documents(output_dir)    # Convert PDFs/DOCX with native tools
        self.process_for_obsidian(output_dir)
        self.split_large_files(output_dir)
        self.deduplicate(output_dir)

        # Generate report
        self.generate_report(output_dir)

        if self.verbose:
            print("\n✅ Research digest complete!")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Automated research aggregation pipeline',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with default config
  %(prog)s

  # Use custom config
  %(prog)s -c my_config.yaml

  # Dry run (show what would be done)
  %(prog)s --dry-run

  # Quiet mode
  %(prog)s -q

This script orchestrates all the scraper tools to:
1. Discover new content from configured sources
2. Scrape and download everything
3. Organize by date in folder structure
4. Format for Obsidian with auto-tagging
5. Split large files for NotebookLM
6. Generate summary report
        """
    )

    parser.add_argument(
        '-c', '--config',
        default='research_config.yaml',
        help='Config file (default: research_config.yaml)'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without executing'
    )

    parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        help='Quiet mode'
    )

    args = parser.parse_args()

    # Check if config exists
    if not Path(args.config).exists():
        print(f"Error: Config file '{args.config}' not found", file=sys.stderr)
        print("Create one from the example: research_config.yaml", file=sys.stderr)
        sys.exit(1)

    # Check if required dependencies are installed
    try:
        import yaml
    except ImportError:
        print("Error: PyYAML required. Install with: pip install pyyaml", file=sys.stderr)
        sys.exit(1)

    # Run digest
    digest = ResearchDigest(args.config, verbose=not args.quiet)

    if args.dry_run:
        print("Dry run mode - no changes will be made")
        print(f"Would process config: {args.config}")
        print(f"Output directory: {digest.get_output_dir()}")
        return

    digest.run()


if __name__ == '__main__':
    main()
