---
name: rdt-thread-curation
description: |
  Batch process Twitter/X threads for research curation. Use when: (1) user has bookmarked threads on engineering culture, innovation, or tech topics, (2) need to download and organize Twitter discussions, (3) curating social media insights for Obsidian or NotebookLM. Covers creating URL lists, batch downloading, tagging, and analysis integration.
author: Claude Code
version: 1.0.0
---

# Twitter/X Thread Curation Workflow

## Problem

Need to systematically collect, organize, and analyze Twitter/X threads containing valuable insights on software leadership, engineering culture, innovation, or academic topics.

## Context / Trigger Conditions

Use this skill when:
- User has bookmarked Twitter threads they want to preserve
- Need to curate social media discussions for research
- Want to capture practitioner insights before they disappear from feeds
- Integrating Twitter content with Obsidian or NotebookLM workflow

## Solution

### Step 1: Create URL List File

Create a text file with thread URLs organized by topic:

```bash
# Create file
touch software_leadership_threads.txt
```

**Format with comments for organization:**
```
# Engineering Culture
https://twitter.com/kelseyhightower/status/1234567890
https://twitter.com/charity/status/9876543210

# Developer Productivity
https://twitter.com/simonw/status/1111111111
https://twitter.com/swyx/status/2222222222

# Team Dynamics & Leadership
https://twitter.com/lethain/status/3333333333
https://twitter.com/shreyas/status/4444444444

# Platform Engineering
https://twitter.com/jessitron/status/5555555555

# Innovation & R&D
https://twitter.com/rands/status/6666666666
```

**Pro tip:** Use browser bookmarks export or Twitter bookmark export tools to get URLs.

### Step 2: Batch Download Threads

**Basic download (plain markdown):**
```bash
./thread_reader.py -f software_leadership_threads.txt
```

**Download with Obsidian formatting:**
```bash
./thread_reader.py -f software_leadership_threads.txt --format obsidian
```

**Output location:**
```
notebooklm_sources_threads/
├── thread_kelseyhightower_2024-01-15_1234567890.md
├── thread_charity_2024-01-16_9876543210.md
└── ...
```

**What you get:**
- Full thread text (all tweets)
- Author name and handle
- Publication date
- Thread URL
- YAML frontmatter (with `--format obsidian`)

### Step 3: Organize by Topic

**Move to topic-specific folders:**
```bash
# Create topic folders
mkdir -p curated_threads/engineering_culture
mkdir -p curated_threads/dev_productivity
mkdir -p curated_threads/team_dynamics
mkdir -p curated_threads/platform_engineering
mkdir -p curated_threads/innovation

# Move files (manually or with script)
mv notebooklm_sources_threads/thread_kelseyhightower_*.md \
   curated_threads/engineering_culture/

# Or integrate with research digest
mv notebooklm_sources_threads/*.md \
   research_digest/$(date +%Y-%m-%d)/obsidian/
```

### Step 4: Tag in Obsidian

If using `--format obsidian`, files have YAML frontmatter:

```yaml
---
type: twitter-thread
author: Kelsey Hightower
handle: @kelseyhightower
date: 2024-01-15
tags: [twitter, thread]
---
```

**Add topic tags:**
```bash
# Open file in editor
vim curated_threads/engineering_culture/thread_kelseyhightower_*.md
```

**Update tags in frontmatter:**
```yaml
---
type: twitter-thread
author: Kelsey Hightower
handle: @kelseyhightower
date: 2024-01-15
tags: [twitter, thread, engineering-culture, distributed-systems, leadership]
topic: engineering-culture
source: twitter-curation
---
```

**Tag suggestions by category:**

**Engineering Culture:**
- `#engineering-culture`
- `#psychological-safety`
- `#team-dynamics`
- `#developer-experience`

**Developer Productivity:**
- `#dev-productivity`
- `#tools`
- `#workflow`
- `#automation`

**Leadership:**
- `#leadership`
- `#management`
- `#tech-lead`
- `#org-design`

**Innovation:**
- `#innovation`
- `#r-and-d`
- `#experimentation`
- `#product-development`

**Platform Engineering:**
- `#platform-engineering`
- `#internal-tools`
- `#developer-platform`

### Step 5: Import to Obsidian

**Manual import:**
```bash
# Copy curated threads to vault
cp -r curated_threads/* ~/Documents/Obsidian/Research/Twitter/

# Or copy to today's research digest
cp curated_threads/*/*.md \
   research_digest/$(date +%Y-%m-%d)/obsidian/
```

**Obsidian workflow:**
1. Open vault
2. Navigate to imported threads
3. Read and annotate
4. Create links to related notes
5. Add to daily notes or MOCs (Maps of Content)

**Create MOC (Map of Content):**
```markdown
# Engineering Culture - Twitter Insights

## Core Themes

### Psychological Safety
- [[thread_kelseyhightower_2024-01-15]] - On building trust
- [[thread_charity_2024-01-20]] - Blameless postmortems

### Developer Experience
- [[thread_simonw_2024-02-01]] - Internal tooling
- [[thread_jessitron_2024-02-10]] - Platform abstractions

## Key Practitioners
- [[Kelsey Hightower]] - Distributed systems, culture
- [[Charity Majors]] - Observability, leadership
```

### Step 6: Upload to NotebookLM

**Prepare for upload:**
```bash
# Threads are already in markdown format
# Check file sizes (NotebookLM limit: 400k chars)
wc -m curated_threads/*/*.md
```

