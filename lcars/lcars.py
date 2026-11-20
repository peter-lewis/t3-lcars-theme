# /lcars: control the LCARS theme from Claude Code. Usage: lcars.py [command] (see HELP below)
# install.sh keeps an untouched copy of each installed theme in ~/.claude/lcars/base/. Every change
# rebuilds ~/.t3/userdata/themes/<theme>.json ($T3CODE_HOME if set) from that copy plus ~/.claude/lcars/settings.json,
# and T3 Code picks up the new file live. Re-running install.sh refreshes the copies and re-applies.
import json, os, re, subprocess, sys

HOME = os.path.expanduser('~')
DIR = os.path.join(HOME, '.claude', 'lcars')
BASE = os.path.join(DIR, 'base')
SETTINGS = os.path.join(DIR, 'settings.json')
THEMES = os.path.join(os.environ.get('T3CODE_HOME') or os.path.join(HOME, '.t3'), 'userdata', 'themes')
SOUNDS = os.path.join(HOME, '.claude', 'hooks', 'lcars-sounds', 'toggle.py')

DEFAULTS = {'mode': 'auto', 'state': 'auto',
            'starfield': True, 'warp': True, 'alerts': True, 'font': True, 'motion': True}
MODES = {'auto': "follows T3 Code's light/dark setting", 'light': 'always light', 'dark': 'always dark'}
STATES = {'auto': 'follows your threads', 'idle': 'starfield at rest', 'warp': 'warp, as if Claude is working',
          'hail': 'incoming hail (blue)', 'yellow': 'yellow alert (amber)', 'red': 'red alert'}
FEATURES = {'starfield': 'drifting stars behind the chat', 'warp': 'warp streaks while Claude works',
            'alerts': 'hail, yellow and red alert colours', 'font': 'the LCARS font (off: the system condensed font)',
            'motion': 'animation: drift, warp, breathing alerts, blinking endcaps'}

# The CSS hooks each setting rewrites. The ship states are :root:has(<trigger>) rules.
WARP = ':has(button[aria-label="Stop generation"])'
ALERTS = {'hail': ':has([data-sidebar-row] .lucide-message-circle-question-mark)',
          'yellow': ':has([data-sidebar-row] .lucide-shield-question-mark)',
          'red': ':has([data-sidebar-row] .lucide-circle-alert)'}
ALWAYS, NEVER = ':is(*)', ':not(*)'
LIGHT = 'html:not(.dark)'   # light-mode rules: T3 Code drops the dark class in light appearance
FONT_FACE = re.compile(r'@font-face\{font-family:"LCARS Antonio";[^}]*\}\n?')
REDUCED = '@media (prefers-reduced-motion:reduce){'
MARK = '\n/* /lcars settings */\n'
CAP_FULL, CAP_COMPACT = 100_000, 50_000

HELP = """LCARS controls:

- `/lcars` or `/lcars status` shows the current settings
- `/lcars light`, `/lcars dark`, `/lcars auto` forces light or dark, or follows T3 Code again
- `/lcars state <state>` holds the ship in one state: {states}
- `/lcars <feature> on` or `off` for each feature: {features}
- `/lcars sounds ...` runs `/sounds` (on, off, status, `use <slot> <file>`, reset)
- `/lcars reset` puts everything back to the defaults

Changes show up in T3 Code within a second or two."""


def load():
    try:
        with open(SETTINGS) as f:
            return {**DEFAULTS, **{k: v for k, v in json.load(f).items() if k in DEFAULTS}}
    except (OSError, ValueError):
        return dict(DEFAULTS)


def save(s):
    os.makedirs(DIR, exist_ok=True)
    with open(SETTINGS, 'w') as f:
        json.dump(s, f, indent=2)
        f.write('\n')


def bases():
    return sorted(f for f in os.listdir(BASE) if f.endswith('.json')) if os.path.isdir(BASE) else []


def block(css, start):
    """Return (begin, end) of the brace block that opens at css[start:] (the text ending in '{')."""
    depth, i = 0, start
    while i < len(css):
        if css[i] == '{': depth += 1
        elif css[i] == '}':
            depth -= 1
            if depth == 0: return start, i + 1
        i += 1
    return start, len(css)


def reduced_motion_rules(css):
    """The theme's own reduced-motion rules, which stop every LCARS animation."""
    out, i = [], css.find(REDUCED)
    while i >= 0:
        b, e = block(css, i)
        out.append(css[b + len(REDUCED):e - 1])
        i = css.find(REDUCED, e)
    return ''.join(out)


def build(theme, s):
    """Apply settings s to a theme dict. Returns (theme, notes) where notes lists settings this build can't do."""
    t = json.loads(json.dumps(theme))
    css, notes, extra = t['css'], [], []
    red_variant = t.get('name') == 'LCARS Red Alert'
    state = s['state']

    def cond(kind, on):
        if state != 'auto': return ALWAYS if state == kind else NEVER
        return None if on else NEVER

    c = cond('warp', s['warp'])
    if c: css = css.replace(WARP, c)
    for kind, trigger in ALERTS.items():
        c = cond(kind, s['alerts'])
        if c: css = css.replace(trigger, c)

    # Replacements are no longer than LIGHT, so a compact build near T3 Code's cap never grows. .lcx is never set.
    dark_only = red_variant or LIGHT not in css or t.get('variants', {}).get('light') == t['colors']
    if s['mode'] == 'light' and dark_only:
        if not red_variant: notes.append('light mode: this build is dark only')   # red alert is dark by design
    elif s['mode'] == 'dark' and not dark_only:
        css = css.replace(LIGHT, 'html.lcx')
        t['variants']['light'] = dict(t['colors'])
    elif s['mode'] == 'light':   # the light rules always match, and dark appearance uses the light palette
        css = css.replace(LIGHT, 'html:not(.lcx)')
        t['colors'] = dict(t['variants']['light'])

    if not s['font']:
        css = FONT_FACE.sub('', css)
    if not s['starfield']:
        extra.append('html:not(#lcars) [data-slot="sidebar-wrapper"]{background-image:none !important;animation:none !important;}')
    if not s['motion']:
        rules = reduced_motion_rules(css)
        if rules: extra.append(rules)
        else: notes.append('motion off: this build has no reduced-motion rules')

    if extra: css += MARK + '\n'.join(extra) + '\n'
    t['css'] = css
    return t, notes


