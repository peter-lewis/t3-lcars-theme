#!/usr/bin/env bash
# Installs the LCARS theme into T3 Code, and optionally the LCARS sounds into Claude Code.
# Usage: ./install.sh [--sounds]
# Safe to re-run: it updates in place and backs up anything it replaces.
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
THEMES="$HOME/.t3/userdata/themes"
HOOKS="$HOME/.claude/hooks/lcars-sounds"
COMMANDS="$HOME/.claude/commands"
STAMP="$(date +%Y%m%d-%H%M%S)"

SOUNDS=0
for arg in "$@"; do
  case "$arg" in
    --sounds) SOUNDS=1 ;;
    -h|--help) sed -n '2,4p' "$0"; exit 0 ;;
    *) echo "Unknown option: $arg" >&2; exit 1 ;;
  esac
done

# Copy src to dst, backing up a different existing file. T3 ignores symlinked themes, so always copy.
place() {
  local src="$1" dst="$2"
  if [ -L "$dst" ]; then rm "$dst"; fi
  if [ -f "$dst" ] && ! cmp -s "$src" "$dst"; then cp "$dst" "$dst.bak-$STAMP"; fi
  cp "$src" "$dst"
}

mkdir -p "$THEMES"
for theme in "$REPO"/themes/*.json; do
  place "$theme" "$THEMES/$(basename "$theme")"
  echo "Installed theme $(basename "$theme" .json) -> $THEMES"
done

if [ "$SOUNDS" = 1 ]; then
  if [ ! -x /usr/bin/afplay ]; then
    echo "Skipping sounds: they need macOS (afplay)." >&2
  else
    mkdir -p "$HOOKS" "$COMMANDS"
    for f in lcars_sound.py toggle.py make_beeps.py make_hum.py; do place "$REPO/sounds/$f" "$HOOKS/$f"; done
    echo "Generating sounds..."
    python3 -I "$HOOKS/make_beeps.py" >/dev/null
    python3 -I "$HOOKS/make_hum.py" >/dev/null
    place "$REPO/sounds/sounds.md" "$COMMANDS/sounds.md"
    python3 -I "$REPO/sounds/hooks.py" add
    echo "Installed sounds -> $HOOKS (toggle with /sounds; restart Claude Code to load the hooks)"
  fi
fi

echo
echo "Done. Choose the LCARS theme in T3 Code's settings to turn it on."
