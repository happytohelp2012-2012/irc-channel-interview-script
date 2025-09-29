#!/usr/bin/env bash
# Accept Python >= 3.10; otherwise install via the native package manager.
set -euo pipefail

REQUIRED_MAJOR=3
REQUIRED_MINOR=10

have_python() { command -v python3 >/dev/null 2>&1; }

ver_ok() {
  local v
  v="$(python3 -c 'import sys;print(".".join(map(str,sys.version_info[:3])))' 2>/dev/null || echo 0)"
  [ "$v" = 0 ] && return 1
  IFS=. read -r MAJ MIN PATCH <<<"$v"
  if (( MAJ > REQUIRED_MAJOR )) || { (( MAJ == REQUIRED_MAJOR )) && (( MIN >= REQUIRED_MINOR )); }; then
    return 0
  else
    return 1
  fi
}

pm=""
if   command -v apt-get >/dev/null 2>&1; then pm="apt"
elif command -v dnf     >/dev/null 2>&1; then pm="dnf"
elif command -v yum     >/dev/null 2>&1; then pm="yum"
elif command -v pacman  >/dev/null 2>&1; then pm="pacman"
elif command -v zypper  >/dev/null 2>&1; then pm="zypper"
fi

echo "▶ Checking Python (need >= ${REQUIRED_MAJOR}.${REQUIRED_MINOR})..."
if have_python && ver_ok; then
  python3 --version
  echo "✅ Python is ready."
  exit 0
fi

echo "↺ Installing/Upgrading Python via $pm..."
case "$pm" in
  apt)
    sudo apt-get update
    # Prefer specific newer versions when available; fall back to default python3
    sudo apt-get install -y python3 || true
    sudo apt-get install -y python3.12 python3.11 python3.10 2>/dev/null || true
    ;;
  dnf)
    sudo dnf -y install python3 || true
    ;;
  yum)
    sudo yum -y install python3 || true
    ;;
  pacman)
    sudo pacman -Sy --noconfirm python || true
    ;;
  zypper)
    sudo zypper --non-interactive install python3 || true
    ;;
  *)
    echo "❌ Unsupported package manager. Please install Python 3.10+ manually."
    exit 1
    ;;
esac

echo "▶ Verifying..."
if have_python; then python3 --version; else echo "❌ python3 not found"; exit 1; fi
if ver_ok; then
  echo "✅ Python is ready. Use: python3"
else
  echo "⚠️ Installed Python may be older than ${REQUIRED_MAJOR}.${REQUIRED_MINOR}. Consider enabling a newer repo or installing from python.org."
  exit 1
fi