def apply(s):
    """Rebuild every installed LCARS theme from its base copy. Returns (notes, error). On an error nothing is written."""
    built, notes = [], []
    for name in bases():
        with open(os.path.join(BASE, name)) as f:
            base = json.load(f)
        cap = CAP_FULL if len(base['css']) > CAP_COMPACT else CAP_COMPACT   # compact builds are for the 50,000 cap
        t, n = build(base, s)
        notes += [f'{name.removesuffix(".json")}: {x}' for x in n]
        if len(t['css']) > cap:
            return notes, (f'That would make {name} too big for this T3 Code ({len(t["css"]):,} of {cap:,} characters), '
                           'so nothing changed. The compact build has no room to spare: turn something else off first, '
                           'or update T3 Code and re-run ./install.sh for the full theme.')
        built.append((name, t))
    os.makedirs(THEMES, exist_ok=True)
    for name, t in built:
        dst = os.path.join(THEMES, name)
        tmp = dst + '.lcars-tmp'   # not .json, so T3 Code never lists a half-written file
        with open(tmp, 'w') as f:
            json.dump(t, f, indent=2)
        os.replace(tmp, dst)
    return notes, None


def status(s, notes=()):
    on = lambda v: 'on' if v else 'off'
    lines = ['LCARS status:', '',
             f"- Mode: `{s['mode']}`, {MODES[s['mode']]}",
             f"- State: `{s['state']}`, {STATES[s['state']]}",
             '- Features: ' + ', '.join(f'{k} `{on(s[k])}`' for k in FEATURES)]
    if os.path.exists(SOUNDS):   # same files toggle.py reads: a MUTE flag, and custom files named after their slot
        muted = os.path.exists(os.path.join(HOME, '.claude', 'lcars-sounds-state', 'MUTE'))
        custom_dir = os.path.join(HOME, '.claude', 'lcars-sounds-custom')
        mine = sorted({os.path.splitext(f)[0] for f in os.listdir(custom_dir)} if os.path.isdir(custom_dir) else [])
        lines.append(f"- Sounds: `{'off' if muted else 'on'}`" + (', your own for ' + ', '.join(mine) if mine else ''))
    else:
        lines.append('- Sounds: not installed (`./install.sh --sounds`)')
    if not bases():
        lines += ['', 'No LCARS theme found in ~/.claude/lcars/base. Run `./install.sh` from the t3-lcars-theme repo.']
    if notes:
        lines += [''] + [f'Note: {n}' for n in notes]
    if s != DEFAULTS:
        lines += ['', '`/lcars reset` goes back to the defaults. `/lcars help` lists everything.']
    return '\n'.join(lines)


def main(args):
    a = [x.lower() for x in args]
    s = load()
    if not a or a[0] == 'status':
        print(status(s)); return 0
    if a[0] in ('help', '-h', '--help'):
        print(HELP.format(states=', '.join(f'`{k}`' for k in STATES), features=', '.join(f'`{k}`' for k in FEATURES))); return 0
    if a[0] == 'sounds':
        if not os.path.exists(SOUNDS):
            print('Sounds are not installed. Run `./install.sh --sounds` from the t3-lcars-theme repo.'); return 1
        return subprocess.run([sys.executable, '-I', SOUNDS] + args[1:]).returncode
    if a[0] == 'apply':   # install.sh: rebuild from fresh base copies with the saved settings
        notes, error = apply(s)
        for n in notes + ([error] if error else []): print(f'LCARS: {n}', file=sys.stderr)
        return 0
    if a[0] == 'reset' and len(a) == 1:
        s = dict(DEFAULTS)
    elif a[0] == 'mode' and len(a) == 2 and a[1] in MODES:
        s['mode'] = a[1]
    elif a[0] in MODES and len(a) == 1:
        s['mode'] = a[0]
    elif a[0] == 'state' and len(a) == 2 and a[1] in STATES:
        s['state'] = a[1]
    elif a[0] in STATES and a[0] != 'auto' and len(a) == 1:
        s['state'] = a[0]
    elif a[0] in FEATURES and len(a) == 2 and a[1] in ('on', 'off'):
        s[a[0]] = a[1] == 'on'
    else:
        print(f'Unknown: `/lcars {" ".join(args)}`. `/lcars help` lists the commands.'); return 1
    if not bases():
        print('No LCARS theme found in ~/.claude/lcars/base. Run `./install.sh` from the t3-lcars-theme repo.'); return 1
    notes, error = apply(s)
    if error:
        print(error); return 1
    save(s)
    print(status(s, notes))
    return 0


sys.exit(main(sys.argv[1:]))
