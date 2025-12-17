#!/usr/bin/env python3
"""
Obsidian Formatter - Convert scraped content to Obsidian format
Adds YAML frontmatter, auto-tags, and creates backlinks.
"""

import argparse
import sys
import re
from pathlib import Path
from datetime import datetime
import hashlib


# Default tag mapping - keywords to tags for software leadership research
DEFAULT_TAG_MAP = {
    # Engineering Culture
    'culture': ['engineering-culture', 'team-culture'],
    'remote': ['remote-work', 'distributed-teams'],
    'onboarding': ['onboarding', 'team-building'],
    'psychological safety': ['psychological-safety', 'team-dynamics'],
    'feedback': ['feedback', 'communication'],

    # Dev Practices
    'testing': ['testing', 'quality'],
    'ci/cd': ['cicd', 'devops'],
    'code review': ['code-review', 'practices'],
    'refactoring': ['refactoring', 'technical-debt'],
    'pair programming': ['pair-programming', 'practices'],
    'tdd': ['tdd', 'testing'],

    # Innovation & Strategy
    'innovation': ['innovation', 'strategy'],
    'platform': ['platform-engineering', 'infrastructure'],
    'api': ['api-design', 'architecture'],
    'microservices': ['microservices', 'architecture'],
    'architecture': ['architecture', 'design'],

    # Productivity & Tools
    'productivity': ['productivity', 'efficiency'],
    'automation': ['automation', 'tooling'],
    'ai': ['ai', 'ml', 'automation'],
    'copilot': ['ai-assisted', 'tools'],
    'ide': ['tools', 'developer-experience'],

    # Knowledge Management
    'documentation': ['documentation', 'knowledge-management'],
    'knowledge': ['knowledge-management', 'learning'],
    'learning': ['learning', 'professional-development'],
    'onboarding': ['onboarding', 'knowledge-transfer'],

    # Team Management
    'leadership': ['leadership', 'management'],
    'hiring': ['hiring', 'recruiting'],
    'career': ['career-development', 'growth'],
    '1:1': ['one-on-ones', 'management'],
    'performance': ['performance-management', 'feedback'],

    # Process
    'agile': ['agile', 'process'],
    'scrum': ['scrum', 'agile'],
    'kanban': ['kanban', 'process'],
    'sprint': ['sprint', 'agile'],
    'retro': ['retrospective', 'process'],
}


def detect_source_type(file_path: Path, content: str) -> str:
    """
    Detect the source type of content.

    Args:
        file_path: Path to file
        content: File content

    Returns:
        Source type identifier
    """
    # Check file path
    if 'sources_web' in str(file_path):
        return 'web'
    elif 'sources_yt' in str(file_path):
        return 'youtube'
    elif 'sources_threads' in str(file_path):
        return 'twitter'
    elif 'sources_hn' in str(file_path) or file_path.name.startswith('hn_'):
        return 'hackernews'

    # Check content markers
    if 'YouTube Video Transcript' in content:
        return 'youtube'
    elif 'Twitter Thread' in content or 'type: twitter-thread' in content:
        return 'twitter'
    elif 'type: hackernews' in content or 'HN Discussion:' in content:
        return 'hackernews'

    return 'web'


def extract_existing_frontmatter(content: str) -> tuple:
    """
    Extract existing YAML frontmatter if present.

    Args:
        content: File content

    Returns:
        Tuple of (frontmatter_dict, content_without_frontmatter)
    """
    frontmatter = {}
    body = content

    if content.startswith('---\n'):
        parts = content.split('---\n', 2)
        if len(parts) >= 3:
            # Parse YAML (basic parsing)
            yaml_lines = parts[1].strip().split('\n')
            for line in yaml_lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()

                    # Handle arrays
                    if value.startswith('[') and value.endswith(']'):
                        value = [v.strip() for v in value[1:-1].split(',')]

                    frontmatter[key] = value

            body = parts[2]

    return frontmatter, body


def auto_tag_content(content: str, tag_map: dict = None, max_tags: int = 10) -> list:
    """
    Automatically tag content based on keywords.

    Args:
        content: Text content
        tag_map: Keyword to tag mapping
        max_tags: Maximum tags to return

    Returns:
        List of tags
    """
    if tag_map is None:
        tag_map = DEFAULT_TAG_MAP

    content_lower = content.lower()
    tags = set()

    # Check for keywords
    for keyword, tag_list in tag_map.items():
        if keyword.lower() in content_lower:
            tags.update(tag_list)

    # Limit number of tags
    return sorted(list(tags))[:max_tags]


