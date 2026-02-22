#!/bin/bash
# Common functions for Skill Hub Client

# Expand tilde in paths
expand_path() {
    local path="$1"
    echo "${path/#\~/$HOME}"
}

# Get config directory
get_config_dir() {
    local dir="${SKILL_HUB_CONFIG:-~/krabot/skills/skill-hub}"
    expand_path "$dir"
}

# Get config file path
get_config_file() {
    echo "$(get_config_dir)/config.json"
}

# Get cache directory
get_cache_dir() {
    local dir="${SKILL_HUB_CACHE:-~/krabot/skills/.hub-cache}"
    expand_path "$dir"
}

# Get registry path
get_registry_path() {
    echo "$(get_cache_dir)/registry.json"
}

# Get skills install path
get_skills_dir() {
    local dir="${SKILL_HUB_SKILLS:-~/krabot/skills}"
    expand_path "$dir"
}

# Read config value (using Python for JSON parsing)
get_config() {
    local key="$1"
    local config_file="$(get_config_file)"
    
    if [[ -f "$config_file" ]]; then
        python3 -c "import json,sys; d=json.load(open('$config_file')); print(d$key)" 2>/dev/null || echo ""
    else
        echo ""
    fi
}

# Get hub URL
get_hub_url() {
    local url=$(get_config "['hub']['url']")
    echo "${url:-https://github.com/vanitu/krabot_skill_hub}"
}

# Get hub branch
get_hub_branch() {
    local branch=$(get_config "['hub']['branch']")
    echo "${branch:-main}"
}

# Check if registry exists and is valid
ensure_registry() {
    local registry="$(get_registry_path)"
    
    if [[ ! -f "$registry" ]]; then
        echo "Registry not found. Running sync..."
        source "$(dirname "${BASH_SOURCE[0]}")/commands/sync.sh"
        do_sync
    fi
    
    if [[ ! -f "$registry" ]]; then
        echo "Error: Failed to load registry"
        exit 1
    fi
}

# Get skill info from registry
get_skill_from_registry() {
    local skill_name="$1"
    local registry="$(get_registry_path)"
    
    python3 -c "
import json
with open('$registry') as f:
    data = json.load(f)
    skill = data.get('skills', {}).get('$skill_name')
    if skill:
        print(json.dumps(skill))
" 2>/dev/null
}

# List all skills from registry
list_skills_from_registry() {
    local registry="$(get_registry_path)"
    
    python3 -c "
import json
with open('$registry') as f:
    data = json.load(f)
    for name, info in data.get('skills', {}).items():
        print(f\"{name}|{info.get('displayName', name)}|{info.get('description', 'N/A')}|{info.get('version', 'N/A')}\")
" 2>/dev/null
}

# Check if skill is installed
is_skill_installed() {
    local skill_name="$1"
    local skill_dir="$(get_skills_dir)/$skill_name"
    
    [[ -d "$skill_dir" ]]
}

# Get installed skill version
get_installed_version() {
    local skill_name="$1"
    local skill_manifest="$(get_skills_dir)/$skill_name/manifest.json"
    
    if [[ -f "$skill_manifest" ]]; then
        python3 -c "import json; print(json.load(open('$skill_manifest'))['version'])" 2>/dev/null
    else
        echo "unknown"
    fi
}

# Colors for output (if terminal)
if [[ -t 1 ]]; then
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    BLUE='\033[0;34m'
    NC='\033[0m' # No Color
else
    RED=''
    GREEN=''
    YELLOW=''
    BLUE=''
    NC=''
fi

# Print colored output
info() { echo -e "${BLUE}ℹ $1${NC}"; }
success() { echo -e "${GREEN}✓ $1${NC}"; }
warn() { echo -e "${YELLOW}⚠ $1${NC}"; }
error() { echo -e "${RED}✗ $1${NC}"; }
