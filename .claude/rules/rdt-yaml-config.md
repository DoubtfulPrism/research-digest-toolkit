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
  hackernews:
    enabled: true
    min_points: 50
    min_comments: 20
    search_topics: ["engineering culture", "platform engineering"]
  rss:
    enabled: true
    feeds:
      - url: "https://example.com/feed/"
        name: "Blog Name"
        tags: ["leadership"]
  reddit:
    enabled: false
    time_filter: week
    subreddits:
      - name: "ExperiencedDevs"
        min_upvotes: 100

topics:
  category_name: ["keyword 1", "keyword 2"]

processing:
  convert_documents: true
  auto_tag: true
  format_for_obsidian: true
  split_large_files: true
  max_file_size: 400000  # NotebookLM char limit
```

### The Pattern

**Load config:**
```python
import yaml
from pathlib import Path

def load_config(config_path: Path = Path("research_config.yaml")) -> dict:
    with open(config_path) as f:
        return yaml.safe_load(f)
```

**Plugins receive only their section:**
```python
# In orchestrator — pass scraper-specific config
for name, scraper_config in config["scrapers"].items():
    if scraper_config.get("enabled", False):
        plugin = load_plugin(name)
        plugin.run(scraper_config, output_dir)  # NOT config["scrapers"]

# In plugin — use .get() with defaults
def run(self, config: dict, output_dir: Path):
    min_points = config.get("min_points", 50)
    days_back = config.get("days_back", 7)
```

### Configuration Keys

**Top-level:** `days_back`, `output`, `scrapers`, `topics`, `processing`

**Per-scraper:** `enabled` (required), `days_back` (optional override), source-specific settings

### Config Validation

```python
def validate_config(config: dict):
    required_keys = ["scrapers", "output", "processing"]
    for key in required_keys:
        if key not in config:
            raise ValueError(f"Missing required config key: {key}")
    for name, sc in config["scrapers"].items():
        if "enabled" not in sc:
            raise ValueError(f"Scraper {name} missing 'enabled' key")
```

### Pydantic Models

`config_models.py` provides validated Pydantic models for the config structure, used by the TUI and service layers.

### Common Mistakes

- Hardcoding settings in scraper code — not user-configurable
- Not checking `enabled` flag — runs disabled scrapers
- Accessing `config["scrapers"]` in plugins — plugins should receive their section only
- Not providing defaults for optional keys — crashes on missing keys
