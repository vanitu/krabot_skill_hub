# Weather Skill

Get current weather and forecasts via wttr.in (no API key required).

## Usage

```bash
# Current weather (auto-location)
curl wttr.in

# Specific city
curl wttr.in/Moscow
curl wttr.in/London?lang=ru

# One-line format
curl "wttr.in/Moscow?format=3"

# Full forecast
curl wttr.in/Moscow

# Moon phase
curl wttr.in/Moon
```

## Aliases (add to your shell)

```bash
alias weather='curl wttr.in'
alias w='curl "wttr.in/?format=3"'
alias wm='curl "wttr.in/Moscow?format=3"'
```

## Options

- `?lang=ru` — Russian language
- `?format=3` — Compact: "Moscow: 🌦 +7°C"
- `?m` — Metric units (default)
- `?u` — US units

## Dependencies

- `curl` (installed by default on most systems)
