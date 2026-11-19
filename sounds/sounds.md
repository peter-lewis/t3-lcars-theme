---
description: Turn LCARS sounds on/off, or swap one for your own file (on | off | status | use <slot> <file> | reset [slot])
argument-hint: "[on|off|status|use <slot> <file>|reset [slot]]"
allowed-tools: Bash(python3 -I ~/.claude/hooks/lcars-sounds/toggle.py:*)
---
!`python3 -I ~/.claude/hooks/lcars-sounds/toggle.py $ARGUMENTS`

Repeat the line above to the user exactly, with nothing else.
