# Spec: Future Enhancements

**Status:** Proposed
**Priority:** P3 (Nice to Have)
**Created:** 2026-02-21
**Last Updated:** 2026-02-21

---

## Overview

Collection of proposed enhancements to extend the Research Digest Toolkit with new features, data sources, and integrations. These are tracked separately from the core roadmap and can be implemented independently.

---

## 1. Formal Packaging & Distribution

**Problem:** Project currently runs as scripts. No formal Python package structure.

**Proposed Solution:**

Create proper `pyproject.toml` with:
- Package metadata (name, version, description, author)
- Console script entry points: `research-digest run`, `research-digest config`
- Dependency specification with version constraints
- Optional dependencies for different features

**Benefits:**
- Install with `pip install -e .` for development
- Distribute via PyPI for wider adoption
- Better dependency management
- IDE integration improvements

**Implementation Checklist:**
- [ ] Create `pyproject.toml` with build system
- [ ] Define console script entry points
- [ ] Move scripts to `src/research_digest/` package structure
- [ ] Add `__main__.py` for `python -m research_digest`
- [ ] Test installation in clean virtual environment

**Priority:** P2 (good developer experience)

---

## 2. New Content Sources

### 2.1 Mastodon/Fediverse

**Problem:** Twitter/X not enough for comprehensive social media coverage.

**Proposed Solution:**

Add `scrapers/mastodon_scraper.py`:
- Query specific instances (mastodon.social, fosstodon.org, etc.)
- Filter by hashtags or user accounts
- Respect instance rate limits
- Handle federated content

**Configuration:**
```yaml
scrapers:
  mastodon:
    enabled: true
    instances:
      - url: "https://mastodon.social"
        hashtags: ["engineeringculture", "platformengineering"]
      - url: "https://fosstodon.org"
        accounts: ["username"]
    days_back: 7
```

**Dependencies:** `Mastodon.py` library

**Priority:** P2 (growing importance of Fediverse)

### 2.2 GitHub Trending

**Problem:** Miss trending repositories and discussions.

**Proposed Solution:**

Add `scrapers/github_scraper.py`:
- Trending repositories (daily/weekly/monthly)
- Discussions in specific repos
- Issues with high activity
- Use GitHub API (authenticated for higher rate limits)

**Configuration:**
```yaml
scrapers:
  github:
    enabled: true
    trending:
      language: "Python"
      since: "daily"
    repositories:
      - "anthropics/anthropic-sdk-python"
      - "astral-sh/ruff"
    track_issues: true
    min_stars: 100
```

**Dependencies:** `PyGithub` library

**Priority:** P1 (highly relevant for software leadership research)

### 2.3 Zotero/Mendeley Integration

**Problem:** Users already maintain reference libraries separately.

**Proposed Solution:**

Add `scrapers/zotero_scraper.py`:
- Read from user's Zotero library via API
- Filter by collection or tags
- Import recent additions (last 7 days)
- Extract annotations/notes if available

**Configuration:**
```yaml
scrapers:
  zotero:
    enabled: true
    api_key: "your_key"
    user_id: "12345"
    collections:
      - "Engineering Culture"
      - "Innovation"
    days_back: 7
```

**Dependencies:** `pyzotero` library

**Priority:** P3 (nice integration for academics)

---

## 3. Enhanced Content Processing

### 3.1 AI-Powered Summarization

**Problem:** Long articles hard to review quickly.

**Proposed Solution:**

Add optional post-processing step:
- Use Claude API or local model (llama.cpp)
- Generate 2-3 sentence summaries
- Extract key insights
- Store in YAML frontmatter

**Configuration:**
```yaml
processing:
  ai_summarization:
    enabled: false
    provider: "anthropic"  # or "local"
    model: "claude-3-haiku-20240307"
    api_key: "${ANTHROPIC_API_KEY}"
    max_length: 3  # sentences
```

**Cost consideration:** ~$0.25 per 100 articles (using Haiku)

**Priority:** P2 (high value, but API costs)

### 3.2 Automated Cross-Linking

**Problem:** Related articles not connected in Obsidian.

**Proposed Solution:**

Add post-processing to create `[[wikilinks]]`:
- TF-IDF similarity between articles
- Shared topic detection
- Entity co-occurrence (people, products, orgs)
- Insert links in markdown files

**Configuration:**
```yaml
processing:
  cross_linking:
    enabled: false
    similarity_threshold: 0.7
    max_links_per_article: 5
```

**Dependencies:** `scikit-learn` (already used in trend analysis spec)

**Priority:** P3 (nice to have for knowledge graph building)

### 3.3 Named Entity Recognition (NER)

**Problem:** Don't track which people, products, or organizations are mentioned.

**Proposed Solution:**

Add NER post-processing:
- Extract entities: PERSON, ORG, PRODUCT, GPE (geo-political entity)
- Add as tags in YAML frontmatter
- Generate entity index (who's being discussed most)

**Configuration:**
```yaml
processing:
  ner:
    enabled: false
    model: "en_core_web_sm"  # spaCy model
    entity_types: ["PERSON", "ORG", "PRODUCT"]
```

**Dependencies:** `spacy` + language model

**Priority:** P3 (interesting for research analysis)

---

## 4. Output & Integration Improvements

### 4.1 Enhanced Notifications

**Problem:** Basic REPORT.md not enough for busy users.

**Proposed Solution:**

Add notification system:
- HTML email reports (weekly digest summary)
- Push notifications via ntfy.sh or similar
- Slack/Discord webhooks
- Configurable notification thresholds (only if X new items)

**Configuration:**
```yaml
notifications:
  email:
    enabled: false
    smtp_server: "smtp.gmail.com"
    smtp_port: 587
    from: "digest@example.com"
    to: ["user@example.com"]
    frequency: "weekly"

  push:
    enabled: false
    service: "ntfy"
    topic: "research-digest"
    priority: "default"
```

**Priority:** P2 (helps with adoption)

### 4.2 Web Interface

**Problem:** CLI-only limits accessibility for non-technical users.

**Proposed Solution:**

Build simple web UI with FastAPI:
- View recent digests
- Configure scrapers (enable/disable, settings)
- Browse archived content
- Search across all digests
- View trend analysis reports

**Tech stack:**
- Backend: FastAPI
- Frontend: HTMX + Tailwind (no build step)
- Database: Same SQLite

**Priority:** P4 (significant scope, lower priority)

---

## Implementation Priority

**P1 - High Value:**
- GitHub scraper
- AI summarization (if budget allows)

**P2 - Good Enhancements:**
- Formal packaging
- Mastodon scraper
- Enhanced notifications

**P3 - Nice to Have:**
- Cross-linking
- NER
- Zotero integration

**P4 - Future Vision:**
- Web interface

---

## References

- Original TODO: `docs/archive/TODO.md` (to be created)
- Plugin architecture: `.claude/rules/plugin-architecture.md`
- Add scraper skill: `.claude/skills/add-scraper-plugin/SKILL.md`
