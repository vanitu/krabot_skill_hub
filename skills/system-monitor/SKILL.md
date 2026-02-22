# System Monitor Skill

System monitoring for Mac/Linux — CPU, RAM, Disk, Load Average, Docker, процессы.

## Quick Commands

```bash
# Полный статус системы
~/krabot/skills/system-monitor/status.sh

# Запустить мониторинг (проверка thresholds)
~/krabot/skills/system-monitor/monitor.sh

# Отправить дневной отчёт
~/krabot/skills/system-monitor/daily_report.sh
```

## Features

- **CPU**: Load average (1/5/15 min)
- **RAM**: Used/Total, percentage
- **Disk**: Root partition usage
- **Top Processes**: По CPU и памяти
- **Docker**: Running containers count
- **Alerts**: Telegram notifications when thresholds exceeded

## Thresholds (configurable)

- Disk usage > 85% → ALERT
- RAM usage > 90% → ALERT
- Load average > 4.0 → ALERT
- OpenClaw process down → ALERT

## Cron Integration

```bash
# Hourly monitoring (alerts only if thresholds exceeded)
0 * * * * ~/krabot/skills/system-monitor/monitor.sh

# Daily report at 10:00 AM
0 10 * * * ~/krabot/skills/system-monitor/daily_report.sh
```

## Files

- `monitor.sh` — Main monitoring script
- `status.sh` — Quick status check
- `daily_report.sh` — Formatted daily report
- `lib/` — Common functions
