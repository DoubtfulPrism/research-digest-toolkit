# Installation Guide — Research Digest Toolkit

## Quick Install (Recommended)

Install globally — no virtual environment activation required.

### With [uv](https://docs.astral.sh/uv/) (recommended)

```bash
uv tool install git+https://github.com/DoubtfulPrism/research-digest-toolkit.git@main
```

### With [pipx](https://pipx.pypa.io/)

```bash
pipx install git+https://github.com/DoubtfulPrism/research-digest-toolkit.git@main
```

Both commands create an isolated environment behind the scenes — you never need to
activate anything. The `rdt` and `Research_Toolkit` commands are placed in `~/.local/bin/`
automatically.

> **Note:** Ensure `~/.local/bin` is on your `PATH`. Most Linux distributions include it
> by default. If not, add `export PATH="$HOME/.local/bin:$PATH"` to your shell profile.

### Platform-Specific Prerequisites

| Platform | Python |
|----------|--------|
| **Linux (Fedora/RHEL)** | `sudo dnf install python3` |
| **Linux (Debian/Ubuntu)** | `sudo apt install python3` |
| **macOS (Homebrew)** | `brew install python` |
| **Windows** | `winget install Python.Python.3` |

Optional native tools for higher-quality document conversion:

```bash
# Fedora/RHEL
sudo dnf install pandoc poppler-utils

# Debian/Ubuntu
sudo apt install pandoc poppler-utils
```

---

## After Installation

Launch the TUI:

```bash
rdt tui
```

On first run, a starter config is created at `~/.research_digest/research_config.yaml`.
Edit it to enable scrapers and customise your research topics.

---

## Upgrading

```bash
# uv
uv tool upgrade research-digest-toolkit

# pipx
pipx upgrade research-digest-toolkit
```

---

## Development Install

Clone the repository and set up an editable development environment:

```bash
git clone https://github.com/DoubtfulPrism/research-digest-toolkit.git
cd research-digest-toolkit

# Option A: automated setup
bash install.sh

# Option B: manual setup
uv sync --all-extras
source .venv/bin/activate
```

Run the TUI from the development environment:

```bash
rdt tui
```

Run the test suite:

```bash
pytest tests/
```

---

## Configuration

The config file is discovered in this order:

1. `./research_config.yaml` — project-local override (current working directory)
2. `~/.research_digest/research_config.yaml` — user home (created on first run)

See the comments in `~/.research_digest/research_config.yaml` for all available options.
