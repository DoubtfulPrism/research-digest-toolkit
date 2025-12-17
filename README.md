# Research Digest Toolkit

**Automated research aggregation for software leadership, innovation, and academic research**

> 🤖 **Vibecoded Project**: This project was developed through AI-assisted pair programming with Claude (Anthropic). The human provided requirements, domain expertise, and direction; Claude provided implementation, best practices, and code structure.

---

## 🎯 What This Is

A complete toolkit for automating research content discovery, aggregation, and organization. Designed for researchers, team leads, and knowledge workers who need to stay current across multiple sources.

**Single-command research digest:**
```bash
./research_digest.py
```

Automatically discovers, scrapes, and organizes content from:
- HackerNews discussions
- RSS feeds (blogs, journals)
- Reddit communities
- Twitter/X threads (manual curation)
- YouTube transcripts

**Output:** Organized by date, formatted for Obsidian, ready for NotebookLM analysis.

---

## ✨ Key Features

- **10 specialized tools** - Each optimized for specific content sources
- **Automated orchestration** - One command to rule them all
- **Native tool integration** - Uses `pandoc` & `pdftotext` for quality
- **Obsidian-ready** - YAML frontmatter + auto-tagging
- **NotebookLM-ready** - Automatic file splitting at 400k char limit
- **Deduplication** - Smart duplicate removal by URL/title
- **Configurable** - YAML config for topics, sources, thresholds
- **Schedulable** - Cron/systemd examples included

---

## 🛠️ Tools Included

### Content Gathering (6 tools)
| Tool | Source | Purpose |
|------|--------|---------|
| `web_scraper.py` | Web pages | Articles, blog posts |
| `youtube_transcript.py` | YouTube | Conference talks, tutorials |
| `thread_reader.py` | Twitter/X | Discussion threads |
| `hn_scraper.py` | HackerNews | Practitioner discussions |
| `rss_reader.py` | RSS/Atom | Blog feeds |
| `reddit_scraper.py` | Reddit | Community discussions |

### Content Processing (4 tools)
| Tool | Purpose |
|------|---------|
| `obsidian_prep.py` | Format for Obsidian + auto-tag |
| `file_splitter.py` | Split large files for NotebookLM |
| `file_converter.py` | Document format conversion |
| `convert_documents.sh` | Native tool wrapper (pandoc, pdftotext) |

### Orchestration
| Tool | Purpose |
|------|---------|
| `research_digest.py` | Run everything automatically |

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Python packages
pip install --user -r requirements.txt

# Native tools (optional but recommended for quality)
sudo dnf install pandoc poppler-utils  # Fedora/RHEL
# or
sudo apt install pandoc poppler-utils  # Debian/Ubuntu
```

### 2. Configure Your Topics

Edit `research_config.yaml`:

```yaml
topics:
  software_leadership:
    - "engineering culture"
    - "platform engineering"

  your_topic:
    - "your keywords"

rss_feeds:
  - url: "https://your-blog.com/feed"
    name: "Favorite Blog"
    tags: ["tag"]
```

### 3. Run

```bash
# Make scripts executable
chmod +x *.py *.sh

# Run the digest
./research_digest.py

# Check results
cat research_digest/$(date +%Y-%m-%d)/REPORT.md
```

### 4. Automate (Optional)

```bash
# Weekly digest every Monday at 9 AM
crontab -e

# Add this line:
0 9 * * 1 cd /path/to/Scripts && ./research_digest.py
```

---

## 📖 Documentation

- **[README.md](README.md)** - Detailed tool documentation
- **[AUTOMATION_GUIDE.md](AUTOMATION_GUIDE.md)** - Complete automation guide
- **[NATIVE_ALTERNATIVES.md](NATIVE_ALTERNATIVES.md)** - Native Linux tools guide
- **[NATIVE_TOOLS_SUMMARY.md](NATIVE_TOOLS_SUMMARY.md)** - Where we use native vs Python
- **[THREAD_READER_GUIDE.md](THREAD_READER_GUIDE.md)** - Twitter thread collection guide

---

## 🎓 Use Cases

### Software Team Lead
- Track engineering culture discussions (HN, Twitter, Reddit)
- Monitor platform engineering trends
- Aggregate developer productivity insights
- Auto-organized for weekly review

### University Researcher
- Monitor academic RSS feeds
- Track higher education discussions
- Aggregate EdTech trends
- Format for literature review workflow

### Knowledge Worker
- Curate topic-specific content
- Build personal knowledge base
- Feed NotebookLM for synthesis
- Integrate with Obsidian vault

---

## 💡 Example Workflow

### Weekly Research Digest

**Monday Morning (Automated):**
```bash
# Cron runs automatically
./research_digest.py

