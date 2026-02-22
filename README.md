# Krabot Skill Hub 🦀

Public skill repository for OpenClaw agents — centralized skill registry with universal package manager.

## Universal Installation (Any Agent)

### One-liner install:

```bash
# Create skill-hub directory anywhere (e.g., in your skills folder)
mkdir -p ~/skills/skill-hub/{bin,lib/commands}
cd ~/skills/skill-hub

# Download client files
curl -fsSL https://raw.githubusercontent.com/vanitu/krabot_skill_hub/main/client/skill-hub/bin/hub -o bin/hub && chmod +x bin/hub
curl -fsSL https://raw.githubusercontent.com/vanitu/krabot_skill_hub/main/client/skill-hub/lib/common.sh -o lib/common.sh

for cmd in sync search info install update remove list; do
  curl -fsSL "https://raw.githubusercontent.com/vanitu/krabot_skill_hub/main/client/skill-hub/lib/commands/${cmd}.sh" -o "lib/commands/${cmd}.sh"
done

# Create config
echo '{"hub":{"url":"https://github.com/vanitu/krabot_skill_hub","branch":"main"},"installed":{}}' > config.json

echo "✓ Skill Hub installed!"
```

### Or step by step:

```bash
# 1. Choose location (anywhere)
INSTALL_DIR="$HOME/skills/skill-hub"
mkdir -p "$INSTALL_DIR"

# 2. Download client
curl -fsSL https://github.com/vanitu/krabot_skill_hub/archive/refs/heads/main.tar.gz | \
  tar -xz --strip=3 -C "$INSTALL_DIR" "krabot_skill_hub-main/client/skill-hub/"

# 3. Use it
"$INSTALL_DIR/bin/hub" sync
"$INSTALL_DIR/bin/hub" search
```

## Usage

```bash
# Add to PATH (optional)
export PATH="/path/to/skill-hub/bin:$PATH"

# Or use full path
~/skills/skill-hub/bin/hub sync
~/skills/skill-hub/bin/hub search
~/skills/skill-hub/bin/hub install weather
```

### Commands

| Command | Description |
|---------|-------------|
| `hub sync` | Update registry from hub |
| `hub search [query]` | Search available skills |
| `hub info <skill>` | Show skill details |
| `hub install <skill>` | Install a skill |
| `hub update <skill>` | Update a skill |
| `hub remove <skill>` | Remove a skill |
| `hub list [--outdated]` | List installed skills |

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SKILL_HUB_ROOT` | Path to skill-hub installation | Auto-detected |
| `SKILL_HUB_SKILLS` | Where to install skills | Parent of hub root |

## Structure

```
skill-hub/              # Can be anywhere
├── bin/hub            # CLI entry point
├── lib/
│   ├── common.sh      # Shared functions
│   └── commands/      # Command implementations
├── .cache/            # Registry cache
│   └── registry.json
└── config.json        # Local config
```

Skills are installed to the parent directory by default:
```
skills/
├── skill-hub/         # This client
├── weather/           # Installed skill
├── system-monitor/    # Installed skill
└── ...
```

## Adding Skills to Hub

1. Create `skills/your-skill/SKILL.md` and `manifest.json`
2. Update `registry.json`
3. Send PR or push to your fork

## License

MIT — free for any OpenClaw agent 🔓
