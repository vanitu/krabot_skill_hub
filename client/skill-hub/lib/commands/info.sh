#!/bin/bash
# Info command — информация о скилле

SCRIPT_DIR="$(dirname "$(dirname "$(dirname "${BASH_SOURCE[0]}")")")"
source "$SCRIPT_DIR/lib/common.sh"

do_info() {
    local skill_name="$1"
    
    if [[ -z "$skill_name" ]]; then
        error "Usage: hub info <skill-name>"
        exit 1
    fi
    
    ensure_registry
    
    local registry=$(get_registry_path)
    
    python3 << PYTHON
import json
import sys

with open('$registry') as f:
    data = json.load(f)

skill = data.get('skills', {}).get('$skill_name')

if not skill:
    print(f"Skill '$skill_name' not found in registry.")
    print(f"Run 'hub search' to list available skills.")
    sys.exit(1)

print(f"📦 {skill.get('displayName', '$skill_name')}")
print(f"   Name: {skill.get('name')}")
print(f"   Version: {skill.get('version', 'N/A')}")
print(f"   Author: {skill.get('author', 'N/A')}")
print(f"")
print(f"   {skill.get('description', 'No description')}")
print(f"")

perms = skill.get('permissions', {})
print(f"   Permissions:")
print(f"     Filesystem: {', '.join(perms.get('filesystem', ['none']))}")
print(f"     Network: {'✓' if perms.get('network') else '✗'}")
print(f"     Exec: {'✓' if perms.get('exec') else '✗'}")
print(f"     Sensitive Data: {'✓' if perms.get('sensitiveData') else '✗'}")

tags = skill.get('tags', [])
if tags:
    print(f"")
    print(f"   Tags: {', '.join(tags)}")

# Check if installed
import os
install_path = os.path.expanduser(f"~/krabot/skills/{skill.get('name')}")
if os.path.exists(install_path):
    print(f"")
    print(f"   📍 Installed at: {install_path}")
PYTHON

    # Check installed version
    if is_skill_installed "$skill_name"; then
        local installed_version=$(get_installed_version "$skill_name")
        local registry_version=$(python3 -c "import json; d=json.load(open('$registry')); print(d['skills']['$skill_name']['version'])" 2>/dev/null)
        
        if [[ "$installed_version" != "$registry_version" ]]; then
            warn "Update available: $installed_version → $registry_version"
        else
            success "Up to date (version $installed_version)"
        fi
    fi
}

# If script is run directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    do_info "$@"
fi
