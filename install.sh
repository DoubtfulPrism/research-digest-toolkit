#!/usr/bin/env bash
# Research Digest Toolkit Installer

set -e

echo "==========================================="
echo " Installing Research Digest Toolkit (RDT)"
echo "==========================================="

# Ensure uv is installed
if ! command -v uv &> /dev/null; then
    echo "Error: 'uv' is not installed. Please install it first (e.g., pip install uv)."
    exit 1
fi

echo ">> Installing RDT package and dependencies locally via uv..."
# Install the project and its dependencies
uv pip install -e .[dev]

# Set up the wrapper script
LOCAL_BIN="$HOME/.local/bin"
WRAPPER_SCRIPT="$LOCAL_BIN/rdt"

echo ">> Setting up global command 'rdt' in $LOCAL_BIN..."
mkdir -p "$LOCAL_BIN"

# The wrapper simply uses the uv-managed venv's python to run the cli
cat << 'EOF' > "$WRAPPER_SCRIPT"
#!/usr/bin/env bash
# Wrapper to run RDT without activating the venv manually

# Resolve the absolute path to the directory containing this project
PROJECT_DIR="$(cd "$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")/../../Documents/AIProjectWork/ResearchTUI" && pwd 2>/dev/null)"
if [ -z "$PROJECT_DIR" ]; then
    # Fallback to current directory assuming it's run from there, or hardcoded path
    PROJECT_DIR="$PWD"
fi

# Hardcode the project dir to ensure reliability since we are installing it locally
PROJECT_DIR="/home/doug/Documents/AIProjectWork/ResearchTUI"

VENV_PYTHON="$PROJECT_DIR/.venv/bin/python"

if [ ! -x "$VENV_PYTHON" ]; then
    echo "Error: RDT virtual environment not found at $PROJECT_DIR/.venv"
    echo "Please run install.sh from the project root."
    exit 1
fi

# Pass all arguments to the CLI entrypoint
exec "$VENV_PYTHON" -m rdt.cli.main "$@"
EOF

chmod +x "$WRAPPER_SCRIPT"

echo ""
echo "✅ Installation Complete!"
echo "The 'rdt' command has been installed to $LOCAL_BIN/rdt."
echo "Ensure that $LOCAL_BIN is in your PATH."
echo "You can now run 'rdt --help' or 'rdt tui' from anywhere!"
