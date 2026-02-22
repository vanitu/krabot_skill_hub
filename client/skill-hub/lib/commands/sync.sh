#!/bin/bash
# Sync command — обновление registry из хаба

SCRIPT_DIR="$(dirname "$(dirname "$(dirname "${BASH_SOURCE[0]}")")")"
source "$SCRIPT_DIR/lib/common.sh"

do_sync() {
    local hub_url=$(get_hub_url)
    local branch=$(get_hub_branch)
    local cache_dir=$(get_cache_dir)
    local registry_url="$hub_url/raw/$branch/registry.json"
    
    info "Syncing registry from $hub_url..."
    
    # Create cache dir if needed
    mkdir -p "$cache_dir"
    
    # Download registry.json
    local temp_registry="$cache_dir/registry.json.tmp"
    
    if command -v curl &> /dev/null; then
        curl -fsSL "$registry_url" -o "$temp_registry" 2>/dev/null
    elif command -v wget &> /dev/null; then
        wget -q "$registry_url" -O "$temp_registry" 2>/dev/null
    else
        error "Neither curl nor wget found"
        exit 1
    fi
    
    if [[ -f "$temp_registry" && -s "$temp_registry" ]]; then
        # Validate JSON
        if python3 -m json.tool "$temp_registry" > /dev/null 2>&1; then
            mv "$temp_registry" "$cache_dir/registry.json"
            success "Registry updated successfully"
            
            # Show stats
            local count=$(python3 -c "import json; d=json.load(open('$cache_dir/registry.json')); print(len(d.get('skills', {})))" 2>/dev/null)
            info "Available skills: $count"
        else
            rm -f "$temp_registry"
            error "Invalid JSON received"
            exit 1
        fi
    else
        rm -f "$temp_registry"
        error "Failed to download registry"
        exit 1
    fi
}

# If script is run directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    do_sync "$@"
fi
