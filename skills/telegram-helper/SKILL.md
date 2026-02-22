# Telegram Helper Skill

Telegram Bot API helper with inline keyboard support. Упрощает отправку сообщений и создание интерактивных UI.

## Quick Start

```bash
cd ~/krabot/skills/telegram-helper

# Отправить сообщение
./send_message.sh "Hello World!"

# Отправить с кнопками
./send_buttons.sh "Confirm?" "✅ Yes:yes" "❌ No:no"

# Отправить в конкретный чат/топик
./send_buttons.sh -c "-1001234567890" -t "123" "Question?" "A:opt_a" "B:opt_b"
```

## Library Mode

Используйте в других скриптах:

```bash
source ~/krabot/skills/telegram-helper/lib/telegram.sh

# Отправить сообщение
telegram_send "$CHAT_ID" "$MESSAGE"

# Отправить с кнопками
telegram_send_buttons "$CHAT_ID" "$TOPIC_ID" "Choose:" "A:opt_a" "B:opt_b"

# Редактировать сообщение после клика
telegram_edit_message "$CHAT_ID" "$MSG_ID" "$NEW_TEXT"
telegram_edit_buttons "$CHAT_ID" "$MSG_ID"  # Удалить кнопки
```

## Button Format

```
"Label:callback_data"
"✅ Confirm:confirm_action"
"🔗 Open Link:url:https://example.com"
```

## Templates

- `button_handler.sh` — Callback router template
- `example_usage.sh` — Usage examples
- `interactive_example.sh` — Interactive flows demo

## Features

- ✅ Inline keyboards with callbacks
- ✅ URL buttons (open links)
- ✅ Edit messages after button click
- ✅ Forum topic support (thread_id)
- ✅ Atomic: no config files, works via env vars
