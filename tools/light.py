# usage: light.py theme.json
# Gives the theme a real light appearance: writes variants.light and the "Light mode" CSS block.
# T3 Code drops the `dark` class from <html> in light mode, so every rule here is scoped to html:not(.dark).
# Safe to re-run: it replaces its own block, which sits just before "/* Ship alert states" so alerts.py keeps it.
import json, re, sys

START = '/* Light mode'
END = '/* End light mode */\n'
L = 'html:not(.dark)'

# Every light-mode colour comes from these tokens. Swap them to retune the whole light look.
TOKENS = {
    'bg': '#E8EDF5',          # canvas, sidebar, starfield: pale cool grey
    'panel': '#F7F9FC',       # composer, details card, tooltips
    'card': 'rgba(248,250,253,.94)',  # assistant messages and the working card
    'raised': '#EEF2F8',      # T3 raised surfaces, code blocks
    'hover': '#E2E7F0',
    'line': '#C6CDDA',
    'ink': '#12141B', 'muted': '#464C5E', 'faint': '#7B8194',
    'tint': '#E9E7F5',        # working / waiting sidebar cards
    'track': '#D2D8E4',       # empty meter segments, standby off-cells
    'glass': '236,240,246',   # terminal and right-panel glass (rgb)
    'stars': ('24,27,40', '30,60,120', '120,70,20'),
    'orange': '#F28C00', 'peach': '#F0A868', 'lav': '#8E62AA', 'violet': '#7676E8', 'blue': '#4F94DE', 'gold': '#E0A21A',
}


def palette(T):
    bg, ink, muted = T['bg'], T['ink'], T['muted']
    return {
        'canvas': bg, 'chrome': bg, 'toolbar': bg, 'toolbarForeground': '#A65A00', 'toolbarBorder': bg,
        'toolbarControl': T['hover'], 'toolbarControlForeground': ink, 'toolbarControlHover': T['line'],
        'surface': bg, 'surfaceRaised': T['raised'], 'surfaceOverlay': T['panel'], 'text': ink, 'textMuted': muted,
        'border': T['line'], 'input': T['line'], 'focus': T['orange'], 'accent': T['orange'], 'accentForeground': '#000000',
        'secondary': T['hover'], 'secondaryForeground': ink, 'muted': T['hover'], 'mutedForeground': muted,
        'placeholder': T['faint'], 'secondaryLabel': '#2F6FB0', 'iconMuted': muted,
        'error': '#C83434', 'errorForeground': '#FFFFFF', 'errorSurface': '#F6DEDE',
        'warning': '#A87800', 'warningForeground': '#000000', 'warningSurface': '#F5EDD2',
        'update': '#2F6FB0', 'updateForeground': '#FFFFFF', 'updateSurface': '#DDE7F3',
        'accentSurface': '#F7E3C8', 'accentSurfaceForeground': '#7A4200', 'messageSurface': T['tint'],
        'messageForeground': ink, 'messageAction': T['orange'], 'messageActionForeground': '#000000',
        'messageActionHover': T['peach'], 'codeBackground': T['raised'], 'codeForeground': '#1F4F80',
        'searchMatchBackground': '#FFD970', 'searchMatchForeground': '#000000',
        'searchMatchActiveBackground': T['orange'], 'searchMatchActiveForeground': '#000000',
        'sidebar': bg, 'sidebarForeground': ink, 'sidebarMutedForeground': muted, 'sidebarControlSurface': T['hover'],
        'sidebarRowHover': T['hover'], 'sidebarRowActive': T['orange'], 'sidebarRowSelected': T['tint'], 'sidebarBorder': bg,
        # The terminal canvas multiplies onto the glass below it, so white drops out.
        'terminalBackground': '#FFFFFF', 'terminalForeground': ink, 'terminalCursor': T['orange'],
        'terminalSelection': '#D9CDEA', 'terminalScrollbar': T['lav'], 'terminalScrollbarHover': T['orange'],
    }


# Star colours live in three channel variables (white, blue-white, warm) so light mode only swaps them.
STAR_VARS = {'255,255,255': '--lc-s1', '204,228,255': '--lc-s2', '255,232,204': '--lc-s3'}
STAR_HEX = {'ffffff': '--lc-s1', 'cce4ff': '--lc-s2', 'ffe8cc': '--lc-s3'}


