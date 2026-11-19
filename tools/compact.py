# usage: python3 tools/compact.py
# Builds themes/compact/ for T3 Code builds that cap theme CSS at 50,000 characters (Stable 0.1.10
# and nightlies before 0.1.11-nightly.20261117.4825). LCARS needs about 83,000, so each build drops
# one feature and install.sh lets the user pick:
#   lcars-dark.json      dark only (light appearance shows the dark console), with Antonio
#   lcars-nofont.json    light and dark, in the system's condensed font instead of Antonio
#   lcars-red-alert.json the red alert variant (already dark only), with Antonio
# The rest is the same CSS, minified: comments and spaces go, --lc-* variables and keyframes get
# short names, rules sharing a selector prefix are nested, and starfield layers are reordered so one
# short background-size list repeats. Antonio comes from fonts/antonio-compact.woff2, an ASCII subset:
#   pyftsubset fonts/antonio.woff2 --unicodes="U+0020-007E,U+2013-2014,U+2018-201D,U+2026,U+00B7" \
#     --flavor=woff2 --layout-features='' --no-hinting --desubroutinize --name-IDs='' \
#     --drop-tables+=STAT,gasp,GDEF,GPOS,GSUB --no-glyph-names --notdef-outline \
#     --output-file=fonts/antonio-compact.woff2
# Re-run after changing themes/*.json. It fails if a build goes over the cap.
import base64, json, os, re, sys

CAP = 50_000
BUILDS = [  # source theme, mode, output in themes/compact/
    ('lcars.json', 'dark', 'lcars-dark.json'),
    ('lcars.json', 'nofont', 'lcars-nofont.json'),
    ('lcars-red-alert.json', 'dark', 'lcars-red-alert.json'),  # dark only already
]
LIGHT_START, LIGHT_END = '/* Light mode', '/* End light mode */'
DARK = 'html:not(.dark)'


def protect(css):
    """Swap strings and data URLs for placeholders so the minifier cannot touch them."""
    keep = []

    def stash(m):
        keep.append(m.group(0))
        return f'\x00{len(keep) - 1}\x00'

    return re.sub(r'url\(data:[^)]*\)|"[^"]*"|\'[^\']*\'', stash, css), keep


def restore(css, keep):
    return re.sub(r'\x00(\d+)\x00', lambda m: keep[int(m.group(1))], css)


def split_top(s, sep):
    """Split on sep outside parentheses and brackets."""
    out, depth, cur = [], 0, ''
    for ch in s:
        depth += ch in '([' and 1 or ch in ')]' and -1 or 0
        if ch == sep and depth == 0:
            out.append(cur)
            cur = ''
        else:
            cur += ch
    return out + [cur]


def statements(css):
    """Top-level statements of minified CSS, each with its braces."""
    out, depth, start = [], 0, 0
    for i, ch in enumerate(css):
        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                out.append(css[start:i + 1])
                start = i + 1
    return out


def minify(css):
    css = re.sub(r'/\*.*?\*/', '', css, flags=re.S)
    css, keep = protect(css)
    css = re.sub(r'\s+', ' ', css)
    css = re.sub(r'\s*([{};,>~])\s*', r'\1', css)
    css = re.sub(r'\s*!important', '!important', css)
    css = re.sub(r':\s+', ':', css)
    css = re.sub(r'\(\s+', '(', css)
    css = re.sub(r'\s+\)', ')', css)
    css = css.replace(';}', '}')
    css = re.sub(r'(\d)\.0+(?!\d)', r'\1', css)            # 1.00 -> 1, 327.0px -> 327px
    css = re.sub(r'(\d\.\d*?[1-9])0+(?!\d)', r'\1', css)   # 0.50 -> 0.5
    css = re.sub(r'(?<![\w.\-#])0\.(\d)', r'.\1', css)      # 0.5 -> .5
    css = re.sub(r'\btransparent\b', '#0000', css)
    css = re.sub(r'radial-gradient\(([\d.]+px) \1 at', r'radial-gradient(\1 at', css)  # equal radii = circle
    css = re.sub(r'rgb\((var\(--[\w-]+\))/1\)', r'rgb(\1)', css)
    css = re.sub(r'at (\d+\.\d\d)% (\d+\.\d\d)%', lambda m: f'at {pct(m[1])} {pct(m[2])}', css)  # stars to 0.1%
    css = re.sub(r'#([0-9a-fA-F]{6}|[0-9a-fA-F]{8})(?![0-9a-fA-F])', short_hex, css)
    css = re.sub(r' ([*/]) ', r'\1', css)                 # calc(a * b): only + and - need spaces
    css = stars(css)
    css = shared_layers(css)
    css = rename(css)
    return restore(css, keep).strip()


