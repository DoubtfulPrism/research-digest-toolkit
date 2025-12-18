# Research Digest Automation Guide

Complete guide to setting up automated research aggregation for software leadership, innovation, and higher education research.

---

## 🎯 What This Does

**Automated Research Digest** discovers, scrapes, and organizes research content from multiple sources with a single command:

```bash
./research_digest.py
```

**Output:**
```
research_digest/
└── 2024-12-17/
    ├── raw/                   # Original scraped content
    │   ├── hackernews/
    │   ├── rss/
    │   └── reddit/
    ├── obsidian/              # Formatted for Obsidian + NotebookLM
    │   └── *.md
    └── REPORT.md              # Summary of what was found
```

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install --user -r requirements.txt
```

### 2. Configure Your Topics

Edit `research_config.yaml`:

```yaml
# Research topics
topics:
  software_leadership:
    - "engineering culture"
    - "platform engineering"

  edtech:
    - "educational technology"
    - "online learning"

# Add your favorite RSS feeds
rss_feeds:
  - url: "https://lethain.com/feeds/"
    name: "Will Larson"
    tags: ["leadership"]
```

### 3. Run It

```bash
./research_digest.py
```

### 4. Review Results

```bash
# Check the report
cat research_digest/2024-12-17/REPORT.md

# Open in Obsidian
cp -r research_digest/2024-12-17/obsidian/* ~/Documents/Obsidian/Research/

# Upload to NotebookLM
# All files in obsidian/ folder are ready!
```

---

## ⚙️ Configuration Guide

### research_config.yaml Structure

The `research_config.yaml` file is the control center for the digest. Here is the new structure:

```yaml
# How many days back to search (can be overridden by scrapers)
days_back: 7

# Output settings
output:
  base_dir: "research_digest"
  use_date_folders: true
  obsidian_vault: "" # Optional: auto-copy to vault

# Scraper configurations
scrapers:
  # HackerNews settings
  hackernews:
    enabled: true
    min_points: 50
    min_comments: 20
    search_topics:
      - "engineering culture"
      - "platform engineering"
      - "developer productivity"

  # RSS Feeds to monitor
  rss:
    enabled: true
    days_back: 7 # Specific override for this scraper
    feeds:
      - url: "https://lethain.com/feeds/"
        name: "Will Larson"
        tags: ["leadership", "engineering-culture"]
      - url: "https://charity.wtf/feed/"
        name: "Charity Majors"
        tags: ["leadership", "observability"]

  # Reddit subreddits to monitor
  reddit:
    enabled: true
    time_filter: week # hour, day, week, month, year, all
    subreddits:
      - name: "ExperiencedDevs"
        min_upvotes: 100
        tags: ["career", "leadership"]
      - name: "ObsidianMD"
        min_upvotes: 50
        tags: ["knowledge-management"]

# Research topics (used for auto-tagging)
topics:
  software_leadership:
    - "engineering culture"
    - "team dynamics"
    - "platform engineering"

# Processing options
processing:
  auto_tag: true
  format_for_obsidian: true
  split_large_files: true
```

### Finding Good RSS Feeds
(This section remains the same)


---

## 🤖 Automation Options

### Option 1: Weekly Cron Job (Recommended)

Run every Monday morning at 9 AM:

```bash
# Edit crontab
crontab -e

# Add this line:
0 9 * * 1 cd /home/doug/Documents/AIProjectWork/Scripts && ./research_digest.py >> logs/digest.log 2>&1
```

**Create logs directory:**
```bash
mkdir -p /home/doug/Documents/AIProjectWork/Scripts/logs
```

### Option 2: Daily Digest

Run every day at 8 AM:

```bash
0 8 * * * cd /home/doug/Documents/AIProjectWork/Scripts && ./research_digest.py -q
```

### Option 3: Monthly Deep Dive

First Monday of every month:

```bash
# Edit config to set days_back: 30

0 9 1-7 * 1 cd /home/doug/Documents/AIProjectWork/Scripts && ./research_digest.py
```

### Option 4: Systemd Timer (Advanced)

Create `~/.config/systemd/user/research-digest.service`:

```ini
[Unit]
Description=Research Digest Aggregation
After=network.target

[Service]
Type=oneshot
WorkingDirectory=/home/doug/Documents/AIProjectWork/Scripts
ExecStart=/home/doug/Documents/AIProjectWork/Scripts/research_digest.py
StandardOutput=journal
StandardError=journal
```

Create `~/.config/systemd/user/research-digest.timer`:

```ini
[Unit]
Description=Run Research Digest Weekly

[Timer]
OnCalendar=Mon *-*-* 09:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

**Enable:**
```bash
systemctl --user enable research-digest.timer
systemctl --user start research-digest.timer

# Check status
systemctl --user list-timers
```

---

## 📋 Workflow Examples

### Weekly Research Workflow

**Monday Morning:**
```bash
# Automatic cron job runs at 9 AM
# Or run manually:
./research_digest.py

# Check what was found
cat research_digest/$(date +%Y-%m-%d)/REPORT.md

# Review in Obsidian
cp -r research_digest/$(date +%Y-%m-%d)/obsidian/* ~/Documents/Obsidian/Inbox/
```

**Throughout Week:**
- Bookmark interesting Twitter threads
- Add URLs to `research_urls.txt`
- Note good YouTube talks

**Friday Afternoon:**
```bash
# Process bookmarked threads
./thread_reader.py -f bookmarked_threads.txt --format obsidian \
  -o research_digest/$(date +%Y-%m-%d)/obsidian/

# Scrape any manual URLs
./web_scraper.py -f research_urls.txt

# Process everything
./obsidian_prep.py -i research_digest/$(date +%Y-%m-%d)/ -r --auto-tag --in-place
```

### Monthly Deep Dive

```bash
# Update config: days_back: 30

./research_digest.py

# Analyze specific topic
cd research_digest/$(date +%Y-%m-%d)/obsidian/
grep -l "platform-engineering" *.md | xargs cat > ~/platform_engineering_digest.md

# Upload to NotebookLM
# Ask: "What are the emerging trends in platform engineering?"
```

### Topic-Specific Research

Create a custom config for specific projects:

**platform_engineering_config.yaml:**
```yaml
days_back: 14

hackernews:
  enabled: true
  search_topics:
    - "platform engineering"
    - "internal developer platform"
    - "developer experience"

reddit:
  enabled: true
  subreddits:
    - name: "devops"
      min_upvotes: 100
```

```bash
./research_digest.py -c platform_engineering_config.yaml
```

---

## 🎨 Customization

### Adding New Scraper Plugins

Thanks to the new plugin architecture, adding a new source is straightforward. You don't need to modify the main `research_digest.py` script.

**1. Create a New Plugin File:**
Create a new Python file in the `scrapers/` directory (e.g., `scrapers/arxiv_scraper.py`).

**2. Build Your Scraper Class:**
Your scraper must inherit from `ScraperBase` and implement a `run` method.

```python
# in scrapers/arxiv_scraper.py
from .base import ScraperBase
from pathlib import Path
import utils
import database

class ArxivScraper(ScraperBase):
    def __init__(self, verbose=True):
        super().__init__(verbose)
        self.name = "Arxiv" # The name used in the config file

    def run(self, config: dict, output_dir: Path):
        if self.verbose:
            print("🔬 Scraping Arxiv...")

        # Your scraping logic here...
        # - Read from config
        # - Fetch data
        # - Check database.item_exists()
        # - Save with utils.save_document()
        # - Add to DB with database.add_item()
```

**3. Configure Your New Scraper:**
Add a section for your new scraper in `research_config.yaml`. The key (`arxiv` in this case) should match the `name` attribute of your class, converted to lowercase.

```yaml
# In research_config.yaml
scrapers:
  arxiv:
    enabled: true
    search_query: "large language models"
    max_results: 10
  # ... other scrapers
```

The digest will automatically discover and run your new plugin.

### Custom Tag Mappings

Edit `obsidian_prep.py` to customize auto-tagging for your specific research areas.

### Integration with Obsidian Vault

Auto-copy to your vault:

```yaml
output:
  obsidian_vault: "/home/doug/Documents/Obsidian/Research"
```

Or create a symlink:
```bash
ln -s /home/doug/Documents/AIProjectWork/Scripts/research_digest \
      /home/doug/Documents/Obsidian/ResearchDigest
```

---

## 📊 Reports & Monitoring

### Daily Report Email (Optional)

Install `mail` utility:
```bash
sudo dnf install mailx
```

Add to cron:
```bash
0 9 * * 1 cd /home/doug/Documents/AIProjectWork/Scripts && ./research_digest.py && mail -s "Weekly Research Digest" your@email.com < research_digest/$(date +%Y-%m-%d)/REPORT.md
```

### Slack/Discord Notifications

Create a wrapper script `run_digest_with_notify.sh`:

```bash
#!/bin/bash

cd /home/doug/Documents/AIProjectWork/Scripts

# Run digest
./research_digest.py

# Send notification to Slack
DATE=$(date +%Y-%m-%d)
REPORT=$(cat research_digest/$DATE/REPORT.md)

curl -X POST -H 'Content-type: application/json' \
  --data "{\"text\":\"$REPORT\"}" \
  YOUR_SLACK_WEBHOOK_URL
```

### Track Over Time

```bash
# See trends
find research_digest/ -name "REPORT.md" -exec cat {} \;

# Count total items per week
for dir in research_digest/*/; do
  echo "$dir: $(find $dir/obsidian -name '*.md' | wc -l) items"