def extract_title(content: str, file_path: Path) -> str:
    """
    Extract or generate a title for the content.

    Args:
        content: File content
        file_path: Path to file

    Returns:
        Title string
    """
    # Try to find markdown header
    lines = content.split('\n')
    for line in lines[:20]:  # Check first 20 lines
        if line.startswith('# '):
            return line[2:].strip()

    # Try to extract from frontmatter-like structure
    if 'title:' in content[:500]:
        match = re.search(r'title:\s*(.+)', content[:500])
        if match:
            return match.group(1).strip()

    # Use filename
    return file_path.stem.replace('_', ' ').title()


def extract_url(content: str, source_type: str) -> str:
    """
    Extract source URL from content.

    Args:
        content: File content
        source_type: Type of source

    Returns:
        URL string or empty
    """
    # Look for URL patterns based on source
    patterns = [
        r'\*\*Video URL:\*\* (https?://[^\s\n]+)',
        r'\*\*Link:\*\* (https?://[^\s\n]+)',
        r'\*\*HN Discussion:\*\* (https?://[^\s\n]+)',
        r'url:\s*(https?://[^\s\n]+)',
        r'hn_url:\s*(https?://[^\s\n]+)',
    ]

    for pattern in patterns:
        match = re.search(pattern, content)
        if match:
            return match.group(1)

    return ''


def create_frontmatter(file_path: Path, content: str, args: argparse.Namespace) -> dict:
    """
    Create YAML frontmatter for Obsidian.

    Args:
        file_path: Path to file
        content: File content
        args: Command line arguments

    Returns:
        Frontmatter dictionary
    """
    # Extract existing frontmatter
    existing_fm, body = extract_existing_frontmatter(content)

    # Detect source type
    source_type = detect_source_type(file_path, content)

    # Build frontmatter
    frontmatter = {
        'type': existing_fm.get('type', source_type),
        'created': datetime.now().strftime('%Y-%m-%d'),
        'source': existing_fm.get('source', source_type),
    }

    # Add title
    title = existing_fm.get('title', extract_title(body, file_path))
    frontmatter['title'] = title

    # Add URL if found
    url = existing_fm.get('url', extract_url(content, source_type))
    if url:
        frontmatter['url'] = url

    # Auto-tag
    if args.auto_tag:
        auto_tags = auto_tag_content(body)
        existing_tags = existing_fm.get('tags', [])

        # Merge tags
        if isinstance(existing_tags, str):
            existing_tags = [t.strip() for t in existing_tags.strip('[]').split(',')]

        all_tags = list(set(auto_tags + existing_tags + (args.tags or [])))
        frontmatter['tags'] = all_tags
    elif args.tags:
        frontmatter['tags'] = args.tags
    elif existing_fm.get('tags'):
        frontmatter['tags'] = existing_fm['tags']

    # Add custom fields
    if args.add_field:
        for field in args.add_field:
            if ':' in field:
                key, value = field.split(':', 1)
                frontmatter[key.strip()] = value.strip()

    # Preserve other existing fields
    for key, value in existing_fm.items():
        if key not in frontmatter:
            frontmatter[key] = value

    return frontmatter


def format_frontmatter(frontmatter: dict) -> str:
    """
    Format frontmatter dictionary as YAML.

    Args:
        frontmatter: Frontmatter dictionary

    Returns:
        YAML string
    """
    lines = ['---']

    for key, value in frontmatter.items():
        if isinstance(value, list):
            if value:
                # Format as array
                formatted_list = ', '.join(value)
                lines.append(f'{key}: [{formatted_list}]')
        else:
            lines.append(f'{key}: {value}')

    lines.append('---')

    return '\n'.join(lines)


def add_backlinks(content: str, backlinks: list) -> str:
    """
    Add backlinks section to content.

    Args:
        content: File content
        backlinks: List of backlink strings

    Returns:
        Content with backlinks
    """
    if not backlinks:
        return content

    backlink_section = "\n\n---\n\n## Related\n\n"
    for link in backlinks:
        # Format as Obsidian wikilink
        backlink_section += f"- [[{link}]]\n"

    return content + backlink_section


def process_file(file_path: Path, output_path: Path, args: argparse.Namespace) -> bool:
    """
    Process a single file for Obsidian.

    Args:
        file_path: Input file path
        output_path: Output file path
        args: Command line arguments

    Returns:
        True if successful
    """
    try:
        # Read file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract existing frontmatter and body
        existing_fm, body = extract_existing_frontmatter(content)

        # Create new frontmatter
        frontmatter = create_frontmatter(file_path, content, args)

        # Format frontmatter
        fm_yaml = format_frontmatter(frontmatter)

        # Combine
        new_content = fm_yaml + '\n\n' + body

        # Add backlinks if specified
        if args.backlink:
            new_content = add_backlinks(new_content, args.backlink)

        # Write output
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        return True

    except Exception as e:
        print(f"  ✗ Error processing {file_path.name}: {e}", file=sys.stderr)
        return False