def star_vars(css):
    """Rewrite literal star colours as rgb(var(--lc-sN)/alpha). Idempotent; the dark look is unchanged."""
    for rgb, v in STAR_VARS.items():
        css = re.sub(r'rgba\(' + rgb + r',([0-9.]+)\)', lambda m: f'rgb(var({v})/{float(m.group(1)):.2f})', css)
    for hx, v in STAR_HEX.items():
        css = re.sub('#' + hx + r'([0-9a-f]{2})\b', lambda m: f'rgb(var({v})/{int(m.group(1), 16) / 255:.2f})', css, flags=re.I)
    if '--lc-s1:' not in css:
        css = css.replace(':root{--lc-orange:', ':root{--lc-s1:255 255 255;--lc-s2:204 228 255;--lc-s3:255 232 204;--lc-orange:', 1)
    return css


def ink(var, pct=62):
    """Text in an LCARS colour, darkened so it reads on the light background and still follows the alert palette."""
    return f'color-mix(in srgb,var({var}) {pct}%,#000)'


ROW = '[data-sidebar-row]'
SEL = '[data-sidebar-row][aria-current]:not([aria-current="false"])'
H, Y, R = '.lucide-message-circle-question-mark', '.lucide-shield-question-mark', '.lucide-circle-alert'