done
```

---

## 🔧 Troubleshooting

### "Config file not found"

```bash
# Make sure you're in the Scripts directory
cd /home/doug/Documents/AIProjectWork/Scripts

# Or specify full path
./research_digest.py -c /full/path/to/research_config.yaml
```

### "No items found"

Check your config:
- Are the search terms too specific?
- Try lowering `min_points` and `min_upvotes`
- Check if RSS feeds are still active
- Increase `days_back` to 14 or 30

### RSS Feed Errors

If you suspect an RSS feed is broken, you can test it by navigating to the URL in your browser.

### Rate Limiting

If you hit rate limits from sources like Reddit or HackerNews:
- The scrapers have a default 1-second delay between requests.
- If issues persist, consider running the digest less frequently or reducing the number of search topics/subreddits.

---

## 💡 Pro Tips

1. **Start Small**: Enable one source at a time, test, then add more

2. **Curate Your Feeds**: Quality over quantity - 5 great blogs > 50 mediocre ones

3. **Review Weekly**: Don't let content pile up - process and organize weekly

4. **Tag Consistently**: Use the auto-tagging feature, then refine tags manually

5. **Create MOCs**: In Obsidian, create Maps of Content for each major topic

6. **Batch to NotebookLM**: Upload all obsidian/*.md files for a topic, ask synthesis questions

7. **Archive Old Digests**: Move old date folders to an archive after processing

8. **Backup Config**: Your `research_config.yaml` is valuable - keep it in git

9. **Use Dry Run**: Test changes with `--dry-run` flag first

10. **Monitor Logs**: Check cron logs regularly to catch issues early

---

## 🎓 Academic Research Workflow

Inspired by the Obsidian academic workflow from Reddit.

### Setup for Literature Review

```yaml
# research_config.yaml for academic research