def stars(css):
    """Starfield layers come as copies of one star set, each copy at its own background-size.
    Reorder them star-major so background-size can be one copy-length list that CSS repeats."""
    def fix(m):
        if '!important' in m.group(0):
            return m.group(0)
        imgs, sizes = split_top(m.group(1), ','), split_top(m.group(2), ',')
        order = list(dict.fromkeys(sizes))
        n, c = len(imgs), len(order)
        if n != len(sizes) or c < 2 or n % c:
            return m.group(0)
        k = n // c
        if sizes != [s for s in order for _ in range(k)]:
            return m.group(0)
        imgs = [imgs[copy * k + star] for star in range(k) for copy in range(c)]
        return f'background-image:{",".join(imgs)};background-size:{",".join(order)}'

    return re.sub(r'background-image:([^;{}]*radial-gradient[^;{}]*);background-size:([^;{}]*)', fix, css)


def pct(n):
    return ('%.1f' % float(n)).rstrip('0').rstrip('.') + '%'


def short_hex(m):
    h = m.group(1)
    if all(h[i] == h[i + 1] for i in range(0, len(h), 2)):
        return '#' + h[::2]
    return m.group(0)


def shared_layers(css):
    """A long gradient list used by two rules becomes one custom property set on both of them.
    Custom properties substitute var() where they are computed, so each element keeps its own
    values for any variables inside the list."""
    runs = []
    for value in re.findall(r'background-image:([^;{}]*)', css):
        items, cur = split_top(value.replace('!important', ''), ',') + [''], []
        for item in items:
            if item.startswith('radial-gradient('):
                cur.append(item)
                continue
            if len(cur) >= 5:
                runs.append(','.join(cur))
            cur = []
    for i, run in enumerate(dict.fromkeys(r for r in runs if css.count(r) == 2)):
        rules = re.findall(r'(?:^|})([^{}@]+)\{[^{}]*' + re.escape(run), css)
        if len(rules) != 2:
            continue
        name = f'--lz{i}'
        css = css.replace(run, f'var({name})')
        css += f'{",".join(rules)}{{{name}:{run}}}'
    return css


def rename(css):
    names = sorted(set(re.findall(r'--lc-[\w-]+', css)), key=lambda n: (-css.count(n), n))
    for i, name in enumerate(names):
        short = '--l' + (chr(97 + i) if i < 26 else chr(65 + i - 26))
        css = re.sub(re.escape(name) + r'(?![\w-])', short, css)
    for i, name in enumerate(sorted(set(re.findall(r'@keyframes ([\w-]+)', css)))):
        css = re.sub(r'(?<![\w-])' + re.escape(name) + r'(?![\w-])', f'lk{i}', css)
    return css


def nest_light(css):
    """Group runs of html:not(.dark) rules into one nested html:not(.dark){...} block."""
    out, run = [], []
    prefix = DARK + ' '

    def flush():
        if run:
            out.append(DARK + '{' + nest(''.join(run)) + '}')
            run.clear()

    for st in statements(css):
        sel = st[:st.index('{')]
        parts = split_top(sel, ',')
        if not sel.startswith('@') and all(p.startswith(prefix) for p in parts):
            run.append(','.join(p[len(prefix):] for p in parts) + st[len(sel):])
        else:
            flush()
            out.append(st)
    flush()
    return ''.join(out)


