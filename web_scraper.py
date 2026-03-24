#!/usr/bin/env python3
"""Web Scraper - Extract clean text content from web pages.

Scrapes web pages and saves them as clean text files suitable for NotebookLM.
"""

import os
import re
from typing import List, Optional

import httpx
import typer
from bs4 import BeautifulSoup
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential

from http_client import get_sync_client
from rich_utils import (
    create_progress_bar,
    create_summary_table,
    get_console,
    print_error,
    print_header,
    print_info,
    print_success,
)

app = typer.Typer(help="Scrape web pages and save as clean text files")


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception(
        lambda e: isinstance(e, (httpx.RequestError, httpx.HTTPStatusError))
    ),
    reraise=True,
)
def make_resilient_request_httpx(client: httpx.Client, url: str, **kwargs):
    """
    Makes a resilient HTTP GET request using httpx.
    """
    response = client.get(url, **kwargs)
    response.raise_for_status()
    return response


def clean_html_content(html_content):
    """Clean HTML content by removing unwanted elements and excess whitespace.

    Args:
        html_content: Raw HTML content

    Returns:
        Cleaned text content
    """
    soup = BeautifulSoup(html_content, "html.parser")

    # Remove unwanted elements
    for element in soup(
        [
            "script",
            "style",
            "header",
            "footer",
            "nav",
            "aside",
            "form",
            "button",
            "iframe",
            "img",
        ]
    ):
        element.decompose()

    text = soup.get_text()

    # Clean up whitespace
    text = re.sub(r"\n\s*\n", "\n\n", text)
    text = re.sub(r" +", " ", text)

    return text.strip()


def scrape_and_save(urls, output_dir="notebooklm_sources_web"):
    """Scrape URLs and save cleaned content to text files.

    Args:
        urls: List of URLs to scrape
        output_dir: Directory to save output files
    """
    console = get_console(True)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print_info(f"Created output directory: '{output_dir}'")

    print_header("Web Scraper", f"Saving to '{output_dir}' directory")

    # Add user agent to avoid being blocked
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    success_count = 0
    client = get_sync_client()

    with create_progress_bar() as progress:
        task = progress.add_task("[cyan]Scraping URLs...", total=len(urls))

        for i, url in enumerate(urls):
            try:
                progress.update(
                    task,
                    description=f"[cyan]Fetching [{i + 1}/{len(urls)}]: {url[:50]}...",
                )
                response = make_resilient_request_httpx(
                    client, url, timeout=10, headers=headers
                )

                clean_text = clean_html_content(response.content)

                # Extract page title for filename
                title_soup = BeautifulSoup(response.content, "html.parser")
                page_title = (
                    title_soup.title.string if title_soup.title else f"article_{i + 1}"
                )

                # Sanitize filename (cross-platform safe)
                filename_base = re.sub(r'[\\/:*?"<>|]', "_", page_title).strip()
                filename = f"{filename_base[:50].strip() or f'article_{i + 1}'}.txt"

                output_path = os.path.join(output_dir, filename)

                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(clean_text)

                file_size = len(clean_text)
                print_success(f"Saved '{filename}' ({file_size:,} chars)")
                success_count += 1

            except httpx.RequestError as e:
                print_error(f"Error fetching {url}: {e}")
            except IOError as e:
                print_error(f"Error writing file for {url}: {e}")
            except Exception as e:
                print_error(f"Unexpected error with {url}: {e}")

            progress.advance(task)

    # Create summary table
    table = create_summary_table("Scraping Results", ["Metric", "Value"])
    table.add_row("Total URLs", str(len(urls)))
    table.add_row("Successful", str(success_count), style="green")
    table.add_row(
        "Failed",
        str(len(urls) - success_count),
        style="red" if len(urls) - success_count > 0 else "",
    )

    console.print("\n")
    console.print(table)


@app.command()
def main(
    urls: Optional[List[str]] = typer.Argument(
        None,
        help="URLs to scrape (space-separated)",
    ),
    file: Optional[str] = typer.Option(
        None,
        "--file",
        "-f",
        help="Read URLs from a text file (one URL per line)",
    ),
    output: str = typer.Option(
        "notebooklm_sources_web",
        "--output",
        "-o",
        help="Output directory",
    ),
):
    """
    Scrape web pages and save as clean text files.

    Examples:

      web_scraper.py https://example.com

      web_scraper.py https://example.com https://another-site.com

      web_scraper.py -o output_folder https://example.com

      web_scraper.py -f urls.txt
    """
    # Collect URLs from arguments or file
    url_list = list(urls) if urls else []

    if file:
        try:
            with open(file, "r", encoding="utf-8") as f:
                file_urls = [
                    line.strip()
                    for line in f
                    if line.strip() and not line.startswith("#")
                ]
                url_list.extend(file_urls)
        except IOError as e:
            console = get_console(True)
            console.print(f"[error]Error reading file '{file}': {e}[/error]")
            raise typer.Exit(1)

    if not url_list:
        console = get_console(True)
        console.print(
            "[error]Error: No URLs provided. Use URLs as arguments or specify a file with -f[/error]"
        )
        raise typer.Exit(1)

    scrape_and_save(url_list, output)


if __name__ == "__main__":
    app()
