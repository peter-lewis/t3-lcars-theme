#!/usr/bin/env bash
# Removes the LCARS theme files and the LCARS sounds. Switch T3 Code to another theme first.
# Usage: ./uninstall.sh
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

for theme in "$REPO"/themes/*.json; do
  rm -f "$HOME/.t3/userdata/themes/$(basename "$theme")"
done
echo "Removed LCARS themes from ~/.t3/userdata/themes"

if [ -d "$HOME/.claude/hooks/lcars-sounds" ]; then
  python3 -I "$HOME/.claude/hooks/lcars-sounds/toggle.py" off >/dev/null 2>&1 || true   # silence a running hum
  python3 -I "$REPO/sounds/hooks.py" remove
  rm -rf "$HOME/.claude/hooks/lcars-sounds" "$HOME/.claude/lcars-sounds-state"
  rm -f "$HOME/.claude/commands/sounds.md"
  echo "Removed LCARS sounds"
fi
