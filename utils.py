#!/usr/bin/env python3
"""Utility functions shared across the Research Digest Toolkit."""

import re
import sys
from pathlib import Path


def generate_filename(source: str, title: str, unique_id: str) -> str:
    """Generates a sanitized, consistent filename for a piece of content.

    Args:
        source: The source of the content (e.g., 'hn', 'rss').
        title: The title of the content.
        unique_id: A unique identifier (e.g., URL or item ID).

    Returns:
        A sanitized filename string with a .md extension.
    """
    # Sanitize title
    sane_title = re.sub(r"[^\w\s-]", "", title or "untitled")
    sane_title = re.sub(r"[-\s]+", "_", sane_title)
    sane_title = sane_title[:50].strip("_").lower()

    # Sanitize ID
    sane_id = re.sub(r"[^\w-]", "", str(unique_id))
    sane_id = sane_id[-50:].strip("_")

    return f"{source}_{sane_id}_{sane_title}.md"


def save_document(filepath: Path, content: str, verbose: bool = True):
    """Saves content to a file after ensuring the directory exists.

    Args:
        filepath: The full Path object for the output file.
        content: The text content to save.
        verbose: Whether to print status messages.
    """
    try:
        # Ensure the parent directory exists
        filepath.parent.mkdir(parents=True, exist_ok=True)

        # Write the file
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        if verbose:
            print(f"    ✓ Saved: {filepath.name}")

    except IOError as e:
        if verbose:
            print(f"    ✗ Error saving file {filepath.name}: {e}", file=sys.stderr)
    except Exception as e:
        if verbose:
            print(
                f"    ✗ Unexpected error saving file {filepath.name}: {e}",
                file=sys.stderr,
            )


def clean_html(html_text: str) -> str:
    """Performs basic cleaning of HTML text.

    Removes common tags, decodes basic entities, and normalizes whitespace.

    Args:
        html_text: The input HTML string.

    Returns:
        Cleaned text.
    """
    if not html_text:
        return ""

    # Basic HTML entity decoding
    text = html_text.replace("&#x27;", "'")
    text = text.replace("&quot;", '"')
    text = text.replace("&gt;", ">")
    text = text.replace("&lt;", "<")
    text = text.replace("&amp;", "&")

    # Remove <p> tags but keep line breaks
    text = re.sub(r"</p>", "\n\n", text, flags=re.IGNORECASE)

    # Handle links by extracting their text and URL
    text = re.sub(r'<a href="([^"]+)"[^>]*>([^<]+)</a>', r"\2 [\1]", text)

    # Remove all other tags
    text = re.sub(r"<[^>]+>", "", text)

    # Clean up whitespace
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = text.strip()

    return text
