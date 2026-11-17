---
description: Turn LCARS sounds on/off (on | off | status; no argument flips)
argument-hint: "[on|off|status]"
allowed-tools: Bash(python3 -I ~/.claude/hooks/lcars-sounds/toggle.py:*)
---
!`python3 -I ~/.claude/hooks/lcars-sounds/toggle.py $ARGUMENTS`

Repeat the line above to the user exactly, with nothing else.