**If files too large, split them:**
```bash
./file_splitter.py curated_threads/engineering_culture/large_thread.md
```

**Upload process:**
1. Go to [NotebookLM](https://notebooklm.google.com/)
2. Create notebook: "Engineering Culture - Twitter Insights"
3. Upload all curated thread files
4. Wait for processing

**Synthesis queries:**
- "What are the main themes in these engineering culture threads?"
- "What do practitioners say about psychological safety?"
- "Summarize debates about platform engineering approaches."
- "What tools and practices are mentioned most frequently?"
- "Compare perspectives on [specific topic]."

### Step 7: Automation Script

Create `curate_threads.sh`:

```bash
#!/bin/bash
# curate_threads.sh - Batch process Twitter threads

# Configuration
THREAD_LIST="$1"  # Path to URL list file
OUTPUT_DIR="curated_threads"
DIGEST_DIR="research_digest/$(date +%Y-%m-%d)/obsidian"

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Download threads
echo "Downloading threads from $THREAD_LIST..."
./thread_reader.py -f "$THREAD_LIST" --format obsidian

# Move to output directory
echo "Organizing threads..."
mv notebooklm_sources_threads/*.md "$OUTPUT_DIR/"

# Optional: Copy to today's research digest
if [ -d "$DIGEST_DIR" ]; then
    echo "Copying to research digest..."
    cp "$OUTPUT_DIR"/*.md "$DIGEST_DIR/"
fi

echo "Complete! Threads in $OUTPUT_DIR/"
echo "Next steps:"
echo "1. Tag threads in Obsidian"
echo "2. Upload to NotebookLM for synthesis"
```

**Make executable:**
```bash
chmod +x curate_threads.sh
```

**Usage:**
```bash
./curate_threads.sh software_leadership_threads.txt
```

## Verification

1. **Threads downloaded:**
   ```bash
   ls -lh notebooklm_sources_threads/
   # Should contain thread_*.md files
   ```

2. **YAML frontmatter present:**
   ```bash
   head -20 notebooklm_sources_threads/thread_*.md
   # Should start with ---
   # Contains: type, author, handle, date, tags
   ```

3. **Full thread content:**
   ```bash
   wc -l notebooklm_sources_threads/thread_*.md
   # Should have substantial line count (full thread)
   ```

4. **Obsidian import successful:**
   - Open Obsidian
   - Search for imported threads
   - Tags should be clickable
   - Metadata visible in frontmatter

## Troubleshooting

**Error: "Thread not found" or "Rate limited":**
- Twitter/X may block scraping or rate limit
- Wait 15-30 minutes and retry
- Some threads may be deleted or private
- Use official Twitter API if available

**Threads missing content:**
- Check if thread was deleted
- Verify URL format is correct
- Some protected accounts can't be scraped

**Files too large for NotebookLM:**
```bash
# Split large files
./file_splitter.py large_thread.md
# Creates: large_thread_part1.md, large_thread_part2.md, etc.
```

**YAML frontmatter not appearing:**
- Verify `--format obsidian` flag used
- Check file encoding (should be UTF-8)

## Advanced Workflows

### Weekly Thread Digest

Create `weekly_threads.sh`:
```bash
#!/bin/bash
# Combine with weekly research digest

# Download threads
./thread_reader.py -f this_week_threads.txt --format obsidian

# Move to this week's digest
TODAY=$(date +%Y-%m-%d)
mv notebooklm_sources_threads/*.md research_digest/$TODAY/obsidian/

# Run main digest
./research_digest.py

echo "Weekly digest + threads complete!"
echo "Check: research_digest/$TODAY/"
```

### Topic-Based Curation

Maintain separate URL lists per topic:
```bash
# Create topic-specific lists
threads/
├── engineering_culture.txt
├── dev_productivity.txt
├── platform_engineering.txt
└── innovation.txt

# Process each topic
for topic_file in threads/*.txt; do
    ./thread_reader.py -f "$topic_file" --format obsidian
done
```

### Integration with Daily Notes

```bash
# Add to today's daily note in Obsidian
echo "## Twitter Threads" >> ~/Documents/Obsidian/Daily/$(date +%Y-%m-%d).md
echo "" >> ~/Documents/Obsidian/Daily/$(date +%Y-%m-%d).md

# List downloaded threads
for thread in notebooklm_sources_threads/*.md; do
    basename "$thread" .md >> ~/Documents/Obsidian/Daily/$(date +%Y-%m-%d).md
done
```

## Use Cases

**Software Leadership Research:**
- Curate practitioner insights on team dynamics
- Track debates about engineering culture
- Collect perspectives on leadership challenges

**Innovation Research:**
- Capture early discussions about emerging practices
- Track how ideas evolve in community discourse
- Identify patterns in product development approaches

**Academic Research:**
- Preserve ephemeral social media data
- Analyze practitioner vs academic perspectives
- Study knowledge sharing in professional communities

**Personal Knowledge Management:**
- Build reference library of expert insights
- Create topic-based collections
- Link to related literature and blog posts

## References

- **Thread Reader Guide:** `THREAD_READER_GUIDE.md`
- **Weekly digest workflow:** `.claude/skills/weekly-research-digest/SKILL.md`
- **Obsidian prep:** `obsidian_prep.py`
- **File splitter:** `file_splitter.py`
