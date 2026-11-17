# Adds or removes the LCARS sound hooks in ~/.claude/settings.json, leaving every other setting alone.
# Usage: hooks.py add|remove   (a timestamped backup of settings.json is written before any change)
import json, os, shutil, sys, time

SETTINGS = os.path.expanduser('~/.claude/settings.json')
SCRIPT = '"$HOME/.claude/hooks/lcars-sounds/lcars_sound.py"'
MARK = 'lcars-sounds/lcars_sound.py'


def cmd(event):
    return {"type": "command", "command": f"python3 -I {SCRIPT} {event}", "timeout": 5}


WANT = {
    "UserPromptSubmit": [{"hooks": [cmd("prompt")]}],
    "PreToolUse": [{"matcher": "AskUserQuestion", "hooks": [cmd("hail")]}],
    "Notification": [{"matcher": "permission_prompt|elicitation_dialog", "hooks": [cmd("hail")]}],
    "Stop": [{"hooks": [cmd("stop")]}],
}


def strip(hooks):
    """Remove every LCARS hook entry, then drop groups and events left empty."""
    for event in list(hooks):
        groups = []
        for g in hooks[event]:
            g = dict(g)
            g["hooks"] = [h for h in g.get("hooks", []) if MARK not in h.get("command", "")]
            if g["hooks"]:
                groups.append(g)
        if groups:
            hooks[event] = groups
        else:
            del hooks[event]


def main():
    action = sys.argv[1] if len(sys.argv) > 1 else ''
    if action not in ('add', 'remove'):
        sys.exit('usage: hooks.py add|remove')
    settings = {}
    if os.path.exists(SETTINGS):
        with open(SETTINGS) as f:
            settings = json.load(f)
        shutil.copy2(SETTINGS, f'{SETTINGS}.bak-{time.strftime("%Y%m%d-%H%M%S")}')
    hooks = settings.setdefault('hooks', {})
    strip(hooks)
    if action == 'add':
        for event, groups in WANT.items():
            hooks.setdefault(event, []).extend(groups)
    if not hooks:
        del settings['hooks']
    os.makedirs(os.path.dirname(SETTINGS), exist_ok=True)
    with open(SETTINGS, 'w') as f:
        json.dump(settings, f, indent=2)
        f.write('\n')
    print(f'LCARS sound hooks {"added to" if action == "add" else "removed from"} {SETTINGS}')


main()
