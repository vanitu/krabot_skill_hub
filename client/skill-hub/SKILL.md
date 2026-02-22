# Skill Hub Client

Universal package manager for OpenClaw agent skills. Install, update, and remove skills from any skill hub.

## Installation

Install anywhere:

```bash
mkdir -p ~/skills/skill-hub/{bin,lib/commands}
cd ~/skills/skill-hub

# Download client
curl -fsSL https://raw.githubusercontent.com/vanitu/krabot_skill_hub/main/client/skill-hub/bin/hub -o bin/hub
chmod +x bin/hub

curl -fsSL https://raw.githubusercontent.com/vanitu/krabot_skill_hub/main/client/skill-hub/lib/common.sh -o lib/common.sh

for cmd in sync search info install update remove list; do
  curl -fsSL "https://raw.githubusercontent.com/vanitu/krabot_skill_hub/main/client/skill-hub/lib/commands/${cmd}.sh" -o "lib/commands/${cmd}.sh"
done

# Create config
echo '{"hub":{"url":"https://github.com/vanitu/krabot_skill_hub","branch":"main"},"installed":{}}' > config.json
```

## Configuration

Config file `config.json` in the skill-hub directory:

```json
{
  "hub": {
    "url": "https://github.com/vanitu/krabot_skill_hub",
    "branch": "main"
  },
  "installed": {
    "weather": { "version": "1.0.0", "installedAt": "2025-01-20T10:00:00Z" }
  }
}
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SKILL_HUB_ROOT` | Path to skill-hub installation | Auto-detected |
| `SKILL_HUB_SKILLS` | Where to install skills | Parent of hub root |

## Commands

### hub search <query> [--tag <tag>]

Search skills in registry:
```
hub search weather
hub search --tag monitoring
```

### hub info <skill-name>

Show skill details:
```
hub info weather
```

### hub install <skill-name> [--version x.x.x]

Install a skill:
```
hub install weather
hub install system-monitor
hub install telegram-helper --version 1.0.0
```

### hub update <skill-name>

Update a skill:
```
hub update weather
```

### hub remove <skill-name>

Remove a skill:
```
hub remove weather
```

### hub list [--outdated]

List installed skills:
```
hub list
hub list --outdated
```

### hub sync

Update local registry cache:
```
hub sync
```

## Usage

```bash
# Add to PATH (optional)
export PATH="$HOME/skills/skill-hub/bin:$PATH"

# Use
hub sync
hub search
hub install weather
```

## Implementation

Client is implemented as shell scripts:
- `bin/hub` — main entry point
- `lib/common.sh` — shared functions
- `lib/commands/` — command implementations (search, install, etc.)

## Custom Hub

To use your own skill hub, fork the repository and update config:

```json
{
  "hub": {
    "url": "https://github.com/YOUR_USERNAME/krabot_skill_hub",
    "branch": "main"
  }
}
```
