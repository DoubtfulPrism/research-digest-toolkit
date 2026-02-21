## YAML Configuration Pattern

**Structured research_config.yaml for scraper configuration and research topics.**

### Configuration Structure

```yaml
# research_config.yaml
days_back: 7  # Global setting

output:
  base_dir: "research_digest"
  use_date_folders: true
  obsidian_vault: ""  # Optional

scrapers:
  # Each scraper has its own nested config
  hackernews:
    enabled: true
    min_points: 50
    min_comments: 20
    search_topics:
      - "engineering culture"
      - "platform engineering"

  rss:
    enabled: true
    days_back: 7  # Can override global setting
    feeds:
      - url: "https://example.com/feed/"
        name: "Blog Name"
        tags: ["leadership", "tech"]

  reddit:
    enabled: false
    time_filter: week
    subreddits:
      - name: "ExperiencedDevs"
        min_upvotes: 100
        tags: ["career"]

topics:
  category_name:
    - "keyword 1"
    - "keyword 2"

processing:
  convert_documents: true
  auto_tag: true
  format_for_obsidian: true
```

### When to Apply

- Configuration-driven feature toggles (`enabled: true/false`)
- Per-source settings (API keys, filters, thresholds)
- Shared topics/keywords for auto-tagging
- Output directory structure and processing options

### The Pattern

**1. Load config in main orchestrator:**

```python
import yaml
from pathlib import Path

def load_config(config_path: Path = Path("research_config.yaml")) -> dict:
    """Load YAML configuration."""
    with open(config_path) as f:
        return yaml.safe_load(f)

config = load_config()
```

**2. Access scraper-specific config:**

```python
# In plugin
def run(self, config: dict, output_dir: Path):
    # Config contains only this scraper's section
    min_points = config["min_points"]
    search_topics = config["search_topics"]
```

**3. Check enabled state before running:**

```python
# In orchestrator
for scraper_name, scraper_config in config["scrapers"].items():
    if scraper_config.get("enabled", False):
        scraper = load_plugin(scraper_name)
        scraper.run(scraper_config, output_dir)
```

### Configuration Keys

**Top-level:**
- `days_back` - Global time range (days)
- `output` - Output directory settings
- `scrapers` - Per-scraper configs (nested)
- `topics` - Keyword categories for auto-tagging
- `processing` - Output processing options

**Per-scraper (under `scrapers.{name}`):**
- `enabled` - Enable/disable scraper (boolean)
- `days_back` - Override global time range (optional)
- Source-specific settings (API keys, filters, thresholds)

### Why

- **User control** - Enable/disable scrapers without code changes
- **Centralized** - All configuration in one file
- **Type safety** - YAML provides structure validation
- **Extensible** - Add new scrapers by adding config sections

### Common Mistakes

- Hardcoding settings in scraper code instead of config - not user-configurable
- Not checking `enabled` flag - runs disabled scrapers
- Accessing `config["scrapers"]` in plugins - plugins should receive their section only
- Not providing defaults for optional keys - crashes on missing keys

### Examples

**Good:**

```python
# Main orchestrator
config = load_config()
for scraper_name, scraper_config in config["scrapers"].items():
    if scraper_config.get("enabled", False):
        plugin = load_plugin(scraper_name)
        # Pass only this scraper's config
        plugin.run(scraper_config, output_dir)
```

**Bad:**

```python
# Hardcoded in scraper
class HNScraper:
    def run(self, config, output_dir):
        min_points = 50  # Should come from config
        search_topics = ["engineering"]  # Should come from config
```

### Config Validation

```python
def validate_config(config: dict):
    """Validate required config keys."""
    required_keys = ["scrapers", "output", "processing"]
    for key in required_keys:
        if key not in config:
            raise ValueError(f"Missing required config key: {key}")

    # Validate scraper configs
    for name, scraper_config in config["scrapers"].items():
        if "enabled" not in scraper_config:
            raise ValueError(f"Scraper {name} missing 'enabled' key")
```

### Default Values

Use `.get()` with defaults for optional keys:

```python
# In plugin
def run(self, config: dict, output_dir: Path):
    min_points = config.get("min_points", 50)  # Default: 50
    days_back = config.get("days_back", 7)     # Default: 7
    verbose = config.get("verbose", True)      # Default: True
```

### Topics Auto-Tagging

The `topics` section defines keyword categories for auto-tagging content:

```yaml
topics:
  software_leadership:
    - "engineering culture"
    - "team leadership"
  productivity:
    - "productivity tools"
    - "knowledge management"
```

**Usage in obsidian_prep.py:**

```python
def auto_tag_content(content: str, topics: dict) -> list[str]:
    """Match content against topic keywords."""
    tags = []
    for category, keywords in topics.items():
        for keyword in keywords:
            if keyword.lower() in content.lower():
                tags.append(category)
                break  # One match per category
    return tags
```

### Processing Options

```yaml
processing:
  convert_documents: true   # Use pandoc/pdftotext
  auto_tag: true            # Tag content via topics
  format_for_obsidian: true # Add YAML frontmatter
  split_large_files: true   # Split at max_file_size
  max_file_size: 400000     # NotebookLM character limit
```

### Output Options

```yaml
output:
  base_dir: "research_digest"
  use_date_folders: true  # Creates YYYY-MM-DD/ subdirectories
  obsidian_vault: "/path/to/vault"  # Optional: auto-copy to vault
```

### Environment-Specific Configs

For multiple environments (dev, prod):

```bash
# Load different config
./research_digest.py --config research_config.dev.yaml
```

```python
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--config", default="research_config.yaml")
args = parser.parse_args()

config = load_config(Path(args.config))
```
