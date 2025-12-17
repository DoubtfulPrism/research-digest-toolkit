# Project Roadmap & TODO List

This document outlines potential improvements and new features for the Research Digest Toolkit. It can be used to track progress as work is done.

---

## 🎯 Priority

1.  **Implement Persistent State Database**: Highest impact for performance and efficiency.
2.  **Create a Unified "Plugin" Architecture**: Best for long-term extensibility.
3.  **Consolidate Common Code**: Improves maintainability.
4.  **Add New Content Sources**: Expands the toolkit's reach.

---

## ✅ TODO List

### Architectural Improvements

- [ ] **Implement Persistent State Database**
    - [ ] Create a `database.py` module using `sqlite3` to manage state.
    - [ ] The database should store a unique ID (URL or item ID) for every processed item.
    - [ ] Modify scrapers (`rss_reader`, `hn_scraper`, etc.) to check the database before downloading content.
    - [ ] If an item already exists in the database, the scraper should skip it.
    - [ ] Add successfully downloaded items to the database.
    - [ ] Remove the old, inefficient `deduplicate` method from `research_digest.py`.

- [ ] **Create a Unified "Plugin" Architecture**
    - [ ] Design a base `Scraper` class that all scrapers will inherit from.
    - [ ] Refactor each scraper script into a plugin class in a `scrapers/` directory.
    - [ ] Modify `research_digest.py` to dynamically load and run scraper plugins based on the config file.

- [ ] **Consolidate Common Code into a `utils` Module**
    - [ ] Create a `utils.py` file.
    - [ ] Move shared logic (e.g., filename sanitization, file saving, HTTP requests) into utility functions in this module.
    - [ ] Refactor the scrapers to import and use these common functions.

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
