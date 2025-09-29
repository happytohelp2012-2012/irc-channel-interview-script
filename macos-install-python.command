#!/usr/bin/env bash
# Accept Python >= 3.10; otherwise install via Homebrew (installs python@3.12).
set -euo pipefail

REQUIRED_MAJOR=3
REQUIRED_MINOR=10

have_python() {
  command -v python3 >/dev/null 2>&1
}

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

echo "▶ Checking Python (need >= ${REQUIRED_MAJOR}.${REQUIRED_MINOR})..."
if have_python && ver_ok; then
  python3 --version
  echo "✅ Python is ready."
  exit 0
fi

echo "↺ Installing/Upgrading Python via Homebrew..."
if ! command -v brew >/dev/null 2>&1; then
  echo "• Installing Homebrew (may prompt for your password)..."
  NONINTERACTIVE=1 /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  # Add brew to PATH for current session
  if [[ -d /opt/homebrew/bin ]]; then export PATH="/opt/homebrew/bin:$PATH"; fi
  if [[ -d /usr/local/bin ]];   then export PATH="/usr/local/bin:$PATH";   fi
fi

brew update
brew install python@3.12 || brew upgrade python@3.12 || true
# Ensure 'python3' points to the brewed Python
if ! command -v python3 >/dev/null 2>&1; then
  echo "• Linking python3..."
  brew link --overwrite python@3.12 || true
fi

echo "▶ Verifying..."
python3 --version
if ver_ok; then
  echo "✅ Python is ready. Use: python3"
else
  echo "⚠️ Python installed, but version check failed. Try opening a new terminal and run: python3 --version"
  exit 1
fi
