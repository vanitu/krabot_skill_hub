#!/bin/bash
# Skill Hub Client Installer
# Usage: curl -fsSL https://raw.githubusercontent.com/vanitu/krabot_skill_hub/main/install.sh | bash

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

info() { echo -e "${BLUE}ℹ $1${NC}"; }
success() { echo -e "${GREEN}✓ $1${NC}"; }
warn() { echo -e "${YELLOW}⚠ $1${NC}"; }
error() { echo -e "${RED}✗ $1${NC}"; }

# Default installation path
DEFAULT_INSTALL_DIR="${SKILL_HUB_INSTALL_DIR:-$HOME/.openclaw/workspace/skills}"
INSTALL_DIR="$DEFAULT_INSTALL_DIR"
HUB_URL="https://github.com/vanitu/krabot_skill_hub"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --path)
            INSTALL_DIR="$2"
            shift 2
            ;;
        --help|-h)
            echo "Skill Hub Client Installer"
            echo ""
            echo "Usage:"
            echo "  curl -fsSL https://raw.githubusercontent.com/vanitu/krabot_skill_hub/main/install.sh | bash"
            echo "  curl -fsSL ... | bash -s -- --path /custom/path"
            echo ""
            echo "Options:"
            echo "  --path <dir>    Installation directory (default: ~/.openclaw/workspace/skills)"
            echo "  --help          Show this help"
            exit 0
            ;;
        *)
            error "Unknown option: $1"
            exit 1
            ;;
    esac
done

HUB_ROOT="$INSTALL_DIR/skill-hub"

echo "🦀 Skill Hub Client Installer"
echo ""

# Check dependencies
info "Checking dependencies..."
if ! command -v curl &> /dev/null; then
    error "curl is required but not installed"
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    warn "python3 not found. Some features may not work."
fi

success "Dependencies OK"

# Create directories
info "Creating directories at $HUB_ROOT..."
mkdir -p "$HUB_ROOT"/{bin,lib/commands,.cache}

# Download files
info "Downloading Skill Hub Client..."

curl -fsSL "$HUB_URL/raw/main/client/skill-hub/bin/hub" -o "$HUB_ROOT/bin/hub"
chmod +x "$HUB_ROOT/bin/hub"

curl -fsSL "$HUB_URL/raw/main/client/skill-hub/lib/common.sh" -o "$HUB_ROOT/lib/common.sh"

for cmd in sync search info install update remove list; do
    curl -fsSL "$HUB_URL/raw/main/client/skill-hub/lib/commands/${cmd}.sh" -o "$HUB_ROOT/lib/commands/${cmd}.sh"
done

# Create config
cat > "$HUB_ROOT/config.json" << CONFIG
{
  "hub": {
    "url": "$HUB_URL",
    "branch": "main"
  },
  "installed": {}
}
CONFIG

success "Files downloaded"

# Set permissions
info "Setting permissions..."
chmod -R u+rw "$HUB_ROOT"
success "Permissions set"

# Test installation
info "Testing installation..."
if "$HUB_ROOT/bin/hub" sync; then
    success "Installation successful!"
else
    error "Installation test failed"
    exit 1
fi

echo ""
echo "🎉 Skill Hub Client installed!"
echo ""
echo "Location: $HUB_ROOT"
echo ""
echo "Usage:"
echo "  $HUB_ROOT/bin/hub search"
echo "  $HUB_ROOT/bin/hub install weather"
echo ""
echo "To add to PATH, add this to your shell config:"
echo "  export PATH=\"$HUB_ROOT/bin:\$PATH\""
echo ""
echo "Or set environment variables:"
echo "  export SKILL_HUB_ROOT=\"$HUB_ROOT\""
echo "  export SKILL_HUB_SKILLS=\"$INSTALL_DIR\""
