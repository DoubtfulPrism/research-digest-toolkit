#!/usr/bin/env python3
"""
Web Scraper - Extract clean text content from web pages
Scrapes web pages and saves them as clean text files suitable for NotebookLM.
"""

import requests
from bs4 import BeautifulSoup
import re
import os
import argparse
import sys


def clean_html_content(html_content):
    """
    Clean HTML content by removing unwanted elements and excess whitespace.

    Args:
        html_content: Raw HTML content

    Returns:
        Cleaned text content
    """
    soup = BeautifulSoup(html_content, 'html.parser')

    # Remove unwanted elements
    for element in soup(["script", "style", "header", "footer", "nav",
                         "aside", "form", "button", "iframe", "img"]):
        element.decompose()

    text = soup.get_text()

    # Clean up whitespace
    text = re.sub(r'\n\s*\n', '\n\n', text)
    text = re.sub(r' +', ' ', text)

    return text.strip()


def scrape_and_save(urls, output_dir="notebooklm_sources_web"):
    """
    Scrape URLs and save cleaned content to text files.

    Args:
        urls: List of URLs to scrape
        output_dir: Directory to save output files
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: '{output_dir}'")

    print(f"Saving cleaned articles to '{output_dir}' directory...")

    # Add user agent to avoid being blocked
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    success_count = 0

    for i, url in enumerate(urls):
        try:
            print(f"\nFetching [{i+1}/{len(urls)}]: {url}")
            response = requests.get(url, timeout=10, headers=headers)
            response.raise_for_status()

            clean_text = clean_html_content(response.content)

            # Extract page title for filename
            title_soup = BeautifulSoup(response.content, 'html.parser')
            page_title = title_soup.title.string if title_soup.title else f"article_{i+1}"

            # Sanitize filename (cross-platform safe)
            filename_base = re.sub(r'[\\/:*?"<>|]', '_', page_title).strip()
            filename = f"{filename_base[:50].strip() or f'article_{i+1}'}.txt"

            output_path = os.path.join(output_dir, filename)

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(clean_text)

            file_size = len(clean_text)
            print(f"  ✓ Success: Saved as '{filename}' ({file_size} chars)")
            success_count += 1

        except requests.exceptions.RequestException as e:
            print(f"  ✗ Error fetching {url}: {e}", file=sys.stderr)
        except IOError as e:
            print(f"  ✗ Error writing file for {url}: {e}", file=sys.stderr)
        except Exception as e:
            print(f"  ✗ Unexpected error with {url}: {e}", file=sys.stderr)

    print(f"\n{'='*60}")
    print(f"Completed: {success_count}/{len(urls)} articles saved successfully")
    print(f"{'='*60}")


def main():
    """Main entry point for CLI usage."""
    parser = argparse.ArgumentParser(
        description='Scrape web pages and save as clean text files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s https://example.com
  %(prog)s https://example.com https://another-site.com
  %(prog)s -o output_folder https://example.com
  %(prog)s -f urls.txt
        """
    )

    parser.add_argument(
        'urls',
        nargs='*',
        help='URLs to scrape (space-separated)'
    )

    parser.add_argument(
        '-f', '--file',
        help='Read URLs from a text file (one URL per line)'
    )

    parser.add_argument(
        '-o', '--output',
        default='notebooklm_sources_web',
        help='Output directory (default: notebooklm_sources_web)'
    )

    args = parser.parse_args()

    # Collect URLs from arguments or file
    urls = list(args.urls) if args.urls else []

    if args.file:
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                file_urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                urls.extend(file_urls)
        except IOError as e:
            print(f"Error reading file '{args.file}': {e}", file=sys.stderr)
            sys.exit(1)

    if not urls:
        parser.print_help()
        print("\nError: No URLs provided. Use URLs as arguments or specify a file with -f", file=sys.stderr)
        sys.exit(1)

    scrape_and_save(urls, args.output)


if __name__ == "__main__":
    main()
