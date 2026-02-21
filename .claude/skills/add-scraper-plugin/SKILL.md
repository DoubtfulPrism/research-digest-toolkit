---
name: add-scraper-plugin
description: |
  Add a new scraper plugin to the Research Digest Toolkit. Use when: (1) user wants to add a new research source (Mastodon, Google Scholar, etc.), (2) extending the toolkit with custom data sources, (3) integrating new APIs or feeds. Key steps: create scraper class inheriting from ScraperBase, add YAML config section, test integration.
author: Claude Code
version: 1.0.0
---

# Add Scraper Plugin to Research Digest Toolkit

## Problem

Need to add a new research source (API, feed, or scraper) to the Research Digest Toolkit without modifying the core orchestrator.

## Context / Trigger Conditions

Use this skill when:
- User asks to add support for a new source (e.g., "Add Mastodon support", "Scrape Google Scholar")
- Need to integrate a new API or RSS-like feed
- Want to extend the toolkit with custom data collection

## Solution

### Step 1: Create Scraper File

Create `scrapers/{source}_scraper.py` (e.g., `scrapers/mastodon_scraper.py`):

```python
#!/usr/bin/env python3
"""Scraper for [Source Name]."""

from pathlib import Path
from scrapers.base import ScraperBase
from retry_utils import retry_api_call
from rich_utils import print_info, print_success, print_error

class [Source]Scraper(ScraperBase):
    """Scraper for [Source Name]."""

    def __init__(self, verbose: bool = True):
        super().__init__(verbose)  # CRITICAL: Call parent __init__
        self.name = "[Source]"

    def run(self, config: dict, output_dir: Path):
        """Main scraper logic.

        Args:
            config: Scraper-specific config from YAML (scrapers.{source} section)
            output_dir: Base output directory (e.g., research_digest/2026-02-21/raw/)
        """
        # Check if enabled (safety check, orchestrator should handle this)
        if not config.get("enabled", False):
            print_info(f"{self.name} scraper is disabled", self.verbose)
            return

        # Create output subdirectory
        source_dir = output_dir / self.name.lower()
        source_dir.mkdir(parents=True, exist_ok=True)

        # Access config values with defaults
        api_key = config.get("api_key", "")
        search_query = config.get("search_query", "")
        max_results = config.get("max_results", 10)

        print_info(f"Running {self.name} scraper...", self.verbose)

        try:
            # Implement scraping logic here
            # Use retry_api_call decorator for API calls
            items = self._fetch_items(api_key, search_query, max_results)

            # Save each item
            for item in items:
                filename = source_dir / f"{item['id']}.md"
                with open(filename, "w") as f:
                    f.write(item["content"])

            print_success(f"Scraped {len(items)} items from {self.name}", self.verbose)

        except Exception as e:
            print_error(f"{self.name} scraper failed: {e}", self.verbose)
            raise

    @retry_api_call(verbose=True)
    def _fetch_items(self, api_key: str, query: str, max_results: int):
        """Fetch items from API with retry logic."""
        # Implement API call here
        # response.raise_for_status() triggers retry on 5xx/429
        pass
```

### Step 2: Add YAML Configuration

Add config section to `research_config.yaml` under `scrapers`:

```yaml
scrapers:
  # ... existing scrapers ...

  [source]:
    enabled: true              # Toggle scraper on/off
    api_key: "your_key_here"   # Source-specific settings
    search_query: "python"
    max_results: 20
    days_back: 7               # Optional: override global days_back
```

### Step 3: Test the Integration

```bash
# 1. Enable only your new scraper for testing
# Edit research_config.yaml: set other scrapers to enabled: false

# 2. Run the digest
./research_digest.py

# 3. Verify output
ls research_digest/$(date +%Y-%m-%d)/raw/[source]/

# 4. Check for errors in console output
```

### Step 4: Handle Common Edge Cases

**Deduplication:**
```python
from database import Database

# In run() method
db = Database("research_digest_state.db")
for item in items:
    if db.is_new_item(item["url"], item["title"]):
        # Save item
        db.add_item(item["url"], item["title"])
```

**Rate limiting:**
```python
from retry_utils import retry_api_call
import time

@retry_api_call(verbose=True)  # Handles 429 with exponential backoff
def _fetch_items(self, ...):
    response = requests.get(url)
    response.raise_for_status()
    return response.json()
```

**Pagination:**
```python
def _fetch_all_pages(self, base_url, max_results):
    """Fetch multiple pages until max_results reached."""
    all_items = []
    page = 1
    while len(all_items) < max_results:
        items = self._fetch_page(base_url, page)
        if not items:
            break
        all_items.extend(items)
        page += 1
    return all_items[:max_results]
```

## Verification

1. **Plugin discovered:**
   ```bash
   ./research_digest.py
   # Should see: "Found plugin: [Source]Scraper"
   ```

2. **Output created:**
   ```bash
   ls research_digest/$(date +%Y-%m-%d)/raw/[source]/
   # Should contain scraped files
   ```

3. **No errors in console**

4. **Test with disabled:**
   ```yaml
   # research_config.yaml
   scrapers:
     [source]:
       enabled: false
   ```
   Run `./research_digest.py` - should skip your scraper

## Common Gotchas

1. **Forgot `super().__init__(verbose)`** → Scraper won't have `self.name` or `self.verbose`
2. **Not checking `enabled` flag** → Runs even when disabled
3. **Accessing `config["scrapers"]` in plugin** → Should receive only `config["scrapers"]["source"]` from orchestrator
4. **No retry logic on API calls** → Fails on transient network errors
5. **Not calling `response.raise_for_status()`** → HTTP errors don't trigger retries
6. **Hardcoding output paths** → Use `output_dir` parameter instead

## File Naming Convention

- **File:** `scrapers/{source}_scraper.py` (lowercase, underscore-separated)
- **Class:** `{Source}Scraper` (PascalCase, ends with "Scraper")
- **YAML key:** `{source}` (lowercase, matches filename prefix)

Examples:
- `scrapers/google_scholar_scraper.py` → `GoogleScholarScraper` → `google_scholar:`
- `scrapers/mastodon_scraper.py` → `MastodonScraper` → `mastodon:`

## Example: Minimal Scraper

```python
#!/usr/bin/env python3
"""Scraper for Example API."""

from pathlib import Path
import requests
from scrapers.base import ScraperBase
from retry_utils import retry_api_call
from rich_utils import print_info, print_success

class ExampleScraper(ScraperBase):
    def __init__(self, verbose: bool = True):
        super().__init__(verbose)
        self.name = "Example"

    def run(self, config: dict, output_dir: Path):
        print_info("Running Example scraper...", self.verbose)

        items = self._fetch_items(config["api_key"])

        source_dir = output_dir / "example"
        source_dir.mkdir(parents=True, exist_ok=True)

        for item in items:
            (source_dir / f"{item['id']}.md").write_text(item["text"])

        print_success(f"Scraped {len(items)} items", self.verbose)

    @retry_api_call(verbose=True)
    def _fetch_items(self, api_key: str):
        url = f"https://api.example.com/data?key={api_key}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()["items"]
```

## References

- **Plugin architecture:** `.claude/rules/plugin-architecture.md`
- **Retry pattern:** `.claude/rules/retry-resilience.md`
- **YAML config:** `.claude/rules/yaml-config.md`
- **Base class:** `scrapers/base.py`
- **Example scrapers:** `scrapers/hn_scraper.py`, `scrapers/rss_scraper.py`
