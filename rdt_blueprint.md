# Research Digest Toolkit (RDT) - Refactoring & Installation Blueprint

## 1. Project Overview
The **Research Digest Toolkit (RDT)** is being transformed from a collection of scripts into a professional, installable Python Terminal User Interface (TUI) application. This blueprint outlines the transition from bash-heavy processing to a cross-platform Python-native architecture.

## 2. Core Architecture (Modular CLI)
The application follows a **Separation of Concerns** model to ensure maintainability and testability:

| Module | Responsibility |
| :--- | :--- |
| `rdt.core` | Document processing logic, sanitisation, and path management. |
| `rdt.tui` | The Terminal User Interface (Views, Inputs, Progress Bars) using **Textual**. |
| `rdt.adapters` | Integration logic for Obsidian, Substack (UK English), and NotebookLM. |
| `rdt.cli` | Entry point and command-line argument parsing (using **Typer**). |
| `rdt.config` | User preference management and path configuration. |

## 3. Technical Stack
* **Language:** Python 3.12+ (Strict UK English for strings/logs).
* **TUI Library:** `Textual` (Modern, CSS-driven terminal interface).
* **CLI Framework:** `Typer` (Standard for Python CLI structures).
* **Dependency Management:** `uv` or `pip`.
* **Document Parsing:** `PyMuPDF` or `python-magic` (replacing bash-based system calls).
* **Packaging:** `Setuptools` with `pyproject.toml` for standard installation.

## 4. Implementation Plan (Agent Instructions)

### Phase 1: Porting Bash Logic
1.  Analyze `convert_documents.sh` to extract conversion parameters.
2.  Replace `pandoc` or system-level calls with Python equivalents where possible, or wrap them in safe `subprocess` calls with dependency checks.
3.  Implement a `FileSystemWatcher` or a robust file picker in the TUI.

### Phase 2: TUI Development
1.  Formalise the existing TUI code into `rdt/tui/app.py`.
2.  Implement a multi-pane layout: 
    * **Left:** File browser / Source selection.
    * **Center:** Configuration/Metadata editing.
    * **Right:** Preview / Log output.

### Phase 3: Installation & Packaging
1.  Create a `pyproject.toml` that defines the entry point:
    ```toml
    [project.scripts]
    rdt = "rdt.cli.main:app"
    ```
2.  Implement a "Self-Check" feature: `rdt --check` to verify system dependencies.

## 5. Antigravity Agent Guidelines
When using Google Antigravity to build this:

* **Model Selection:**
    * Use **High-Level Reasoning Models** (e.g., Gemini 1.5 Pro) for structural refactoring and logic mapping.
    * Use **Task Completion Models** (e.g., Gemini 1.5 Flash) for writing unit tests and CSS-styling for the TUI.
* **Agent Prompts:**
    * *"Refactor the bash logic in convert_documents.sh into a Python class in rdt/core/converter.py. Use TDD."*
    * *"Create a Textual TUI screen that allows users to select a directory and filters for .pdf and .md files."*
* **Cross-Platform Strategy:**
    * Use `pathlib` for all file operations to ensure Windows compatibility.
    * Avoid hardcoded `/tmp/` paths; use `tempfile.gettempdir()`.

## 6. Testing Protocol (TDD)
1.  **Red:** Write a test in `tests/test_conversion.py` that fails.
2.  **Green:** Implement the Python logic to pass the test.
3.  **Refactor:** Ensure the code is clean and adheres to the UK English documentation standards.

## 7. Definition of Done
- [ ] `pip install -e .` works locally.
- [ ] Typing `rdt` in the terminal launches the TUI.
- [ ] Application processes a PDF and outputs a formatted Markdown file for Obsidian.
- [ ] 85%+ Test coverage.
