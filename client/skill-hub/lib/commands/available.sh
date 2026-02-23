#!/bin/bash
# Available command — список всех доступных скиллов из хаба

SCRIPT_DIR="$(dirname "$(dirname "$(dirname "${BASH_SOURCE[0]}")")")"
source "$SCRIPT_DIR/lib/common.sh"

do_available() {
    local no_sync=false

    # Parse args
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --no-sync)
                no_sync=true
                shift
                ;;
            -*)
                error "Unknown option: $1"
                exit 1
                ;;
        esac
    done

    # Sync registry unless --no-sync is specified
    if [[ "$no_sync" == "false" ]]; then
        source "$SCRIPT_DIR/lib/commands/sync.sh"
        do_sync
        echo ""
    else
        ensure_registry
    fi

    local registry=$(get_registry_path)
    local skills_dir=$(get_skills_dir)

    info "Available skills from hub:"
    echo ""

    python3 << PYTHON
import json
import sys
import os

with open('$registry') as f:
    data = json.load(f)

skills = data.get('skills', {})

if not skills:
    print("No skills available in hub.")
    sys.exit(0)

# Check which skills are installed
skills_dir = '$skills_dir'
installed_skills = set()
if os.path.isdir(skills_dir):
    for name in os.listdir(skills_dir):
        if os.path.isdir(os.path.join(skills_dir, name)) and os.path.isfile(os.path.join(skills_dir, name, 'SKILL.md')):
            installed_skills.add(name)

print(f"{'NAME':<20} {'VERSION':<10} {'STATUS':<12} {'DESCRIPTION'}")
print("-" * 80)

for name in sorted(skills.keys()):
    info = skills[name]
    version = info.get('version', 'N/A')
    desc = info.get('description', '')[:35]

    if name in installed_skills:
        status = "installed"
    else:
        status = "available"

    print(f"{name:<20} {version:<10} {status:<12} {desc}")

print("")
print(f"Total: {len(skills)} skill(s). Use 'hub info <name>' for details.")
print(f"Installed: {len(installed_skills)}, Available to install: {len(skills) - len(installed_skills)}")
PYTHON
}

# If script is run directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    do_available "$@"
fi
