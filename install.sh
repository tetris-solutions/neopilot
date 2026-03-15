#!/usr/bin/env bash
# ============================================================================
# NeoPilot Installer
# One-command setup for macOS users with Claude Desktop
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/tetris-solutions/neopilot/main/install.sh | bash
#
# Or clone + run locally:
#   git clone https://github.com/tetris-solutions/neopilot.git
#   cd neopilot && bash install.sh
# ============================================================================

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

info()    { echo -e "${BLUE}ℹ${NC}  $1"; }
success() { echo -e "${GREEN}✅${NC} $1"; }
warn()    { echo -e "${YELLOW}⚠️${NC}  $1"; }
error()   { echo -e "${RED}❌${NC} $1"; exit 1; }

echo ""
echo -e "${BLUE}╔══════════════════════════════════════╗${NC}"
echo -e "${BLUE}║       NeoPilot Installer             ║${NC}"
echo -e "${BLUE}║  NeoDash AI Connector for Claude     ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════╝${NC}"
echo ""

# -------------------------------------------------------------------
# 1. Check prerequisites
# -------------------------------------------------------------------
info "Checking prerequisites..."

# Python 3.11+
if command -v python3 &>/dev/null; then
    PY=$(command -v python3)
    PY_VERSION=$($PY --version 2>&1 | awk '{print $2}')
    PY_MAJOR=$(echo "$PY_VERSION" | cut -d. -f1)
    PY_MINOR=$(echo "$PY_VERSION" | cut -d. -f2)
    if [ "$PY_MAJOR" -lt 3 ] || { [ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -lt 11 ]; }; then
        error "Python 3.11+ is required (found $PY_VERSION). Please upgrade Python."
    fi
    success "Python $PY_VERSION found at $PY"
else
    error "Python 3 not found. Install it from https://www.python.org/downloads/"
fi

# Git
if ! command -v git &>/dev/null; then
    error "Git not found. Install it from https://git-scm.com/"
fi
success "Git found"

# -------------------------------------------------------------------
# 2. Clone or update the repo
# -------------------------------------------------------------------
INSTALL_DIR="$HOME/.neopilot/app"

if [ -d "$INSTALL_DIR/.git" ]; then
    info "NeoPilot already installed. Updating..."
    cd "$INSTALL_DIR"
    git pull --ff-only origin main 2>/dev/null || warn "Could not auto-update. Try: cd $INSTALL_DIR && git pull"
    success "Updated to latest version"
else
    info "Installing NeoPilot to $INSTALL_DIR ..."
    mkdir -p "$(dirname "$INSTALL_DIR")"
    # If running from inside the repo, copy; otherwise clone
    if [ -f "$(dirname "$0")/pyproject.toml" ] 2>/dev/null; then
        SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
        if [ "$SCRIPT_DIR" != "$INSTALL_DIR" ]; then
            git clone "$SCRIPT_DIR" "$INSTALL_DIR"
        fi
    else
        git clone https://github.com/tetris-solutions/neopilot.git "$INSTALL_DIR"
    fi
    success "Cloned NeoPilot"
fi

cd "$INSTALL_DIR"

# -------------------------------------------------------------------
# 3. Set up virtual environment
# -------------------------------------------------------------------
VENV_DIR="$INSTALL_DIR/.venv"

if [ ! -d "$VENV_DIR" ]; then
    info "Creating virtual environment..."
    $PY -m venv "$VENV_DIR"
    success "Virtual environment created"
else
    info "Virtual environment already exists"
fi

info "Installing dependencies..."
"$VENV_DIR/bin/pip" install --quiet --upgrade pip
"$VENV_DIR/bin/pip" install --quiet -e .
success "Dependencies installed"

# Get the installed version
NEOPILOT_VERSION=$("$VENV_DIR/bin/python" -c "from neopilot import __version__; print(__version__)" 2>/dev/null || echo "unknown")
success "NeoPilot v$NEOPILOT_VERSION ready"

# -------------------------------------------------------------------
# 4. Configure Claude Desktop
# -------------------------------------------------------------------
CLAUDE_CONFIG_DIR="$HOME/Library/Application Support/Claude"
CLAUDE_CONFIG="$CLAUDE_CONFIG_DIR/claude_desktop_config.json"

PYTHON_PATH="$VENV_DIR/bin/python"

if [ ! -d "$CLAUDE_CONFIG_DIR" ]; then
    warn "Claude Desktop config directory not found. Is Claude Desktop installed?"
    warn "You can manually add NeoPilot later. See: $INSTALL_DIR/docs/SETUP.md"
else
    info "Configuring Claude Desktop..."

    if [ -f "$CLAUDE_CONFIG" ]; then
        # Check if neopilot is already configured
        if grep -q '"neopilot"' "$CLAUDE_CONFIG" 2>/dev/null; then
            # Update the existing config (just update the python path)
            info "NeoPilot already configured in Claude Desktop"
            # Use python to safely update the JSON
            "$VENV_DIR/bin/python" -c "
import json, sys
with open('$CLAUDE_CONFIG', 'r') as f:
    config = json.load(f)
config.setdefault('mcpServers', {})
config['mcpServers']['neopilot'] = {
    'command': '$PYTHON_PATH',
    'args': ['-m', 'neopilot.server']
}
with open('$CLAUDE_CONFIG', 'w') as f:
    json.dump(config, f, indent=2)
"
            success "Updated NeoPilot config in Claude Desktop"
        else
            # Add neopilot to existing config
            "$VENV_DIR/bin/python" -c "
import json
with open('$CLAUDE_CONFIG', 'r') as f:
    config = json.load(f)
config.setdefault('mcpServers', {})
config['mcpServers']['neopilot'] = {
    'command': '$PYTHON_PATH',
    'args': ['-m', 'neopilot.server']
}
with open('$CLAUDE_CONFIG', 'w') as f:
    json.dump(config, f, indent=2)
"
            success "Added NeoPilot to Claude Desktop config"
        fi
    else
        # Create new config
        "$VENV_DIR/bin/python" -c "
import json
config = {
    'mcpServers': {
        'neopilot': {
            'command': '$PYTHON_PATH',
            'args': ['-m', 'neopilot.server']
        }
    }
}
with open('$CLAUDE_CONFIG', 'w') as f:
    json.dump(config, f, indent=2)
"
        success "Created Claude Desktop config with NeoPilot"
    fi
fi

# -------------------------------------------------------------------
# 5. Done!
# -------------------------------------------------------------------
echo ""
echo -e "${GREEN}╔══════════════════════════════════════╗${NC}"
echo -e "${GREEN}║    NeoPilot installed successfully!  ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════╝${NC}"
echo ""
echo "Next steps:"
echo "  1. Restart Claude Desktop (quit and reopen)"
echo "  2. In Claude, say: \"Connect to my NeoDash instance 'yourslug' with token 'yourtoken'\""
echo ""
echo "To update later, run:"
echo "  cd $INSTALL_DIR && git pull && .venv/bin/pip install -e ."
echo ""
echo "Installed at: $INSTALL_DIR"
echo "Python:       $PYTHON_PATH"
echo ""