# Outputs to:
research_digest/2024-12-17/
├── raw/           # Original content
├── obsidian/      # Formatted & tagged
└── REPORT.md      # Summary
```

**Review:**
```bash
# Read summary
cat research_digest/$(date +%Y-%m-%d)/REPORT.md

# Import to Obsidian
cp -r research_digest/$(date +%Y-%m-%d)/obsidian/* \
      ~/Documents/Obsidian/Research/

# Upload to NotebookLM for analysis
# All files in obsidian/ are pre-formatted and split
```

---

## 🏗️ Architecture

### Design Philosophy

**Hybrid Approach**: Use the best tool for each job
- **Native tools** (pandoc, pdftotext) for document conversion → Quality
- **Python** for APIs, scraping, logic → Flexibility

### Pipeline

```
1. Discovery & Scraping (Python)
   ├─ HackerNews API
   ├─ RSS feeds (feedparser)
   └─ Reddit JSON API

2. Document Conversion (Native Tools)
   ├─ PDF → pdftotext + pandoc
   └─ DOCX → pandoc

3. Processing (Python)
   ├─ Obsidian formatting (YAML frontmatter)
   ├─ Auto-tagging (keyword matching)
   ├─ File splitting (NotebookLM limits)
   └─ Deduplication (URL/title hashing)

4. Output
   ├─ Date-organized folders
   ├─ Markdown with frontmatter
   └─ Summary report
```

---

## 🔧 Configuration

**`research_config.yaml`** - Main configuration file

Key sections:
- `topics` - Your research keywords
- `hackernews` - Search terms, thresholds
- `rss_feeds` - Blog URLs to monitor
- `reddit` - Subreddits to track
- `processing` - Auto-tag, split, dedupe settings

See [AUTOMATION_GUIDE.md](AUTOMATION_GUIDE.md) for detailed configuration options.

---

## 🤝 Contributing

This is a personal research toolkit, but contributions welcome!

**If you:**
- Add a new source (Mastodon, arXiv, etc.)
- Improve auto-tagging for specific domains
- Add new output formats
- Fix bugs

Please submit PRs with clear descriptions.

---

## 📜 License

MIT License - See [LICENSE](LICENSE) file

---

## 🙏 Acknowledgments

### Development
- **Vibecoded with**: Claude (Anthropic) - AI pair programming assistant
- **Human**: Doug - Domain expertise, requirements, use case definition
- **Approach**: Collaborative AI-assisted development

### Inspiration
- [Obsidian](https://obsidian.md/) - Personal knowledge management
- [NotebookLM](https://notebooklm.google.com/) - AI-powered research synthesis
- Reddit academic workflows - Community inspiration

### Tools
- **Python** - Primary language
- **pandoc** - Universal document converter
- **poppler-utils** - PDF text extraction
- Various Python libraries (see requirements.txt)

---

## 🔬 About Vibecoding

**Vibecoding** (AI-assisted development) was used extensively in this project:

**What the human provided:**
- Problem definition and use case
- Domain expertise (software leadership, academia)
- Requirements and feature requests
- Workflow design
- Testing and feedback

**What Claude provided:**
- Code implementation
- Best practices and patterns
- Documentation
- Error handling and edge cases
- Tool selection and integration

**Result:** A production-ready toolkit built faster than solo development, with better code quality through AI-assisted review.

---

## 📊 Stats

- **10 CLI tools** - Each with `--help` documentation
- **5,000+ lines** of well-documented Python
- **Native tool integration** - Best quality output
- **YAML configuration** - Easy customization
- **Cron-ready** - Set and forget automation
- **Obsidian + NotebookLM** - Seamless workflow integration

---

## 🚦 Status

**Production Ready** ✅

All tools are:
- ✅ Fully functional
- ✅ Documented
- ✅ Error handled
- ✅ Tested on Fedora/Linux
- ✅ Ready for automation

---

## 💬 Support

- **Documentation**: See guides in this repo
- **Issues**: Use GitHub issues for bugs/features
- **Discussion**: For general questions about setup

---

## 🗺️ Roadmap

Potential future additions:
- [ ] Mastodon/Fediverse integration
- [ ] arXiv paper monitoring
- [ ] Google Scholar alerts → RSS
- [ ] Slack/Discord notifications
- [ ] Email digest formatting
- [ ] Web UI for configuration
- [ ] Docker containerization

---

**Built with ❤️ and 🤖 for researchers who want to focus on thinking, not searching.**

---

*Last updated: December 2024*
*Development approach: Vibecoded (AI-assisted)*
