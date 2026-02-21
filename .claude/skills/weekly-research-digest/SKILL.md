---
name: weekly-research-digest
description: |
  Complete weekly research digest workflow for software leadership and academic research. Use when: (1) user wants to set up automated research aggregation, (2) weekly review of technical content, (3) preparing content for Obsidian or NotebookLM analysis. Covers running digest, reviewing results, Obsidian integration, and NotebookLM upload.
author: Claude Code
version: 1.0.0
---

# Weekly Research Digest Workflow

## Problem

Need a systematic workflow for aggregating, reviewing, and organizing research content from multiple sources (HackerNews, RSS feeds, Reddit, arXiv) on a weekly basis.

## Context / Trigger Conditions

Use this skill when:
- User asks "How do I run the weekly research digest?"
- Setting up automated research aggregation workflow
- Need to organize content for Obsidian vault or NotebookLM
- Want to review software leadership, innovation, or academic research trends

## Solution

### Step 1: Configure Your Research Topics

Edit `research_config.yaml` to match your research interests:

```bash
# Open config file
vim research_config.yaml  # or your preferred editor
```

**Key sections to customize:**

```yaml
scrapers:
  hackernews:
    enabled: true
    min_points: 50           # Adjust threshold
    search_topics:
      - "your research area"  # Add your keywords

  rss:
    enabled: true
    feeds:
      - url: "https://blog.example.com/feed/"
        name: "Blog Name"
        tags: ["your-tags"]

  reddit:
    enabled: true
    subreddits:
      - name: "YourSubreddit"
        min_upvotes: 100

topics:
  your_category:
    - "keyword 1"
    - "keyword 2"
```

### Step 2: Run the Digest

**One-time run:**
```bash
./research_digest.py
```

**Scheduled run (built-in scheduler):**
```bash
# Weekly digest every Monday at 9 AM
./research_digest.py --schedule "every().monday.at('09:00')"

# Every 4 hours
./research_digest.py --schedule "every(4).hours"
```

**Alternative: Cron job**
```bash
# Edit crontab
crontab -e

# Add weekly digest (Mondays at 9 AM)
0 9 * * 1 cd /home/doug/Documents/AIProjectWork/Scripts && ./research_digest.py --run-once
```

**Output structure:**
```
research_digest/
└── 2026-02-21/
    ├── raw/                 # Original content by source
    │   ├── hackernews/
    │   ├── rss/
    │   └── reddit/
    ├── obsidian/            # Formatted for Obsidian (YAML frontmatter, tags)
    │   └── *.md
    └── REPORT.md            # Summary of findings
```

### Step 3: Review the Results

**Quick summary:**
```bash
# View today's report
cat research_digest/$(date +%Y-%m-%d)/REPORT.md
```

**Count items by source:**
```bash
# HackerNews items
ls research_digest/$(date +%Y-%m-%d)/raw/hackernews/ | wc -l

# RSS items
ls research_digest/$(date +%Y-%m-%d)/raw/rss/ | wc -l

# Reddit items
ls research_digest/$(date +%Y-%m-%d)/raw/reddit/ | wc -l
```

**Browse content:**
```bash
# Open in your preferred markdown viewer
cd research_digest/$(date +%Y-%m-%d)/obsidian/
ls -lh  # List formatted files
```

### Step 4: Import to Obsidian

**Option A: Manual copy to vault**
```bash
# Copy all formatted content
cp -r research_digest/$(date +%Y-%m-%d)/obsidian/* \
      ~/Documents/Obsidian/Research/

# Or copy selectively
cp research_digest/$(date +%Y-%m-%d)/obsidian/interesting_article.md \
   ~/Documents/Obsidian/Research/
```

**Option B: Configure auto-copy in YAML**
```yaml
# research_config.yaml
output:
  base_dir: "research_digest"
  obsidian_vault: "/path/to/your/vault/Research"  # Auto-copy here
```

**Obsidian workflow:**
1. Open Obsidian vault
2. Navigate to Research folder
3. Review files with tags (auto-tagged based on `topics` config)
4. Add your own notes/links
5. Create connections to existing notes

### Step 5: Upload to NotebookLM

**Files are already formatted:**
- All files in `obsidian/` directory are markdown
- Already split to 400k character limit (NotebookLM max)
- Include YAML frontmatter with metadata

