# Installation Guide — Research Digest Toolkit

## Quick Install

### Linux / macOS

With [uv](https://docs.astral.sh/uv/) (recommended):

```bash
uv pip install git+https://github.com/DoubtfulPrism/research-digest-toolkit.git@main
```

Or with pip:

```bash
pip install git+https://github.com/DoubtfulPrism/research-digest-toolkit.git@main
```

### macOS (Homebrew Python)

```bash
brew install python
pip3 install git+https://github.com/DoubtfulPrism/research-digest-toolkit.git@main
```

### Windows (winget)

```powershell
winget install Python.Python.3
pip install git+https://github.com/DoubtfulPrism/research-digest-toolkit.git@main
```

---

## After Installation

Launch the TUI:

```bash
Research_Toolkit
```

On first run, a starter config is created at `~/.research_digest/research_config.yaml`.
Edit it to enable scrapers and customise your research topics.

---

## Development Install

Clone the repository and install in editable mode:

```bash
git clone https://github.com/DoubtfulPrism/research-digest-toolkit.git
cd research-digest-toolkit
uv pip install -e ".[dev]"
```

Run the TUI directly:

```bash
python -m research_digest_tui
```

---

## Configuration

The config file is discovered in this order:

1. `./research_config.yaml` — project-local override (current working directory)
2. `~/.research_digest/research_config.yaml` — user home (created on first run)

See the comments in `~/.research_digest/research_config.yaml` for all available options.
