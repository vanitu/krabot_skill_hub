#!/bin/bash
# Install command — установка скилла

SCRIPT_DIR="$(dirname "$(dirname "$(dirname "${BASH_SOURCE[0]}")")")"
source "$SCRIPT_DIR/lib/common.sh"

do_install() {
    local skill_name=""
    local version=""
    local force=false
    
    # Parse args
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --version)
                version="$2"
                shift 2
                ;;
            --force)
                force=true
                shift
                ;;
            -*)
                error "Unknown option: $1"
                exit 1
                ;;
            *)
                skill_name="$1"
                shift
                ;;
        esac
    done
    
    if [[ -z "$skill_name" ]]; then
        error "Usage: hub install <skill-name> [--version x.x.x]"
        exit 1
    fi
    
    ensure_registry
    
    local registry=$(get_registry_path)
    local skills_dir=$(get_skills_dir)
    local hub_url=$(get_hub_url)
    local branch=$(get_hub_branch)
    
    # Check if skill exists in registry
    local skill_info=$(get_skill_from_registry "$skill_name")
    if [[ -z "$skill_info" ]]; then
        error "Skill '$skill_name' not found in registry"
        echo "Run 'hub search' to find available skills"
        exit 1
    fi
    
    # Check if already installed
    if is_skill_installed "$skill_name"; then
        if [[ "$force" == "true" ]]; then
            warn "Skill '$skill_name' is already installed, reinstalling..."
        else
            warn "Skill '$skill_name' is already installed"
            echo "Use 'hub update $skill_name' to update or --force to reinstall"
            exit 0
        fi
    fi
    
    # Get skill details
    local skill_version=$(echo "$skill_info" | python3 -c "import json,sys; print(json.load(sys.stdin)['version'])")
    local skill_author=$(echo "$skill_info" | python3 -c "import json,sys; print(json.load(sys.stdin).get('author', 'unknown'))")
    local skill_path=$(echo "$skill_info" | python3 -c "import json,sys; print(json.load(sys.stdin)['path'])")
    local perms_exec=$(echo "$skill_info" | python3 -c "import json,sys; print(json.load(sys.stdin).get('permissions',{}).get('exec',False))")
    local perms_sensitive=$(echo "$skill_info" | python3 -c "import json,sys; print(json.load(sys.stdin).get('permissions',{}).get('sensitiveData',False))")
    
    info "Installing $skill_name v$skill_version by $skill_author..."
    
    # Warning for dangerous permissions
    if [[ "$perms_exec" == "True" ]] || [[ "$perms_sensitive" == "True" ]]; then
        warn "⚠️  This skill requires elevated permissions:"
        [[ "$perms_exec" == "True" ]] && echo "   - Shell execution (exec: true)"
        [[ "$perms_sensitive" == "True" ]] && echo "   - Access to sensitive data (sensitiveData: true)"
        echo ""
        read -p "Continue with installation? [y/N] " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            info "Installation cancelled"
            exit 0
        fi
    fi
    
    # Create skill directory
    local install_path="$skills_dir/$skill_name"
    mkdir -p "$install_path"
    
    # Download skill files
    local base_url="$hub_url/raw/$branch/$skill_path"
    
    info "Downloading from $base_url..."
    
    # Try to download SKILL.md and manifest.json
    local files=("SKILL.md" "manifest.json")
    local failed=false
    
    for file in "${files[@]}"; do
        local url="$base_url/$file"
        local output="$install_path/$file"
        
        if command -v curl &> /dev/null; then
            if ! curl -fsSL "$url" -o "$output" 2>/dev/null; then
                error "Failed to download $file"
                failed=true
                break
            fi
        elif command -v wget &> /dev/null; then
            if ! wget -q "$url" -O "$output" 2>/dev/null; then
                error "Failed to download $file"
                failed=true
                break
            fi
        fi
    done
    
    if [[ "$failed" == "true" ]]; then
        rm -rf "$install_path"
        error "Installation failed"
        exit 1
    fi
    
    # TODO: Download additional files (scripts/, lib/, etc.)
    # For MVP, we just download SKILL.md and manifest.json
    
    # Update config
    local config_file=$(get_config_file)
    if [[ -f "$config_file" ]]; then
        python3 << PYTHON
import json
import os
from datetime import datetime

config_path = '$config_file'
with open(config_path) as f:
    config = json.load(f)

if 'installed' not in config:
    config['installed'] = {}

config['installed']['$skill_name'] = {
    'version': '$skill_version',
    'installedAt': datetime.utcnow().isoformat() + 'Z',
    'path': '$install_path'
}

with open(config_path, 'w') as f:
    json.dump(config, f, indent=2)
PYTHON
    fi
    
    success "Skill '$skill_name' installed successfully!"
    echo ""
    echo "Location: $install_path"
    echo "Documentation: $install_path/SKILL.md"
}

# If script is run directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    do_install "$@"
fi