**Upload process:**
1. Go to [NotebookLM](https://notebooklm.google.com/)
2. Create new notebook or open existing
3. Click "Add Source" → "Upload"
4. Select all files from `research_digest/YYYY-MM-DD/obsidian/`
5. Wait for processing
6. Ask NotebookLM to synthesize insights

**Example queries for NotebookLM:**
- "What are the main themes in this week's research?"
- "Summarize discussions about [your topic]"
- "What are the key debates or disagreements?"
- "What new tools or practices are emerging?"

### Step 6: Deduplication Across Runs

The toolkit automatically deduplicates content using SQLite:

```bash
# Check what's been scraped
sqlite3 research_digest_state.db "SELECT url, title, scraped_at FROM items ORDER BY scraped_at DESC LIMIT 10;"
```

**Deduplication logic:**
- Tracks URLs and titles
- Skips already-scraped items on subsequent runs
- Prevents duplicate content in your digest

### Optional: Thread Curation

For Twitter/X threads not captured by automated scrapers:

```bash
# Single thread
./thread_reader.py https://twitter.com/username/status/123 --format obsidian

# Batch processing (create threads.txt with URLs)
./thread_reader.py -f software_leadership_threads.txt --format obsidian

# Manually copy to digest folder
mv notebooklm_sources_threads/*.md research_digest/$(date +%Y-%m-%d)/obsidian/
```

## Verification

1. **Digest runs successfully:**
   ```bash
   ./research_digest.py
   # Check for "Found plugin: ..." messages
   # No errors in console
   ```

2. **Output created:**
   ```bash
   ls research_digest/$(date +%Y-%m-%d)/
   # Should have: raw/, obsidian/, REPORT.md
   ```

3. **Items scraped:**
   ```bash
   cat research_digest/$(date +%Y-%m-%d)/REPORT.md
   # Should list counts per source
   ```

4. **Obsidian files formatted:**
   ```bash
   head -20 research_digest/$(date +%Y-%m-%d)/obsidian/some_file.md
   # Should have YAML frontmatter with tags
   ```

## Troubleshooting

**No items scraped:**
- Check `min_points`, `min_upvotes` thresholds in config (might be too high)
- Verify `search_topics` match actual content
- Check if `days_back` is too short (try 14 days)

**Rate limited (429 errors):**
- Wait and re-run (retry logic will handle it)
- Reduce number of enabled scrapers temporarily
- Check if API keys are valid (for Reddit, arXiv)

**Obsidian files not created:**
- Verify `processing.format_for_obsidian: true` in config
- Check if `obsidian/` directory exists in output

**Files too large for NotebookLM:**
- Set `processing.split_large_files: true`
- Adjust `processing.max_file_size: 400000` (characters)

## Automation Tips

**Weekly digest + automated analysis:**
```bash
#!/bin/bash
# weekly_digest.sh

# Run digest
./research_digest.py

# Get today's folder
TODAY=$(date +%Y-%m-%d)

# Copy to Obsidian
cp -r research_digest/$TODAY/obsidian/* ~/Documents/Obsidian/Research/

# Generate summary (optional - requires NotebookLM API or similar)
echo "Digest complete. Files in research_digest/$TODAY/"
echo "Upload obsidian/ folder to NotebookLM for analysis."
```

**Make it executable:**
```bash
chmod +x weekly_digest.sh
```

**Schedule with cron:**
```bash
# Every Monday at 9 AM
0 9 * * 1 /home/doug/Documents/AIProjectWork/Scripts/weekly_digest.sh
```

## Example Workflow Timeline

**Monday 9:00 AM** (automated)
- Cron triggers `./research_digest.py`
- Scrapes HN, RSS, Reddit, arXiv
- Generates formatted output

**Monday 10:00 AM** (manual)
- Review `REPORT.md` summary
- Skim interesting titles in `obsidian/` folder
- Decide what to read deeply

**Monday afternoon** (manual)
- Upload `obsidian/` folder to NotebookLM
- Ask synthesis questions
- Take notes in Obsidian
- Link to related existing notes

**Throughout week**
- Add manual threads via `thread_reader.py`
- Scrape individual articles with `web_scraper.py`
- All content auto-tagged and organized

## References

- **Project overview:** `.claude/rules/project.md`
- **YAML config:** `.claude/rules/yaml-config.md`
- **Automation guide:** `AUTOMATION_GUIDE.md`
- **Thread reader guide:** `THREAD_READER_GUIDE.md`
