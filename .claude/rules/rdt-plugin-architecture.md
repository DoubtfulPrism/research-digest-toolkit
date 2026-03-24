## Plugin Architecture Pattern

**Dynamic scraper plugin loading for extensible research sources.**

### When to Apply

- Adding a new research source (Mastodon, Google Scholar, etc.)
- Creating reusable components that share a common interface
- Need configuration-driven enable/disable of features

### The Pattern

**1. Define the base class:**

```python
# scrapers/base.py
class ScraperBase:
    def __init__(self, verbose: bool = True):
        self.name = "Base"
        self.verbose = verbose

    def run(self, config: dict, output_dir: Path):
        raise NotImplementedError("Implement 'run' method in subclass")
```

**2. Implement plugins:**

```python
# scrapers/my_source_scraper.py
from scrapers.base import ScraperBase

class MySourceScraper(ScraperBase):
    def __init__(self, verbose: bool = True):
        super().__init__(verbose)
        self.name = "MySource"

    def run(self, config: dict, output_dir: Path):
        # Access config: config["my_source"]["api_key"]
        # Save to: output_dir / "filename.md"
        pass
```

**3. Configure in YAML:**

```yaml
# research_config.yaml
scrapers:
  my_source:
    enabled: true
    api_key: "..."
    # Source-specific config
```

**4. Load dynamically:**

```python
# Main orchestrator
import importlib
from pathlib import Path

scraper_dir = Path("scrapers")
for file in scraper_dir.glob("*_scraper.py"):
    module = importlib.import_module(f"scrapers.{file.stem}")
    # Find ScraperBase subclass, instantiate, check config enabled
```

### Why

- **Zero coupling** - Main orchestrator doesn't know about specific scrapers
- **Easy additions** - Drop new file in `scrapers/`, add config section
- **User control** - Enable/disable sources via YAML without code changes

### Common Mistakes

- Importing scrapers directly instead of dynamic loading - couples main to all plugins
- Not checking `enabled` flag - runs disabled scrapers
- Plugin-specific logic in orchestrator - defeats purpose of plugin architecture

### Examples

**Good:**

```python
# research_digest.py
scrapers = discover_plugins("scrapers/")  # Dynamic
for scraper in scrapers:
    if config["scrapers"][scraper.name.lower()]["enabled"]:
        scraper.run(config["scrapers"][scraper.name.lower()], output_dir)
```

**Bad:**

```python
# research_digest.py
from scrapers.hn_scraper import HNScraper  # Static import
from scrapers.reddit_scraper import RedditScraper
# ... manual instantiation, not extensible
```

### File Naming Convention

- Base class: `base.py`
- Plugins: `{source}_scraper.py` (e.g., `arxiv_scraper.py`, `hn_scraper.py`)
- Class name: `{Source}Scraper` (e.g., `ArxivScraper`, `HNScraper`)