def block(T=TOKENS):
    bg, panel, fg = T['bg'], T['panel'], T['ink']
    s1, s2, s3 = T['stars']
    return f'''{START}: grey console. T3 Code removes html.dark in light appearance; regenerate with tools/light.py. */
{L}{{--lc-orange:{T['orange']};--lc-peach:{T['peach']};--lc-lav:{T['lav']};--lc-violet:{T['violet']};--lc-blue:{T['blue']};--lc-gold:{T['gold']};--lc-term-glass:rgba({T['glass']},.80);--lc-panel-glass:rgba({T['glass']},.86);}}
{L} ::selection{{background:color-mix(in srgb,var(--lc-lav) 34%,transparent);}}
/* Ink starfield on grey */
{L}{{--lc-s1:{s1.replace(',',' ')};--lc-s2:{s2.replace(',',' ')};--lc-s3:{s3.replace(',',' ')};}}
{L} [data-slot="sidebar-wrapper"],{L} [data-thread-terminal-drawer]{{background-color:{bg} !important;}}
{L} [data-thread-terminal-drawer] canvas{{mix-blend-mode:multiply;}}
/* Header rail: background-coloured gaps between the segments */
{L} [data-chat-header]{{border-image:linear-gradient(90deg,var(--lc-orange) 0 40%,{bg} 40% 40.6%,var(--lc-peach) 40.6% 60%,{bg} 60% 60.6%,var(--lc-lav) 60.6% 82%,{bg} 82% 82.6%,var(--lc-violet) 82.6% 100%) 1 !important;}}
/* Panels: light grey instead of deep space */
{L} [data-message-role="assistant"] .chat-markdown,{L} [data-timeline-row-kind="working"],{L} [data-timeline-row-kind="working"] ~ [data-timeline-row-kind]{{background:{T['card']};}}
{L} [data-slot="composer-host"],{L} [data-composer-command-drawer],{L} [data-thread-details-card]{{background:{panel} !important;}}
{L} [data-slot="tooltip-popup"]{{background:{panel} !important;color:{fg} !important;}}
{L} [data-message-role="user"] :has(> button[aria-label^="Preview "]){{background:{panel} !important;box-shadow:none;}}
/* LCARS-coloured text, darkened to read on grey */
{L} .chat-markdown :is(h1,h2,h3,h4){{color:{ink('--lc-orange', 78)} !important;}}
{L} .chat-markdown strong{{color:{ink('--lc-orange', 74)} !important;}}
{L} .chat-markdown a{{color:{ink('--lc-blue', 72)} !important;}}
{L} [data-surface-launcher-keys] h3,{L} [data-thread-details-card] [tabindex="0"][aria-label*=": "] > span:last-child,{L} {ROW} .text-info-foreground{{color:{ink('--lc-orange', 72)} !important;}}
{L} [data-thread-details-card] [tabindex="0"][aria-label*=": "] > span:first-child{{color:{ink('--lc-peach', 55)} !important;}}
{L} [data-thread-details-card] svg{{color:{ink('--lc-lav', 80)} !important;}}
{L} button.bg-message-action:disabled,{L} [data-pending-user-input-toggle],{L} [data-pending-user-input-toggle] *{{color:{ink('--lc-orange', 72)} !important;}}
{L} {ROW} :is(span,div):has(> {H}){{color:#1F78A8 !important;}}
/* Tabs and launcher keys: tinted panels, ink labels */
{L} [data-right-panel-tab-list] [data-active-tab]{{background:color-mix(in srgb,var(--lc-lav) 26%,{panel}) !important;color:{fg} !important;}}
{L} [data-right-panel-tab-list] [data-active-tab]:hover{{background:color-mix(in srgb,var(--lc-lav) 48%,{panel}) !important;}}
{L} [data-right-panel-tab-list] [data-active-tab="true"],{L} [data-right-panel-tab-list] [data-active-tab="true"] *{{color:#000 !important;}}
{L} :is([data-surface-launcher-keys] .flex-col > [data-slot="tooltip-trigger"],[data-surface-launcher-keys] .flex-col > .group > button:first-child){{background:color-mix(in srgb,var(--lc-row,var(--lc-orange)) 18%,{panel}) !important;color:{fg} !important;}}
{L} :is([data-surface-launcher-keys] .flex-col > .group > button:first-child):is(:hover,:focus-visible){{background:var(--lc-row,var(--lc-orange)) !important;color:#000 !important;}}
{L} [data-surface-launcher-keys] .flex-col > .group > button:not(:first-child){{color:{fg} !important;}}
/* Autocomplete rows and details-card hovers */
{L} [data-composer-item-id]:not([data-active]){{color:{fg} !important;}}
{L} [data-composer-item-id]:not([data-active]):hover,{L} [data-thread-details-card] :is(button,a,[role="button"],[data-slot="button"]):hover{{background-color:{T['hover']} !important;}}
{L} [data-thread-details-card] [tabindex="0"][aria-label*=": "] > span.relative{{background:repeating-linear-gradient(90deg,{T['track']} 0 9px,transparent 9px 12px) !important;}}
/* Sidebar status cards: pale tints, endcaps blink to a pale tone instead of to black */
@keyframes lc-cap-cycle-l{{0%,49.9%{{box-shadow:inset -8px 0 0 {T['orange']}}}50%,100%{{box-shadow:inset -8px 0 0 #F2C58A}}}}
@keyframes lc-cap-cycle-sel-l{{0%,49.9%{{box-shadow:inset -8px 0 0 #B35F00}}50%,100%{{box-shadow:inset -8px 0 0 #6B3500}}}}
@keyframes lc-standby-l{{0%,49.9%{{--lc-c1:{T['violet']};--lc-c2:{T['track']}}}50%,100%{{--lc-c1:{T['track']};--lc-c2:{T['violet']}}}}}
@keyframes lc-wait-cap-l{{0%,49.9%{{box-shadow:inset -8px 0 0 {T['violet']}}}50%,100%{{box-shadow:inset -8px 0 0 {T['track']}}}}}
{L} {ROW}:is(:has(.text-info-foreground),:has(.lucide-circle-dot-dashed)):not([aria-current="page"]):not([aria-current="true"]){{background-color:{T['tint']} !important;}}
/* Working cards: one segmented meter (same cells as the waiting card), two levels jumping independently */
{L} {ROW}:has(.text-info-foreground){{background-image:repeating-linear-gradient(90deg,transparent 0 calc(12.5% - 4px),{T['tint']} calc(12.5% - 4px) 12.5%),linear-gradient(var(--lc-orange),var(--lc-orange)),linear-gradient(var(--lc-violet),var(--lc-violet)),linear-gradient({T['track']},{T['track']}) !important;background-size:calc(100% - 28px) 3px,var(--lc-a) 3px,var(--lc-b) 3px,calc(100% - 28px) 3px !important;background-position:14px calc(100% - 4px) !important;background-repeat:no-repeat !important;animation:lc-meter-a 3.2s steps(4,jump-none) infinite,lc-meter-b 2.6s steps(3,jump-none) infinite,lc-cap-cycle-l 1.6s infinite !important;}}
{L} {ROW}:has(.lucide-circle-dot-dashed){{animation:lc-standby-l 2s infinite,lc-wait-cap-l 2s infinite !important;}}
/* Selected card: a pale tint of the accent with a solid endcap, so its text keeps the normal ink colours */
{L} {SEL}{{background:color-mix(in srgb,var(--lc-orange) 24%,{panel}) !important;box-shadow:inset -8px 0 0 var(--lc-orange) !important;}}
{L} {SEL},{L} {SEL} *{{color:revert-layer !important;}}
{L} {SEL}:has(.text-info-foreground){{background-color:color-mix(in srgb,var(--lc-orange) 24%,{panel}) !important;background-image:repeating-linear-gradient(90deg,transparent 0 calc(12.5% - 4px),color-mix(in srgb,var(--lc-orange) 24%,{panel}) calc(12.5% - 4px) 12.5%),linear-gradient(var(--lc-orange),var(--lc-orange)),linear-gradient(var(--lc-violet),var(--lc-violet)),linear-gradient({T['track']},{T['track']}) !important;background-size:calc(100% - 28px) 3px,var(--lc-a) 3px,var(--lc-b) 3px,calc(100% - 28px) 3px !important;background-position:14px calc(100% - 4px) !important;background-repeat:no-repeat !important;animation:lc-meter-a 3.2s steps(4,jump-none) infinite,lc-meter-b 2.6s steps(3,jump-none) infinite,lc-cap-cycle-l 1.6s infinite !important;}}
{L} {SEL} .text-info-foreground{{color:{ink('--lc-orange', 72)} !important;}}
{L} {SEL} :is(span,div):has(> {H}){{color:#1F78A8 !important;}}
{L} {SEL}:has(.lucide-circle-dot-dashed){{background-color:color-mix(in srgb,var(--lc-orange) 24%,{panel}) !important;animation:lc-standby-l 2s infinite,lc-wait-cap-l 2s infinite !important;}}
/* Alerts on grey: deeper hues so the bars hold up against the light background */
{L}:has({ROW} {H}){{--lc-orange:#1E9BD7;--lc-peach:#6EC3EA;--lc-lav:#3F68B0;--lc-violet:#5B86E8;--lc-blue:#1C7FB8;--lc-gold:#2BB3C4;--lc-glow:rgba(30,140,230,.18);--lc-stop:#1E9BD7;}}
@keyframes lc-hail-cap-l{{0%,100%{{box-shadow:inset -8px 0 0 #1E9BD7}}50%{{box-shadow:inset -8px 0 0 #A8D8F0}}}}
{L} {ROW}:has({H}){{background-color:#D8E8F4 !important;animation:lc-hail-cap-l 2s ease-in-out infinite !important;}}
{L} {SEL}:has({H}){{background:color-mix(in srgb,#1E9BD7 24%,{panel}) !important;animation:lc-hail-cap-l 2s ease-in-out infinite !important;}}
{L}:has({ROW} {Y}){{--lc-orange:#E0A000;--lc-peach:#EEC04A;--lc-lav:#A88412;--lc-violet:#D9AE1F;--lc-blue:#9A7A00;--lc-gold:#D49B00;--lc-glow:rgba(230,170,0,.24);--lc-stop:#E0A000;}}
@keyframes lc-yellow-cap-l{{0%,100%{{box-shadow:inset -8px 0 0 #E0A000}}50%{{box-shadow:inset -8px 0 0 #F2DC94}}}}
{L} {ROW}:has({Y}){{background-color:#F2EACB !important;animation:lc-yellow-cap-l 2.4s ease-in-out infinite !important;}}
{L} {SEL}:has({Y}){{background:color-mix(in srgb,#E0A000 24%,{panel}) !important;animation:lc-yellow-cap-l 2.4s ease-in-out infinite !important;}}
{L}:has({ROW} {R}){{--lc-orange:#E02828;--lc-peach:#F08080;--lc-lav:#A02C2C;--lc-violet:#E84A4A;--lc-blue:#C03030;--lc-gold:#E05555;--lc-glow:rgba(230,30,30,.18);--lc-stop:#E02828;}}
@keyframes lc-red-cap-l{{0%,49.9%{{box-shadow:inset -8px 0 0 #E02828}}50%,100%{{box-shadow:inset -8px 0 0 #F2A8A8}}}}
{L} {ROW}:has({R}){{background-color:#F2D8D8 !important;animation:lc-red-cap-l 1.2s infinite !important;}}
{L} {SEL}:has({R}){{background:color-mix(in srgb,#E02828 24%,{panel}) !important;animation:lc-red-cap-l 1.2s infinite !important;}}
@media (prefers-reduced-motion:reduce){{{L} {ROW}{ROW}{{animation:none !important;}}}}
{END}'''


def strip(css):
    if START in css:
        css = css[:css.index(START)] + css[css.index(END) + len(END):]
    return css


if __name__ == '__main__':
    p = sys.argv[1]
    t = json.load(open(p))
    css = star_vars(strip(t['css']))
    marker = '/* Ship alert states'
    at = css.index(marker)
    t['css'] = css[:at] + block() + css[at:]
    t['variants'] = {**t.get('variants', {}), 'light': palette(TOKENS)}
    json.dump(t, open(p, 'w'), indent=2)
    print('ok', p)
