#!/usr/bin/env bash
# Research Digest Toolkit — Developer Setup
#
# This script sets up a LOCAL DEVELOPMENT environment.
# End users should install via:
#   uv tool install git+https://github.com/DoubtfulPrism/research-digest-toolkit.git@main
# See README.md or INSTALL.md for details.

set -e

echo "==========================================="
echo " RDT — Developer Environment Setup"
echo "==========================================="

# Ensure uv is installed
if ! command -v uv &> /dev/null; then
    echo "Error: 'uv' is not installed."
    echo "Install it with:  curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

echo ">> Creating virtual environment and installing in editable mode..."
uv sync --all-extras

echo ""
echo "✅ Development environment ready!"
echo ""
echo "Activate the venv with:"
echo "  source .venv/bin/activate"
echo ""
echo "Then run the TUI with:"
echo "  rdt tui"
echo ""
echo "Or run tests with:"
echo "  pytest tests/"