rss_feeds:
  # Your field's top journals
  - url: "https://journal-feed-url.com/rss"
    name: "Top Journal"
    tags: ["literature-review"]

reddit:
  subreddits:
    - name: "AskAcademia"
    - name: "GradSchool"
    - name: "PhD"
```

### Monthly Workflow

```bash
# Run digest
./research_digest.py

# Import to Obsidian
cp -r research_digest/$(date +%Y-%m-%d)/obsidian/* \
      ~/Documents/Obsidian/Literature/

# In Obsidian:
# - Review auto-tags
# - Add to literature notes
# - Create connections
# - Update bibliography

# For systematic review:
# Upload all to NotebookLM and ask:
# "What are the main themes in this literature?"
# "What methodologies are being used?"
# "What gaps exist in current research?"
```

---

## 📚 Next Steps

1. **Customize `research_config.yaml`** for your topics
2. **Run once manually** to test
3. **Review the output** in `research_digest/YYYY-MM-DD/`
4. **Set up automation** (cron or systemd)
5. **Integrate with Obsidian** workflow
6. **Refine over time** based on what you find useful

---

## 🆘 Getting Help

- Check individual tool docs: `./tool_name.py --help`
- Review examples in this guide
- Test components separately before automation
- Start with `--dry-run` flag

**Remember:** This is YOUR research system. Customize it to match YOUR workflow!

---

Generated for: Software Team Lead / University Research
Topics: Software leadership, innovation, productivity, EdTech, UK higher education
