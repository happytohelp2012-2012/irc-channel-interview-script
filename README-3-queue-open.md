# `queue-open.py` — Quick Start

Watches your Orpheus **#recruitment** IRC log and notifies you when:
- Someone types the open‑queue command (e.g., `!open-queue`), **or**
- The bot announces the queue is open (e.g., `hermes: The queue is now open. Interviews will start immediately.`)

It sends a small burst of ntfy notifications so you don’t miss the start.

---

## 1) Requirements
- **Python 3.10+** (use the installer scripts I provided if needed).
- Internet access to your **ntfy** server/topic.
- IRC logs saved locally.

---

## 2) Configure the script
Open `queue-open.py` and confirm these at the top:

```python
LOG_ROOT = "YOUR-PATH-TO-THE-LOGFILES"
TOPIC = "YOUR-UNIQUE-TOPIC-ON-NTFY"
NTFY_SERVER = "https://ntfy.sh"

BOT_NAME = "hermes"
OPEN_QUEUE_COMMAND = "!open-queue"
OPEN_QUEUE_ANNOUNCEMENT = "The queue is now open. Interviews will start immediately."
NOTIFY_TEXT = "Orpheus interviews are open!"
```

- **LOG_ROOT**: Path to the **#recruitment** channel folder inside your IRC logs.
- **BOT_NAME**: The bot that posts the announcement (exact nick).
- **OPEN_QUEUE_COMMAND / OPEN_QUEUE_ANNOUNCEMENT**: Match the phrases used in your channel.
- **TOPIC / NTFY_SERVER**: Your ntfy topic and server.

---

## 3) Put it somewhere simple
Recommended:
```
~/scripts/queue-open.py
```

---

## 4) Run it
**macOS / Linux**
```bash
python3 ~/scripts/queue-open.py
```

**Windows (PowerShell)**
```powershell
py -3 ~\scripts\queue-open.py
```

(Optional) Run in background on macOS/Linux:
```bash
nohup python3 ~/scripts/queue-open.py >/tmp/queue-open.log 2>&1 &
```

---

## 5) Test it (simulated log lines)
Paste the following in a terminal to append test lines into **today’s** `#recruitment` log file:

```bash
LOG="YOUR-PATH-TO-THE-LOGFILES/$(date +%F).txt"

printf '[%s] <randomUser> !open-queue\n' "$(date -Iseconds)" >> "$LOG"

printf "[%s] <hermes> The queue is now open. Interviews will start immediately.\n" "$(date -Iseconds)" >> "$LOG"
```

**Expected notifications**
- When the command or the announcement is detected, you’ll receive a short burst (default: 3) of ntfy notifications.

---

## 6) Troubleshooting
- **No notifications?** Confirm `LOG_ROOT` is correct and today’s file exists.
- **Bot/phrases mismatch?** Adjust `BOT_NAME`, `OPEN_QUEUE_COMMAND`, and `OPEN_QUEUE_ANNOUNCEMENT` to match what you see in the logs.
- **ntfy check:** Verify your topic/server with:
  ```bash
  curl -d "test" -H "Title: hello" https://ntfy.sh/YOUR-UNIQUE-TOPIC-ON-NTFY
  ```
- **Still nothing?** Watch the terminal output for `[info]` lines confirming matches and file switches.