def combinators(sel):
    """Indexes of top-level combinators (space, >, ~, +) in a selector."""
    out, depth = [], 0
    for i, ch in enumerate(sel):
        depth += ch in '([' and 1 or ch in ')]' and -1 or 0
        if depth == 0 and ch in ' >~+':
            out.append(i)
    return out


def shared_prefix(parts):
    """Longest leading compound selector chain that every part shares, ending at a combinator."""
    best = None
    for i in combinators(parts[0]):
        p = parts[0][:i]
        if all(q.startswith(p) and i in combinators(q) for q in parts):
            best = p
    return best


def nest(css, min_prefix=10):
    """Nest runs of consecutive rules that share a selector prefix: `P a{}P b{}` -> `P{a{}b{}}`.
    Prefixes come from single selectors (no top-level comma), so :is(P) keeps P's specificity, and
    they end at a combinator, so they never hold a pseudo-element. Rule order does not change."""
    sts = statements(css)
    sels = [None if st.startswith('@') else split_top(st[:st.index('{')], ',') for st in sts]
    out, i = [], 0
    while i < len(sts):
        j, prefix, parts = i, None, list(sels[i] or [])
        while sels[i] is not None and j + 1 < len(sts) and sels[j + 1] is not None:
            p = shared_prefix(parts + sels[j + 1])
            if not p or len(p) < min_prefix:
                break
            j, prefix, parts = j + 1, p, parts + sels[j + 1]
        if prefix is None:
            out.append(sts[i])
            i += 1
            continue
        inner = ''
        for k in range(i, j + 1):
            rest = [q[len(prefix):] for q in sels[k]]
            rest = [r[1:] if r.startswith(' ') else r for r in rest]
            inner += ','.join(rest) + sts[k][sts[k].index('{'):]
        out.append(prefix + '{' + inner + '}')
        i = j + 1
    return ''.join(out)


def build(theme, mode, font):
    css = theme['css']
    css = css[css.index('\n', css.index('@font-face')) + 1:]   # the full-size Antonio @font-face
    if mode == 'dark':
        if LIGHT_START in css:
            start, end = css.index(LIGHT_START), css.index(LIGHT_END) + len(LIGHT_END)
            css = css[:start] + css[end:]
            theme['name'] += ' (dark only)'
        theme['variants'] = {**theme.get('variants', {}), 'light': dict(theme['colors'])}
    else:
        css = css.replace('"LCARS Antonio",', '')
        theme['name'] += ' (system font)'
    css = minify(css)
    if mode == 'nofont':
        css = nest_light(css)
    css = nest(css)
    if mode == 'dark':
        b64 = base64.b64encode(open(font, 'rb').read()).decode()
        css = ('@font-face{font-family:"LCARS Antonio";src:url(data:font/woff2;base64,' + b64 +
               ')format("woff2");font-weight:100 700;font-display:swap}' + css)
    theme['css'] = css
    return theme


if __name__ == '__main__':
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    font = os.path.join(root, 'fonts', 'antonio-compact.woff2')
    out = os.path.join(root, 'themes', 'compact')
    os.makedirs(out, exist_ok=True)
    over = False
    for src, mode, dst in BUILDS:
        theme = build(json.load(open(os.path.join(root, 'themes', src))), mode, font)
        n = len(theme['css'])
        with open(os.path.join(out, dst), 'w') as f:
            json.dump(theme, f, indent=2)
            f.write('\n')
        print(f'themes/compact/{dst}: {n} characters of CSS, {CAP - n} under the cap')
        over |= n > CAP
    if over:
        sys.exit(f'A compact theme is over the {CAP}-character cap. Trim the source CSS.')
