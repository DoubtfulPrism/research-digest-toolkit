# Utility Tools and Manual Scripts

This document provides a reference for the standalone utility scripts included in the toolkit.

> **Note on Scrapers:** Core data gathering from sources like Hacker News, RSS feeds, and Reddit is now handled automatically by the main `research_digest.py` script via its plugin system. The original standalone scraper scripts have been removed. To configure these scrapers, please see the `scrapers` section in `research_config.yaml`.

The tools listed below are for manual, one-off tasks or for processing content not covered by the automated scrapers.

## Installation

```bash
# Install dependencies
pip install --user -r requirements.txt

# Make scripts executable
chmod +x *.py *.sh

# Optional: Install native tools for better quality (recommended)
# See NATIVE_ALTERNATIVES.md for details
sudo dnf install pandoc poppler-utils
```

## Scripts

### 1. Web Scraper (`web_scraper.py`)

Scrapes web pages and saves clean text content.

**Features:**
- Removes scripts, styles, navigation, and other non-content elements
- Supports batch processing from URL file
- Auto-generates filenames from page titles
- Custom output directory

**Usage:**
```bash
# Single URL
./web_scraper.py https://example.com

# Multiple URLs
./web_scraper.py https://example.com https://another.com

# From file
./web_scraper.py -f example_urls.txt

# Custom output directory
./web_scraper.py -o my_articles https://example.com

# Help
./web_scraper.py --help
```

**Output:** `notebooklm_sources_web/`

---

### 2. YouTube Transcript Downloader (`youtube_transcript.py`)

Downloads YouTube video transcripts with formatting options.

**Features:**
- Accepts URLs or video IDs
- Optional timestamps
- Language selection
- Batch processing from file
- Auto-generated filenames
- Paragraph formatting for readability

**Usage:**
```bash
# Single video
./youtube_transcript.py "https://www.youtube.com/watch?v=VIDEO_ID"

# With timestamps
./youtube_transcript.py VIDEO_ID --timestamps

# Specific language
./youtube_transcript.py VIDEO_ID --language es

# List available languages
./youtube_transcript.py VIDEO_ID --list-languages

# Batch from file
./youtube_transcript.py -f example_video_ids.txt

# Custom output directory
./youtube_transcript.py VIDEO_ID -d my_transcripts

# Save to specific file
./youtube_transcript.py VIDEO_ID -o transcript.txt

# Help
./youtube_transcript.py --help
```

**Output:** `notebooklm_sources_yt/`

---

### 3. File Splitter (`file_splitter.py`)

Splits large text files into NotebookLM-compatible chunks (400k character limit).

**Features:**
- Two split modes: by words or by lines
- Preserves file structure
- Recursive directory processing
- Support for many text file formats
- Progress reporting
- Smart chunk numbering

**Usage:**
```bash
# Process default directory (files_to_split/)
./file_splitter.py

# Split single file
./file_splitter.py -i largefile.txt

# Process directory
./file_splitter.py -i documents/ -o output/

# Custom character limit (200k)
./file_splitter.py -i file.txt -m 200000

# Split by lines (preserves line structure)
./file_splitter.py -i data.csv --lines

# Recursive subdirectories
./file_splitter.py -i docs/ -r

# Process all files (ignore extension filtering)
./file_splitter.py -i data/ --all

# Quiet mode
./file_splitter.py -i file.txt -q

# Help
./file_splitter.py --help
```

**Supported formats:**
`.txt`, `.md`, `.csv`, `.log`, `.json`, `.xml`, `.html`, `.py`, `.js`, `.java`, `.c`, `.cpp`, `.h`, `.sh`, `.yaml`, `.yml`, `.toml`, `.ini`, `.conf`, `.rst`, `.tex`

**Output:** `notebooklm_sources_split/`

---

### 4. File Converter (`file_converter.py`)

Convert between document formats (txt, md, html, docx, pdf).

> **Note:** For better quality conversions, especially PDF extraction, consider using native Linux tools like `pandoc` and `pdftotext`. See `NATIVE_ALTERNATIVES.md` for detailed comparison and usage.

**Features:**
- Convert between multiple formats
- Batch processing support
- Smart format detection
- Preserves basic formatting
- Optional dependencies (works without them)

