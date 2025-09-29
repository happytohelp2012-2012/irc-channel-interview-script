# `interview_notify.py` — Quick Start

Monitors your IRC logs for lines like **“Currently interviewing:”** from the invite bot (`Gatekeeper`/`GK`). The script is written for the Textual client, however it should easily work with other clients as well. 
Sends an ntfy notification every time interviews are active, and if it’s **your nick**, it sends a high‑priority burst so you won’t miss it.

---

## 1) Requirements
- **Python 3.10+** (use the installer scripts I provided if needed).
- Internet access to your **ntfy** server/topic.
- Textual IRC logs saved locally (the script follows the **newest** file and handles midnight rotation).

---

## 2) Configure the script
Open `interview_notify.py` and check these at the top:

```python
LOG_ROOT = "YOUR-PATH-TO-THE-LOGFILES"
TOPIC = "YOUR-UNIQUE-TOPIC-ON-NTFY"
MY_NICK = "YOUR-IRC-NICK"
BOT_NAMES = {"Gatekeeper", "GK"}
NTFY_SERVER = "https://ntfy.sh"
```

- **LOG_ROOT**: Path to the **#RED-invites** channel folder inside your IRC CLIENT logs.
- **MY_NICK**: Your IRC nick (exact spelling/case used by the bot output).
- **BOT_NAMES**: The bot nick(s) seen in your logs (exact matches).
- **TOPIC / NTFY_SERVER**: Your ntfy topic and server.

> Tip: If your log path or bot names differ, adjust them here.

---

## 3) Put it somewhere simple
Recommended:
```
~/scripts/interview_notify.py
```

---

## 4) Run it
**macOS / Linux**
```bash
python3 ~/scripts/interview_notify.py
```

**Windows (PowerShell)**
```powershell
py -3 ~\scripts\interview_notify.py
```

> Keep the window open while you want notifications. The script will print `[info]` messages when it matches lines or switches to a rotated log file.

(Optional) Run in background on macOS/Linux:
```bash
nohup python3 ~/scripts/interview_notify.py >/tmp/interview_notify.log 2>&1 &
```

---

## 5) Test it (simulated log lines)
Edit and then paste the following in a terminal to append test lines into **today’s** `#RED-invites` log file:

```bash
LOG="YOUR-PATCH-TO-THE-LOGFILES/$(date +%F).txt"

printf "[%s] <%%Gatekeeper> Currently interviewing: other-random-nick ::: #red-interview-01 ::: 48 remaining in queue.\n" "$(date -Iseconds)" >> "$LOG"

printf "[%s] <%%Gatekeeper> Currently interviewing: YOUR-IRC-NICK ::: #red-interview-02 ::: 40 remaining in queue.\n" "$(date -Iseconds)" >> "$LOG"
```

**Expected notifications**
- For each line: a standard “**Interviews are happening**” notification.
- If `nick` matches `MY_NICK`: a **burst of 3 high‑priority** notifications (1s apart).

---

## 6) Troubleshooting
- **No notifications?** Double‑check `LOG_ROOT` points to the correct channel folder and today’s log file exists.
- **Bot nick mismatch?** Ensure `BOT_NAMES` matches exactly what appears in your logs.
- **ntfy check:** Verify your topic/server with a quick test:
  ```bash
  curl -d "test" -H "Title: hello" https://ntfy.sh/YOUR-UNIQUE-TOPIC-ON-NTFY
  ```
- **Still nothing?** Watch the script output for `[info]` lines indicating matches or log rotation.
