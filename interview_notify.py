#!/usr/bin/env python3
import os
import re
import time
import glob
import urllib.request
import urllib.error
from typing import Optional

# === SETTINGS ===
LOG_ROOT = "YOUR-PATH-TO-THE-LOGFILES"
TOPIC = "YOUR-UNIQUE-TOPIC-ON-NTFY"
MY_NICK = "YOUR-IRC-NICK"
BOT_NAMES = {"Gatekeeper", "GK"}  # Change these if the bot's name is changed. It's currently Gatekeeper.
NTFY_SERVER = "https://ntfy.sh" # Leave this as is.

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
LINE_RE = re.compile(
    r"""
    ^\[[^\]]+\]\s+         # [timestamp]
    <%?                    # '<' or '<%'
    (?P<bot>Gatekeeper|GK) # bot nick
    >\s+
    (?P<msg>.*)$           # rest of line
    """,
    re.VERBOSE,
)

CURRENTLY_INTERVIEWING_RE = re.compile(
    r"""
    ^Currently\ interviewing:\s+
    (?P<nick>[^\s:]+)\s+
    :::\s+(?P<room>\#red-interview-\d+)\s+:::\s+
    (?P<queue>\d+)\s+remaining\ in\ queue\.
    """,
    re.IGNORECASE | re.VERBOSE,
)

def handle_line(line: str):
    m = LINE_RE.match(line)
    if not m:
        return
    bot = m.group("bot")
    if bot not in BOT_NAMES:
        return

    msg = m.group("msg")
    m2 = CURRENTLY_INTERVIEWING_RE.match(msg)
    if not m2:
        return

    nick = m2.group("nick")
    room = m2.group("room")
    queue = m2.group("queue")

    # 1) Always send a single "interviews are happening" notification
    send_ntfy(
        title="Interviews are happening",
        body=f"{nick} is being interviewed in {room} — {queue} remaining in queue.",
        priority=None,
    )

    # 2) If it's your interview, send 3 high-priority notifications 1s apart
    if nick == MY_NICK:
        for i in range(3):
            send_ntfy(
                title="YOUR INTERVIEW IS UP",
                body=f"It's your turn, {MY_NICK}! In {room}. ({queue} remaining in queue at announce time)",
                priority=5,
            )
            if i < 2:
                time.sleep(1)

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
    print(f"[info] Bot(s): {', '.join(BOT_NAMES)} | Nick: {MY_NICK}")

    current_path = newest_channel_log()
    if not current_path:
        print(f"[error] No log files found under {LOG_ROOT}")
        return
    print(f"[info] Following newest log file: {current_path}")

    last_rotation_check = time.time()

    while True:
        # Follow the current file, but allow rotation checks even when idle.
        for maybe_line in follow_file(current_path):
            if maybe_line is not None:
                handle_line(maybe_line)

            # Check for a newer file every 15 seconds regardless of new lines
            if time.time() - last_rotation_check >= 15:
                last_rotation_check = time.time()
                latest = newest_channel_log()
                if latest and latest != current_path:
                    print(f"[info] Switching to newer log file: {latest}")
                    current_path = latest
                    break  # break inner loop to reopen the new file

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
