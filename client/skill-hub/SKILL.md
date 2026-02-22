# Skill Hub Client

Пакетный менеджер для скиллов Krabot. Управляет установкой, обновлением и удалением скиллов из приватного хаба.

## Configuration

Создайте `~/krabot/skills/skill-hub/config.json`:

```json
{
  "hub": {
    "url": "https://github.com/vanitu/krabot_skill_hub",
    "token": "${SKILLS_HUB_TOKEN}",
    "branch": "main",
    "localCache": "~/krabot/skills/.hub-cache"
  },
  "installed": {
    "weather": { "version": "1.0.0", "installedAt": "2025-01-20T10:00:00Z" }
  }
}
```

## Commands

### hub search <query> [--tag <tag>]

Поиск скиллов в registry:
```
hub search weather
hub search --tag monitoring
```

### hub info <skill-name>

Информация о скилле:
```
hub info weather
```

### hub install <skill-name> [--version x.x.x]

Установка скилла:
```
hub install weather
hub install system-monitor
hub install telegram-helper --version 1.0.0
```

### hub update <skill-name>

Обновление скилла:
```
hub update weather
```

### hub remove <skill-name>

Удаление скилла:
```
hub remove weather
```

### hub list [--outdated]

Список установленных скиллов:
```
hub list
hub list --outdated
```

### hub sync

Обновление локального кэша registry.json:
```
hub sync
```

## Implementation

Клиент реализован как набор shell-скриптов:
- `bin/hub` — main entry point
- `lib/` — common functions
- `lib/commands/` — команды (search, install, etc.)
