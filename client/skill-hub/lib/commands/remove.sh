#!/bin/bash
# Remove command — удаление скилла

SCRIPT_DIR="$(dirname "$(dirname "$(dirname "${BASH_SOURCE[0]}")")")"
source "$SCRIPT_DIR/lib/common.sh"

do_remove() {
    local skill_name="$1"
    local force=false
    
    # Parse args
    while [[ $# -gt 0 ]]; do
        case "$1" in
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
        error "Usage: hub remove <skill-name> [--force]"
        exit 1
    fi
    
    if ! is_skill_installed "$skill_name"; then
        error "Skill '$skill_name' is not installed"
        exit 1
    fi
    
    local skills_dir=$(get_skills_dir)
    local install_path="$skills_dir/$skill_name"
    
    info "Removing skill '$skill_name'..."
    
    if [[ "$force" != "true" ]]; then
        read -p "Are you sure? [y/N] " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            info "Removal cancelled"
            exit 0
        fi
    fi
    
    # Remove directory
    rm -rf "$install_path"
    
    # Update config
    local config_file=$(get_config_file)
    if [[ -f "$config_file" ]]; then
        python3 << PYTHON
import json

config_path = '$config_file'
with open(config_path) as f:
    config = json.load(f)

if 'installed' in config and '$skill_name' in config['installed']:
    del config['installed']['$skill_name']
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
PYTHON
    fi
    
    success "Skill '$skill_name' removed"
}

# If script is run directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    do_remove "$@"
fi