def main():
    """Main entry point for CLI usage."""
    parser = argparse.ArgumentParser(
        description='Format content for Obsidian with YAML frontmatter and auto-tagging',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Single file with auto-tagging
  %(prog)s article.txt --auto-tag

  # Add custom tags
  %(prog)s thread.md --tags engineering-culture,team-dynamics

  # Batch process directory
  %(prog)s -i notebooklm_sources_web/ -o ~/Obsidian/Inbox/ --auto-tag

  # Add backlinks
  %(prog)s article.md --backlink "Platform Engineering" --backlink "DevOps"

  # Add custom frontmatter fields
  %(prog)s file.md --add-field "author:John Doe" --add-field "priority:high"

  # Process for Obsidian vault
  %(prog)s -i notebooklm_sources_*/ -r -o ~/Obsidian/Research/ --auto-tag

Auto-Tagging:
  Automatically adds tags based on content keywords for:
  - Engineering culture, remote work, team dynamics
  - Dev practices, testing, CI/CD, code review
  - Innovation, architecture, platform engineering
  - Productivity, automation, AI tools
  - Knowledge management, documentation
  - Leadership, hiring, career development
        """
    )

    parser.add_argument(
        'input',
        nargs='*',
        help='Input file(s) or directory'
    )

    parser.add_argument(
        '-i', '--input-dir',
        help='Input directory'
    )

    parser.add_argument(
        '-o', '--output',
        help='Output file or directory'
    )

    parser.add_argument(
        '--vault',
        help='Obsidian vault directory (shortcut for output)'
    )

    parser.add_argument(
        '-r', '--recursive',
        action='store_true',
        help='Process subdirectories recursively'
    )

    parser.add_argument(
        '--auto-tag',
        action='store_true',
        help='Automatically add tags based on content'
    )

    parser.add_argument(
        '--tags',
        nargs='+',
        help='Additional tags to add'
    )

    parser.add_argument(
        '--backlink',
        action='append',
        help='Add backlink (can be used multiple times)'
    )

    parser.add_argument(
        '--add-field',
        action='append',
        help='Add custom frontmatter field (format: key:value)'
    )

    parser.add_argument(
        '--in-place',
        action='store_true',
        help='Modify files in place (no output directory)'
    )

    parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        help='Quiet mode - minimal output'
    )

    args = parser.parse_args()

    verbose = not args.quiet

    # Determine input files
    input_paths = []

    if args.input_dir:
        input_dir = Path(args.input_dir)
        if not input_dir.exists():
            print(f"Error: Directory '{input_dir}' does not exist", file=sys.stderr)
            sys.exit(1)

        if args.recursive:
            input_paths = list(input_dir.rglob('*.txt')) + list(input_dir.rglob('*.md'))
        else:
            input_paths = list(input_dir.glob('*.txt')) + list(input_dir.glob('*.md'))

    elif args.input:
        for item in args.input:
            path = Path(item)
            if path.is_dir():
                if args.recursive:
                    input_paths.extend(path.rglob('*.txt'))
                    input_paths.extend(path.rglob('*.md'))
                else:
                    input_paths.extend(path.glob('*.txt'))
                    input_paths.extend(path.glob('*.md'))
            elif path.is_file():
                input_paths.append(path)

    else:
        parser.print_help()
        print("\nError: No input specified", file=sys.stderr)
        sys.exit(1)

    if not input_paths:
        print("No files found to process")
        return

    # Determine output
    output_dir = None
    if args.vault:
        output_dir = Path(args.vault)
    elif args.output:
        output_dir = Path(args.output)
    elif not args.in_place:
        output_dir = Path('obsidian_output')

    # Process files
    if verbose:
        print(f"Processing {len(input_paths)} file(s)...")
        if output_dir:
            print(f"Output directory: {output_dir}")
        if args.auto_tag:
            print("Auto-tagging enabled")
        print()

    success_count = 0

    for input_path in input_paths:
        if verbose:
            print(f"Processing: {input_path.name}")

        # Determine output path
        if args.in_place:
            output_path = input_path
        else:
            # Preserve relative structure
            if args.input_dir:
                rel_path = input_path.relative_to(args.input_dir)
            else:
                rel_path = input_path.name

            output_path = output_dir / rel_path

        # Process file
        if process_file(input_path, output_path, args):
            if verbose:
                print(f"  ✓ Saved to: {output_path}")
            success_count += 1

    # Summary
    if verbose:
        print(f"\n{'='*60}")
        print(f"Completed: {success_count}/{len(input_paths)} files processed")
        print(f"{'='*60}")


if __name__ == '__main__':
    main()
