#!/bin/bash
# Update command — обновление скилла

SCRIPT_DIR="$(dirname "$(dirname "$(dirname "${BASH_SOURCE[0]}")")")"
source "$SCRIPT_DIR/lib/common.sh"

do_update() {
    local skill_name="$1"
    
    if [[ -z "$skill_name" ]]; then
        error "Usage: hub update <skill-name>"
        exit 1
    fi
    
    ensure_registry
    
    if ! is_skill_installed "$skill_name"; then
        error "Skill '$skill_name' is not installed"
        echo "Run 'hub install $skill_name' to install it"
        exit 1
    fi
    
    local registry=$(get_registry_path)
    local skills_dir=$(get_skills_dir)
    local install_path="$skills_dir/$skill_name"
    
    # Check if update available
    local installed_version=$(get_installed_version "$skill_name")
    local latest_version=$(python3 -c "import json; d=json.load(open('$registry')); print(d.get('skills', {}).get('$skill_name', {}).get('version', 'N/A'))" 2>/dev/null)
    
    if [[ "$latest_version" == "N/A" ]]; then
        error "Skill '$skill_name' not found in registry"
        exit 1
    fi
    
    if [[ "$installed_version" == "$latest_version" ]]; then
        success "Skill '$skill_name' is already up to date (v$installed_version)"
        exit 0
    fi
    
    info "Updating $skill_name: v$installed_version → v$latest_version"
    
    # Backup old version
    local backup_path="${install_path}.backup.$(date +%s)"
    cp -r "$install_path" "$backup_path"
    
    # Re-install (remove and install fresh)
    source "$SCRIPT_DIR/lib/commands/remove.sh"
    do_remove "$skill_name" --force
    
    source "$SCRIPT_DIR/lib/commands/install.sh"
    if do_install "$skill_name"; then
        rm -rf "$backup_path"
        success "Skill '$skill_name' updated to v$latest_version"
    else
        # Restore backup
        mv "$backup_path" "$install_path"
        error "Update failed, restored previous version"
        exit 1
    fi
}

# If script is run directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    do_update "$@"
fi
