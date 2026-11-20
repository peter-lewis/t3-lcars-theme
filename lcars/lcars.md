---
description: Control the LCARS theme (light/dark, force a ship state, features on/off, sounds)
argument-hint: "[status|help|light|dark|auto|state <state>|<feature> on|off|sounds ...|reset]"
allowed-tools: Bash(python3 -I ~/.claude/lcars/lcars.py:*)
---
!`python3 -I ~/.claude/lcars/lcars.py $ARGUMENTS`

Repeat the output above to the user exactly, with nothing else.
