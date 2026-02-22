#!/bin/bash
# List command — список установленных скиллов

SCRIPT_DIR="$(dirname "$(dirname "$(dirname "${BASH_SOURCE[0]}")")")"
source "$SCRIPT_DIR/lib/common.sh"

do_list() {
    local show_outdated=false
    
    # Parse args
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --outdated)
                show_outdated=true
                shift
                ;;
            -*)
                error "Unknown option: $1"
                exit 1
                ;;
        esac
    done
    
    local skills_dir=$(get_skills_dir)
    
    if [[ ! -d "$skills_dir" ]]; then
        info "No skills directory found"
        exit 0
    fi
    
    # Find installed skills (directories with SKILL.md)
    local installed=()
    for dir in "$skills_dir"/*/; do
        if [[ -f "$dir/SKILL.md" ]]; then
            local name=$(basename "$dir")
            installed+=("$name")
        fi
    done
    
    if [[ ${#installed[@]} -eq 0 ]]; then
        info "No skills installed"
        echo "Run 'hub search' to find skills, 'hub install <name>' to install"
        exit 0
    fi
    
    info "Installed skills:"
    echo ""
    
    ensure_registry 2>/dev/null || true
    local registry=$(get_registry_path)
    local registry_exists=false
    [[ -f "$registry" ]] && registry_exists=true
    
    printf "%-20s %-12s %-12s %-10s\n" "NAME" "INSTALLED" "LATEST" "STATUS"
    echo "--------------------------------------------------------------------------------"
    
    local outdated_count=0
    
    for skill_name in "${installed[@]}"; do
        local installed_version=$(get_installed_version "$skill_name")
        local latest_version="N/A"
        local status="✓"
        
        if [[ "$registry_exists" == "true" ]]; then
            latest_version=$(python3 -c "import json; d=json.load(open('$registry')); print(d.get('skills', {}).get('$skill_name', {}).get('version', 'N/A'))" 2>/dev/null)
            
            if [[ "$latest_version" != "N/A" && "$installed_version" != "$latest_version" ]]; then
                status="⬆ update"
                ((outdated_count++))
            fi
        fi
        
        if [[ "$show_outdated" == "false" ]] || [[ "$status" == "⬆ update" ]]; then
            printf "%-20s %-12s %-12s %-10s\n" "$skill_name" "$installed_version" "$latest_version" "$status"
        fi
    done
    
    echo ""
    if [[ $outdated_count -gt 0 ]]; then
        info "$outdated_count skill(s) have updates available"
        echo "Run 'hub list --outdated' to see only outdated"
        echo "Run 'hub update <name>' to update a skill"
    else
        success "All skills are up to date"
    fi
}

# If script is run directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    do_list "$@"
fi
