#!/bin/bash
# Search command — поиск скиллов

SCRIPT_DIR="$(dirname "$(dirname "$(dirname "${BASH_SOURCE[0]}")")")"
source "$SCRIPT_DIR/lib/common.sh"

do_search() {
    local query=""
    local tag=""
    
    # Parse args
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --tag)
                tag="$2"
                shift 2
                ;;
            -*)
                error "Unknown option: $1"
                exit 1
                ;;
            *)
                query="$1"
                shift
                ;;
        esac
    done
    
    ensure_registry
    
    local registry=$(get_registry_path)
    
    info "Searching for skills..."
    echo ""
    
    python3 << PYTHON
import json
import sys

with open('$registry') as f:
    data = json.load(f)

skills = data.get('skills', {})
query = '$query'.lower()
tag = '$tag'.lower()

found = []
for name, info in skills.items():
    # Filter by query
    if query:
        searchable = f"{name} {info.get('displayName', '')} {info.get('description', '')}".lower()
        if query not in searchable:
            continue
    
    # Filter by tag
    if tag:
        tags = [t.lower() for t in info.get('tags', [])]
        if tag not in tags:
            continue
    
    found.append((name, info))

if not found:
    print("No skills found matching your criteria.")
    sys.exit(0)

print(f"{'NAME':<20} {'VERSION':<10} {'DESCRIPTION'}")
print("-" * 70)
for name, info in found:
    display = info.get('displayName', name)
    version = info.get('version', 'N/A')
    desc = info.get('description', '')[:40]
    print(f"{name:<20} {version:<10} {desc}")

print("")
print(f"Found {len(found)} skill(s). Use 'hub info <name>' for details.")
PYTHON
}

# If script is run directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    do_search "$@"
fi
