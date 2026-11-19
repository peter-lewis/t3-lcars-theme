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

# LCARS has more than 50,000 characters of CSS. T3 Code 0.1.10 and earlier, and nightlies before
# 0.1.11-nightly.20261117.4825, cap theme CSS at 50,000 and leave the theme out of the list.
# Prints the version of each installed T3 Code app that is too old.
old_t3_versions() {
  local app v base build
  for app in /Applications/T3\ Code*.app "$HOME"/Applications/T3\ Code*.app; do
    [ -f "$app/Contents/Info.plist" ] || continue
    v="$(defaults read "$app/Contents/Info.plist" CFBundleShortVersionString 2>/dev/null)" || continue
    base="${v%%-*}"
    build="${v##*.}"
    if [ "$(printf '%s\n0.1.11\n' "$base" | sort -t. -k1,1n -k2,2n -k3,3n | head -1)" != "0.1.11" ]; then
      echo "$(basename "$app" .app) $v"   # older than 0.1.11
    elif [ "$base" = "0.1.11" ] && [ "$v" != "$base" ] && [ "$build" -lt 4825 ] 2>/dev/null; then
      echo "$(basename "$app" .app) $v"   # a 0.1.11 prerelease from before the 100,000 cap
    fi
  done
}

mkdir -p "$THEMES"
for theme in "$REPO"/themes/*.json; do
  place "$theme" "$THEMES/$(basename "$theme")"
  echo "Installed theme $(basename "$theme" .json) -> $THEMES"
done

if [ "$(uname)" = Darwin ]; then
  OLD="$(old_t3_versions)"
  if [ -n "$OLD" ]; then
    echo >&2
    echo "Warning: these T3 Code versions cap theme CSS at 50,000 characters and will not list LCARS:" >&2
    echo "$OLD" | sed 's/^/  /' >&2
    echo "LCARS needs T3 Code Nightly 0.1.11-nightly.20261117.4825 or later, or a Stable release after 0.1.10." >&2
  fi
fi

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