**Usage:**
```bash
# Convert PDF to text
./file_converter.py document.pdf --to txt

# Convert DOCX to markdown
./file_converter.py file.docx --to md

# Batch convert all PDFs to text
./file_converter.py *.pdf --to txt --batch

# Save to specific file
./file_converter.py input.docx --to md -o output.md

# Convert to specific directory
./file_converter.py *.txt --to md --batch -o converted/

# Help
./file_converter.py --help
```

**Supported Conversions:**
- PDF → TXT, MD
- DOCX → TXT, MD
- HTML → TXT, MD
- MD → TXT, DOCX
- TXT → MD

**Native Alternatives (Recommended):**
```bash
# Better PDF extraction
pdftotext input.pdf output.txt

# Universal converter (best quality)
pandoc input.docx -o output.md
```

**Output:** `converted/` (default batch directory)

---

### 5. Thread Reader (`thread_reader.py`)

Download and format Twitter/X threads (no API required).

> **Note:** Uses Nitter instances to avoid Twitter's API costs. If Nitter is experiencing downtime, use threadreaderapp.com as a fallback.

**Features:**
- Downloads complete Twitter/X threads
- No API keys or authentication needed
- Multiple output formats (markdown, text, Obsidian)
- Batch processing support
- Automatic thread parsing and formatting
- Rate limiting for batch requests

**Usage:**
```bash
# Download a single thread
./thread_reader.py https://twitter.com/user/status/123456789

# Use X.com URLs
./thread_reader.py https://x.com/user/status/123456789

# Save in Obsidian format
./thread_reader.py https://twitter.com/user/status/123 --format obsidian

# Batch process from file
./thread_reader.py -f example_threads.txt

# Custom output file
./thread_reader.py https://twitter.com/user/status/123 -o my_thread.md

# Quiet mode with delay between requests
./thread_reader.py -f threads.txt --delay 3 -q

# Help
./thread_reader.py --help
```

**Output Formats:**
- `markdown` - Standard markdown (default)
- `text` - Plain text
- `obsidian` - Markdown with YAML frontmatter for Obsidian

**Fallback if Nitter is down:**
1. Visit https://threadreaderapp.com
2. Paste the thread URL
3. Copy the unrolled content
4. Save manually

**Output:** `notebooklm_sources_threads/`

---

### 6. Obsidian Formatter (`obsidian_prep.py`)

Format any scraped content for Obsidian with YAML frontmatter and auto-tagging.

**Features:**
- Add/update YAML frontmatter
- Auto-tag based on content keywords
- Add backlinks to related notes
- Batch process entire directories
- Preserve existing frontmatter
- Custom tag mapping for your research areas

**Usage:**
```bash
# Single file with auto-tagging
./obsidian_prep.py article.txt --auto-tag

# Add custom tags
./obsidian_prep.py thread.md --tags engineering-culture,team-dynamics

# Batch process to Obsidian vault
./obsidian_prep.py -i notebooklm_sources_web/ -o ~/Documents/Obsidian/Inbox/ --auto-tag

# Process all sources recursively
./obsidian_prep.py -i research_digest/2025-12-17/raw/ -r --vault ~/Documents/Obsidian/Research/ --auto-tag

# Add backlinks
./obsidian_prep.py article.md --backlink "Platform Engineering" --backlink "DevOps"

# Add custom frontmatter fields
./obsidian_prep.py file.md --add-field "author:John Doe" --add-field "priority:high"

# Modify in place
./obsidian_prep.py -i sources/ -r --auto-tag --in-place

# Help
./obsidian_prep.py --help
```

**Auto-Tag Categories:**
Automatically recognizes and tags content about:
- **Engineering culture**: remote work, team dynamics, psychological safety
- **Dev practices**: testing, CI/CD, code review, refactoring
- **Innovation**: architecture, platform engineering, microservices
- **Productivity**: automation, AI tools, developer experience
- **Knowledge management**: documentation, learning, onboarding
- **Leadership**: hiring, career development, performance management
- **Process**: agile, scrum, kanban, retrospectives

**Output Format:**
```yaml
---
type: web
created: 2024-01-15
source: web
title: Platform Engineering Best Practices
url: https://example.com
tags: [platform-engineering, devops, architecture]
---
```

**Output:** Specified directory or `obsidian_output/`

---

## Workflow Examples

