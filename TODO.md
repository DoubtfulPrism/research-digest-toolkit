# Project Roadmap & TODO List

This document outlines potential improvements and new features for the Research Digest Toolkit. It can be used to track progress as work is done.

---

## 🎯 Current Priorities

1.  **Add Automated Testing**: Foundation for quality assurance and confident development.
2.  **Formal Packaging**: Create `pyproject.toml` for proper distribution.
3.  **Add New Content Sources**: Expand toolkit reach (GitHub, Mastodon).
4.  **Enhanced Processing**: AI summarization, cross-linking, NER.

---

## ✅ Completed

### Architectural Improvements

- [x] **Implement Persistent State Database** *(Completed 2025-12-17)*
    - [x] Create a `database.py` module using `sqlite3` to manage state.
    - [x] The database stores a unique ID (URL or item ID) for every processed item.
    - [x] All scrapers check the database before downloading content.
    - [x] Items already in the database are skipped.
    - [x] Successfully downloaded items are added to the database.
    - [x] Database tracks 359+ items across 4 sources.

- [x] **Create a Unified "Plugin" Architecture** *(Completed 2025-12-17)*
    - [x] Design a base `Scraper` class that all scrapers inherit from.
    - [x] Refactor each scraper script into a plugin class in a `scrapers/` directory.
    - [x] Modify `research_digest.py` to dynamically load and run scraper plugins based on the config file.
    - [x] 4 scrapers implemented: ArXiv, HackerNews, RSS, Reddit.

- [x] **Consolidate Common Code into a `utils` Module** *(Completed 2025-12-17)*
    - [x] Create a `utils.py` file.
    - [x] Move shared logic (e.g., filename sanitization, HTML cleaning) into utility functions.
    - [x] Refactor the scrapers to import and use these common functions.

- [x] **Add ArXiv Content Source** *(Completed 2025-12-17)*
    - [x] Scraper for academic pre-prints by category or keyword.
    - [x] Configurable search queries and result limits.
    - [x] Timezone-aware datetime handling.

---

## 🚀 TODO List

### Quality Assurance

- [x] **Add Automated Testing** *(Completed 2025-12-18)*
    - [x] Set up pytest infrastructure with `tests/` directory.
    - [x] Write tests for `database.py` (deduplication, state tracking).
    - [x] Write tests for plugin loading mechanism in `research_digest.py`.
    - [x] Write tests for `utils.py` functions (sanitization, HTML cleaning).
    - [x] Write tests for base scraper class.
    - [x] Add integration tests for end-to-end workflows.
    - [x] Set up GitHub Actions CI/CD pipeline.
    - [x] 86 tests with 89%+ coverage on core modules.
    - [x] CI runs on Python 3.9, 3.10, 3.11, 3.12.
    - [x] Automated code quality checks and security scanning.

### Architectural Improvements

- [ ] **Improve Dependency and Execution Management**
    - [ ] Create a `pyproject.toml` file to formally package the project.
    - [ ] Define console script entry points for easier execution (e.g., `research-digest run`).

### Feature Extensions

- [ ] **Add New Content Sources**
    - [ ] **arXiv**: Scraper for academic pre-prints by category or keyword.
    - [ ] **Mastodon/Fediverse**: Scraper for public threads on specified instances.
    - [ ] **GitHub**: Scraper for trending repositories, discussions, or issues.
    - [ ] **Zotero/Mendeley**: Integration to read from a user's existing reference library.

- [ ] **Enhance Content Processing**
    - [ ] **AI-Powered Summarization**: Add an optional processing step to generate summaries for each item using an LLM.
    - [ ] **Automated Cross-Linking**: Create a post-processing step to add `[[wikilinks]]` between related articles in the digest output.
    - [ ] **Named Entity Recognition (NER)**: Use a library like SpaCy to identify and tag people, products, and organizations.

- [ ] **Improve Output and Integrations**
    - [ ] **Enhanced Notifications**: Create a dedicated script for sending formatted HTML email reports or push notifications (e.g., via ntfy.sh).
    - [ ] **Web Interface**: Build a simple web UI (e.g., with Flask or FastAPI) to manage the configuration and view reports.
