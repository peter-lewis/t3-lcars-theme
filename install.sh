#!/usr/bin/env bash
# Installs the LCARS theme into T3 Code, and optionally the LCARS sounds into Claude Code.
# Usage: ./install.sh [--sounds] [--compact dark|nofont | --full]
#   --compact dark    for T3 Code 0.1.10: dark mode only, with the LCARS font
#   --compact nofont  for T3 Code 0.1.10: light and dark, in the system's condensed font
#   --full            the full theme, even when T3 Code looks too old for it
# Safe to re-run: it updates in place and backs up anything it replaces.
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
THEMES="$HOME/.t3/userdata/themes"
HOOKS="$HOME/.claude/hooks/lcars-sounds"
COMMANDS="$HOME/.claude/commands"
STAMP="$(date +%Y%m%d-%H%M%S)"
NEEDS="T3 Code Nightly 0.1.11-nightly.20261117.4825 or later, or a Stable release after 0.1.10"

SOUNDS=0
VARIANT=""
while [ $# -gt 0 ]; do
  case "$1" in
    --sounds) SOUNDS=1 ;;
    --full) VARIANT=full ;;
    --compact) shift; VARIANT="${1:-}" ;;
    --compact=*) VARIANT="${1#--compact=}" ;;
    -h|--help) sed -n '2,7p' "$0"; exit 0 ;;
    *) echo "Unknown option: $1" >&2; exit 1 ;;
  esac
  shift
done
case "$VARIANT" in
  ""|full|dark|nofont) ;;
  *) echo "--compact takes dark or nofont, not '$VARIANT'" >&2; exit 1 ;;
esac

# Copy src to dst, backing up a different existing file. T3 ignores symlinked themes, so always copy.
place() {
  local src="$1" dst="$2"
  if [ -L "$dst" ]; then rm "$dst"; fi
  if [ -f "$dst" ] && ! cmp -s "$src" "$dst"; then cp "$dst" "$dst.bak-$STAMP"; fi
  cp "$src" "$dst"
}

# The full theme has about 83,000 characters of CSS. T3 Code 0.1.10 and earlier, and nightlies
# before 0.1.11-nightly.20261117.4825, cap theme CSS at 50,000 and leave the theme out of the list.
too_old() {
  local v="$1" base build
  base="${v%%-*}"
  build="${v##*.}"
  if [ "$(printf '%s\n0.1.11\n' "$base" | sort -t. -k1,1n -k2,2n -k3,3n | head -1)" != "0.1.11" ]; then
    return 0   # older than 0.1.11
  fi
  [ "$base" = "0.1.11" ] && [ "$v" != "$base" ] && [ "$build" -lt 4825 ] 2>/dev/null   # 0.1.11 prerelease before the 100,000 cap
}

# Prints "<name> <version>" for each T3 Code that is too old for the full theme. Inside T3 Code,
# T3CODE_CLI_PATH names the server running this shell, so only that one counts. Otherwise check the
# installed apps, then the t3 command.
old_t3_versions() {
  local app v found=0
  if [ -n "${T3CODE_CLI_PATH:-}" ] && [ -x "$T3CODE_CLI_PATH" ]; then
    v="$("$T3CODE_CLI_PATH" --version 2>/dev/null | awk '{print $NF}' | sed 's/^v//')" || v=""
    if [ -n "$v" ]; then
      if too_old "$v"; then echo "T3 Code $v"; fi
      return 0
    fi
  fi
  if [ "$(uname)" = Darwin ]; then
    for app in /Applications/T3\ Code*.app "$HOME"/Applications/T3\ Code*.app; do
      [ -f "$app/Contents/Info.plist" ] || continue
      v="$(defaults read "$app/Contents/Info.plist" CFBundleShortVersionString 2>/dev/null)" || continue
      found=1
      if too_old "$v"; then echo "$(basename "$app" .app) $v"; fi
    done
  fi
  if [ "$found" = 0 ] && command -v t3 >/dev/null 2>&1; then
    v="$(t3 --version 2>/dev/null | awk '{print $NF}' | sed 's/^v//')" || v=""
    if [ -n "$v" ] && too_old "$v"; then echo "t3 $v"; fi
  fi
  return 0
}

OLD="$(old_t3_versions)"
if [ -z "$VARIANT" ] && [ -z "$OLD" ]; then
  VARIANT=full
fi

if [ -z "$VARIANT" ]; then
  RERUN="./install.sh"
  if [ "$SOUNDS" = 1 ]; then RERUN="$RERUN --sounds"; fi
  if [ -t 0 ] && [ -t 1 ]; then
    echo "This T3 Code caps theme CSS at 50,000 characters, too small for the full LCARS theme:"
    echo "$OLD" | sed 's/^/  /'
    echo
    echo "Install a compact version instead. Each one leaves out one thing:"
    echo "  1) Dark mode only, with the LCARS font (recommended)"
    echo "  2) Light and dark mode, in the system's condensed font instead of the LCARS font"
    echo "  3) The full theme anyway. It appears only after you update to $NEEDS."
    echo "  q) Cancel"
    printf "Choice [1]: "
    read -r answer
    case "${answer:-1}" in
      1) VARIANT=dark ;;
      2) VARIANT=nofont ;;
      3) VARIANT=full ;;
      *) echo "Cancelled. Nothing was installed."; exit 1 ;;
    esac
  else
    # No terminal: an agent is running this. Stop before changing anything so it can ask the user.
    cat <<EOF
LCARS INSTALL NEEDS A CHOICE FROM THE USER. Nothing was installed.

This T3 Code caps theme CSS at 50,000 characters:
$(echo "$OLD" | sed 's/^/  /')
The full LCARS theme needs about 83,000, so T3 Code would leave it out of the theme list.

Agent: ask the user which version to install. Use your question tool if you have one
(AskUserQuestion in Claude Code), otherwise ask in chat and wait for the answer. Offer these
options in this order, then do what the chosen one says:
  1. Dark mode only, with the LCARS font (recommended)
     Run: $RERUN --compact dark
  2. Light and dark mode, with the system's condensed font instead of the LCARS font
     Run: $RERUN --compact nofont
  3. Update T3 Code first, then install the full theme
     The user updates to $NEEDS.
     Then run: $RERUN
Do not pick for the user, and do not edit or minify the theme files.
EOF
    exit 2
  fi
fi

mkdir -p "$THEMES"
if [ "$VARIANT" = full ]; then
  for theme in "$REPO"/themes/*.json; do
    place "$theme" "$THEMES/$(basename "$theme")"
    echo "Installed theme $(basename "$theme" .json) -> $THEMES"
  done
  if [ -n "$OLD" ]; then
    echo >&2
    echo "Warning: this T3 Code caps theme CSS at 50,000 characters and will not list LCARS:" >&2
    echo "$OLD" | sed 's/^/  /' >&2
    echo "Update to $NEEDS, or run ./install.sh --compact dark (or nofont)." >&2
  fi
else
  place "$REPO/themes/compact/lcars-$VARIANT.json" "$THEMES/lcars.json"
  place "$REPO/themes/compact/lcars-red-alert.json" "$THEMES/lcars-red-alert.json"
  echo "Installed compact theme lcars ($VARIANT) and lcars-red-alert -> $THEMES"
  echo "After you update to $NEEDS, run ./install.sh again for the full theme."
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