### Complete Research Workflow
```bash
# 1. Run the automated digest to gather content from configured sources (HN, RSS, Reddit)
./research_digest.py

# 2. Manually gather content from other sources
./web_scraper.py -f research_urls.txt
./youtube_transcript.py -f research_videos.txt
./thread_reader.py -f example_threads.txt

# 3. (Optional) Manually format all gathered content for Obsidian
# Note: research_digest.py does this automatically for its content.
# This is only needed if you want to process manually gathered items.
./obsidian_prep.py -i notebooklm_sources_*/ -r --vault ~/Documents/Obsidian/Research/ --auto-tag

# 4. Split any large files for NotebookLM
./file_splitter.py -i research_digest/$(date +%Y-%m-%d)/obsidian/ -r --in-place
```

### Single Source Processing
```bash
# Get a specific article manually
./web_scraper.py https://longform-article.com

# Check if it needs splitting (if over 400k chars)
./file_splitter.py -i notebooklm_sources_web/Article_Title.txt
```

### Document Conversion Workflow
```bash
# Convert PDFs to text (use native tool for better quality)
pdftotext research.pdf research.txt

# Or use Python script for batch
./file_converter.py *.pdf --to txt --batch

# Convert DOCX to markdown
pandoc report.docx -o report.md

# Or use Python script
./file_converter.py report.docx --to md

# Split if needed
./file_splitter.py -i converted/ -r
```

---

## Directory Structure

```
Scripts/
├── research_digest.py          # Main orchestrator
├── scrapers/                   # Scraper plugins (hn_scraper.py, etc.)
│   ├── base.py
│   ├── hn_scraper.py
│   ├── reddit_scraper.py
│   └── rss_scraper.py
├── utils.py                    # Shared utility functions
├── database.py                 # Persistent state database logic
├── web_scraper.py              # Manual web scraping tool
├── youtube_transcript.py       # Manual YouTube transcript downloader
├── thread_reader.py            # Manual Twitter/X thread downloader
├── obsidian_prep.py            # Manual Obsidian formatter
├── file_splitter.py            # Utility to split large files
├── file_converter.py           # Utility for document conversion
├── requirements.txt            # Python dependencies
├── research_config.yaml        # Main configuration file
├── README.md                   # Project README
└── research_digest/            # Default output directory
    └── 2025-12-17/
        ├── raw/
        └── obsidian/
```

---

## Tips

1. **Batch Processing:** Use text files with `-f` flag to process multiple sources
2. **Large Files:** Always run file_splitter after scraping to ensure files meet NotebookLM limits
3. **Organization:** Each script uses its own output directory for easy management
4. **Quiet Mode:** Use `-q` flag when processing many files
5. **Extensions:** File splitter auto-detects text files, use `--all` to override
6. **Native Tools:** For document conversion, prefer `pandoc` and `pdftotext` - see `NATIVE_ALTERNATIVES.md`
7. **Obsidian Integration:** Use `obsidian_prep.py --auto-tag` to automatically categorize all your research
8. **HN Quality Filtering:** Use `--min-comment-score 10` to get only high-quality HN discussions
9. **Twitter Threads:** Bookmark threads throughout the week, batch download on Friday
10. **Research Pipeline:** Scrape → Format for Obsidian → Split for NotebookLM → Analyze

---

## Troubleshooting

**"No transcripts available"**
- Video may have disabled transcripts
- Try `--list-languages` to see available options

**"Encoding error" when splitting**
- File may not be UTF-8 text
- Use `--all` flag to attempt processing anyway

**Web scraper fails**
- Some sites block automated requests
- Check your internet connection
- Site may use JavaScript (not supported)

**"Package not installed" error in file_converter**
- Install optional dependencies: `pip install --user python-docx markdownify PyPDF2`
- Or use native tools instead (recommended): See `NATIVE_ALTERNATIVES.md`

**PDF extraction produces garbled text**
- PyPDF2 has limited capability
- Use native tool instead: `pdftotext input.pdf output.txt`
- For scanned PDFs, use OCR: `ocrmypdf input.pdf output.pdf`

---

## NotebookLM Integration

After running these scripts:
1. Navigate to [NotebookLM](https://notebooklm.google.com/)
2. Create a new notebook
3. Upload files from the output directories
4. Start analyzing!

**Remember:** NotebookLM has a ~400,000 character limit per source. Use `file_splitter.py` for larger files.
