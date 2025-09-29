#!/usr/bin/env python3
import os
import re
import time
import glob
import urllib.request
import urllib.error
from typing import Optional

# === SETTINGS ===
# Point this to your IRC logs for the #recruitment channel
LOG_ROOT = "YOUR-PATH-TO-THE-LOGFILES"

# ntfy topic & server
TOPIC = "YOUR-UNIQUE-TOPIC-ON-NTFY"  # <-- set your topic
NTFY_SERVER = "https://ntfy.sh"

# Bot and trigger phrases
BOT_NAME = "hermes"
OPEN_QUEUE_COMMAND = "!open-queue"
OPEN_QUEUE_ANNOUNCEMENT = "The queue is now open. Interviews will start immediately."
NOTIFY_TEXT = "Orpheus interviews are open!"

# === Notifications ===
def send_ntfy(title: str, body: str, priority: Optional[int] = None) -> None:
    url = f"{NTFY_SERVER.rstrip('/')}/{TOPIC}"
    req = urllib.request.Request(url, data=body.encode("utf-8"), method="POST")
    req.add_header("Title", title)
    if priority is not None:
        req.add_header("Priority", str(priority))  # 1..5
    try:
        with urllib.request.urlopen(req, timeout=10) as _:
            pass
    except urllib.error.URLError as e:
        print(f"[warn] ntfy post failed: {e}")

def burst_notify(times: int = 3, delay_s: float = 1.0):
    for i in range(times):
        send_ntfy(title=NOTIFY_TEXT, body=NOTIFY_TEXT, priority=None)
        if i < times - 1:
            time.sleep(delay_s)

# === Log discovery ===
def newest_channel_log() -> Optional[str]:
    """
    Find the newest file anywhere under LOG_ROOT.
    Assumes LOG_ROOT is the channel folder.
    """
    pattern = os.path.join(LOG_ROOT, "**", "*")
    candidates = [p for p in glob.glob(pattern, recursive=True) if os.path.isfile(p)]
    if not candidates:
        return None
    return max(candidates, key=lambda p: os.path.getmtime(p))

# === Parsing ===
# Example IRC log lines:
# [12:34:56] <nick> message
# [12:34:56] <%nick> message
LINE_RE = re.compile(
    r"""
    ^\[[^\]]+\]\s+        # [timestamp]
    <%?                   # '<' or '<%'
    (?P<nick>[^>]+)       # nick (anything up to '>')
    >\s+
    (?P<msg>.*)$          # rest of the line
    """,
    re.VERBOSE,
)

def is_open_queue_command(msg: str) -> bool:
    return OPEN_QUEUE_COMMAND.lower() in msg.lower()

def is_open_queue_announcement(nick: str, msg: str) -> bool:
    return nick.strip().lower() == BOT_NAME.lower() and msg.strip().lower() == OPEN_QUEUE_ANNOUNCEMENT.lower()

def handle_line(line: str):
    m = LINE_RE.match(line)
    if not m:
        return

    nick = m.group("nick").strip()
    msg = m.group("msg").strip()

    if is_open_queue_command(msg) or is_open_queue_announcement(nick, msg):
        print(f"[info] Trigger matched: nick='{nick}' | msg='{msg}'")
        burst_notify(times=3, delay_s=1.0)

# === Robust tail that handles midnight rotation ===
def follow_file(path: str):
    """
    Generator that yields new lines from 'path'. If no new line appears,
    yields None so the caller can do housekeeping (like rotation checks).
    """
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            f.seek(0, os.SEEK_END)
            while True:
                line = f.readline()
                if line:
                    yield line.rstrip("\n")
                else:
                    yield None
                    time.sleep(1.0)
    except FileNotFoundError:
        # If the file disappears (rotation), let caller handle.
        yield None

def main():
    print(f"[info] Watching IRC logs under: {LOG_ROOT}")
    print(f"[info] Bot: {BOT_NAME} | Command trigger: {OPEN_QUEUE_COMMAND!r}")
    print(f"[info] Announcement trigger: {OPEN_QUEUE_ANNOUNCEMENT!r}")
    print(f"[info] ntfy topic: {TOPIC}")

    current_path = newest_channel_log()
    if not current_path:
        print(f"[error] No log files found under {LOG_ROOT}")
        return
    print(f"[info] Following newest log file: {current_path}")

    last_rotation_check = time.time()

    while True:
        for maybe_line in follow_file(current_path):
            if maybe_line is not None:
                handle_line(maybe_line)

            # Check for a newer file every 15 seconds
            if time.time() - last_rotation_check >= 15:
                last_rotation_check = time.time()
                latest = newest_channel_log()
                if latest and latest != current_path:
                    print(f"[info] Switching to newer log file: {latest}")
                    current_path = latest
                    break  # reopen new file

            # If the file vanished, break and re-discover
            if maybe_line is None and not os.path.exists(current_path):
                latest = newest_channel_log()
                if latest and latest != current_path:
                    print(f"[info] File rotated; switching to: {latest}")
                    current_path = latest
                    break

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[info] Exiting on Ctrl-C")
