# usage: light.py theme.json
# Gives the theme a real light appearance: writes variants.light and the "Light mode" CSS block.
# T3 Code drops the `dark` class from <html> in light mode, so every rule here is scoped to html:not(.dark).
# Safe to re-run: it replaces its own block, which sits just before "/* Ship alert states" so alerts.py keeps it.
import json, re, sys

START = '/* Light mode'
END = '/* End light mode */\n'
L = 'html:not(.dark)'

PALETTE = {
    'canvas': '#F4EEE4', 'chrome': '#F4EEE4', 'toolbar': '#F4EEE4', 'toolbarForeground': '#A65A00',
    'toolbarBorder': '#F4EEE4', 'toolbarControl': '#EADFD0', 'toolbarControlForeground': '#4A3020',
    'toolbarControlHover': '#E2D3C0', 'surface': '#F4EEE4', 'surfaceRaised': '#FBF7F0',
    'surfaceOverlay': '#FBF7F0', 'text': '#1E1B2E', 'textMuted': '#5E5A80', 'border': '#D8CDBE',
    'input': '#D8CDBE', 'focus': '#E07800', 'accent': '#F28C00', 'accentForeground': '#000000',
    'secondary': '#EAE2D6', 'secondaryForeground': '#1E1B2E', 'muted': '#EDE5D9',
    'mutedForeground': '#5E5A80', 'placeholder': '#8A86A8', 'secondaryLabel': '#2F6FB0',
    'iconMuted': '#5E5A80', 'error': '#C83434', 'errorForeground': '#FFFFFF', 'errorSurface': '#FBE0DC',
    'warning': '#A87800', 'warningForeground': '#000000', 'warningSurface': '#FBF0CF',
    'update': '#2F6FB0', 'updateForeground': '#FFFFFF', 'updateSurface': '#DDEBF8',
    'accentSurface': '#FBE3C2', 'accentSurfaceForeground': '#7A4200', 'messageSurface': '#EFE4F1',
    'messageForeground': '#1E1B2E', 'messageAction': '#F28C00', 'messageActionForeground': '#000000',
    'messageActionHover': '#F5A640', 'codeBackground': '#FBF7F0', 'codeForeground': '#1F4F80',
    'searchMatchBackground': '#FFD970', 'searchMatchForeground': '#000000',
    'searchMatchActiveBackground': '#F28C00', 'searchMatchActiveForeground': '#000000',
    'sidebar': '#F4EEE4', 'sidebarForeground': '#1E1B2E', 'sidebarMutedForeground': '#5E5A80',
    'sidebarControlSurface': '#EAE2D6', 'sidebarRowHover': '#EBDFD0', 'sidebarRowActive': '#F28C00',
    'sidebarRowSelected': '#E8DCEC', 'sidebarBorder': '#F4EEE4',
    # The terminal canvas multiplies onto the glass below it, so white drops out.
    'terminalBackground': '#FFFFFF', 'terminalForeground': '#3A2A1A', 'terminalCursor': '#E07800',
    'terminalSelection': '#E3C8EC', 'terminalScrollbar': '#B784C0', 'terminalScrollbarHover': '#F28C00',
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
    """Text in an LCARS colour, darkened so it reads on the parchment and still follows the alert palette."""
    return f'color-mix(in srgb,var({var}) {pct}%,#000)'


ROW = '[data-sidebar-row]'
SEL = '[data-sidebar-row][aria-current]:not([aria-current="false"])'
H, Y, R = '.lucide-message-circle-question-mark', '.lucide-shield-question-mark', '.lucide-circle-alert'


def block():
    return f'''{START}: parchment console. T3 Code removes html.dark in light appearance; regenerate with tools/light.py. */
{L}{{--lc-orange:#F28C00;--lc-peach:#F2B272;--lc-lav:#B784C0;--lc-violet:#7F7FEA;--lc-blue:#5C9EE0;--lc-gold:#E6AE1A;--lc-term-glass:rgba(251,247,240,.80);--lc-panel-glass:rgba(251,247,240,.86);}}
{L} ::selection{{background:color-mix(in srgb,var(--lc-lav) 34%,transparent);}}
/* Ink starfield on parchment */
{L}{{--lc-s1:28 30 60;--lc-s2:30 70 140;--lc-s3:150 80 10;}}
{L} [data-slot="sidebar-wrapper"],{L} [data-thread-terminal-drawer]{{background-color:#F4EEE4 !important;}}
{L} [data-thread-terminal-drawer] canvas{{mix-blend-mode:multiply;}}
/* Header rail: parchment gaps between the segments */
{L} [data-chat-header]{{border-image:linear-gradient(90deg,var(--lc-orange) 0 40%,#F4EEE4 40% 40.6%,var(--lc-peach) 40.6% 60%,#F4EEE4 60% 60.6%,var(--lc-lav) 60.6% 82%,#F4EEE4 82% 82.6%,var(--lc-violet) 82.6% 100%) 1 !important;}}
/* Panels: warm paper instead of deep space */
{L} [data-message-role="assistant"] .chat-markdown,{L} [data-timeline-row-kind="working"],{L} [data-timeline-row-kind="working"] ~ [data-timeline-row-kind]{{background:rgba(255,252,246,.94);}}
{L} [data-slot="composer-host"],{L} [data-composer-command-drawer],{L} [data-thread-details-card]{{background:#FFFDF8 !important;}}
{L} [data-slot="tooltip-popup"]{{background:#FFFDF8 !important;color:#1E1B2E !important;}}
{L} [data-message-role="user"] :has(> button[aria-label^="Preview "]){{background:#FFFDF8 !important;box-shadow:none;}}
/* LCARS-coloured text, darkened to read on paper */
{L} .chat-markdown :is(h1,h2,h3,h4){{color:{ink('--lc-orange', 78)} !important;}}
{L} .chat-markdown strong{{color:{ink('--lc-gold', 58)} !important;}}
{L} .chat-markdown a{{color:{ink('--lc-blue', 72)} !important;}}
{L} [data-surface-launcher-keys] h3,{L} [data-thread-details-card] [tabindex="0"][aria-label*=": "] > span:last-child,{L} {ROW} .text-info-foreground{{color:{ink('--lc-orange', 72)} !important;}}
{L} [data-thread-details-card] [tabindex="0"][aria-label*=": "] > span:first-child{{color:{ink('--lc-peach', 55)} !important;}}
{L} [data-thread-details-card] svg{{color:{ink('--lc-lav', 80)} !important;}}
{L} button.bg-message-action:disabled,{L} [data-pending-user-input-toggle],{L} [data-pending-user-input-toggle] *{{color:{ink('--lc-orange', 72)} !important;}}
{L} {ROW} :is(span,div):has(> {H}){{color:#1F78A8 !important;}}
/* Tabs and launcher keys: tinted paper, ink labels */
{L} [data-right-panel-tab-list] [data-active-tab]{{background:color-mix(in srgb,var(--lc-lav) 26%,#FFFDF8) !important;color:#3A2A40 !important;}}
{L} [data-right-panel-tab-list] [data-active-tab]:hover{{background:color-mix(in srgb,var(--lc-lav) 48%,#FFFDF8) !important;}}
{L} [data-right-panel-tab-list] [data-active-tab="true"],{L} [data-right-panel-tab-list] [data-active-tab="true"] *{{color:#000 !important;}}
{L} :is([data-surface-launcher-keys] .flex-col > [data-slot="tooltip-trigger"],[data-surface-launcher-keys] .flex-col > .group > button:first-child){{background:color-mix(in srgb,var(--lc-row,var(--lc-orange)) 18%,#FFFDF8) !important;color:#3A2A1A !important;}}
{L} :is([data-surface-launcher-keys] .flex-col > .group > button:first-child):is(:hover,:focus-visible){{background:var(--lc-row,var(--lc-orange)) !important;color:#000 !important;}}
{L} [data-surface-launcher-keys] .flex-col > .group > button:not(:first-child){{color:#3A2A1A !important;}}
/* Autocomplete rows and details-card hovers */
{L} [data-composer-item-id]:not([data-active]){{color:#1E1B2E !important;}}
{L} [data-composer-item-id]:not([data-active]):hover,{L} [data-thread-details-card] :is(button,a,[role="button"],[data-slot="button"]):hover{{background-color:#F3E6D6 !important;}}
{L} [data-thread-details-card] [tabindex="0"][aria-label*=": "] > span.relative{{background:repeating-linear-gradient(90deg,#E4DAEC 0 9px,transparent 9px 12px) !important;}}
/* Sidebar status cards: pale tints, endcaps blink to a pale tone instead of to black */
@keyframes lc-cap-cycle-l{{0%,49.9%{{box-shadow:inset -8px 0 0 #F28C00}}50%,100%{{box-shadow:inset -8px 0 0 #F7CF94}}}}
@keyframes lc-standby-l{{0%,49.9%{{--lc-c1:#7F7FEA;--lc-c2:#D6D6F4}}50%,100%{{--lc-c1:#D6D6F4;--lc-c2:#7F7FEA}}}}
@keyframes lc-wait-cap-l{{0%,49.9%{{box-shadow:inset -8px 0 0 #7F7FEA}}50%,100%{{box-shadow:inset -8px 0 0 #CACAF0}}}}
{L} {ROW}:is(:has(.text-info-foreground),:has(.lucide-circle-dot-dashed)):not([aria-current="page"]):not([aria-current="true"]){{background-color:#EFE6F2 !important;}}
{L} {ROW}:has(.text-info-foreground){{background-image:linear-gradient(90deg,#FF9966 0 18px,#F28C00 18px),linear-gradient(90deg,#B784C0 0 18px,#7F7FEA 18px),repeating-linear-gradient(90deg,#00000022 0 1px,transparent 1px 12.5%) !important;animation:lc-meter-a 3.2s steps(4,jump-none) infinite,lc-meter-b 2.6s steps(3,jump-none) infinite,lc-cap-cycle-l 1.6s infinite !important;}}
{L} {ROW}:has(.lucide-circle-dot-dashed){{animation:lc-standby-l 2s infinite,lc-wait-cap-l 2s infinite !important;}}
{L} {SEL}:has(.text-info-foreground){{background-image:linear-gradient(90deg,#7A3D00 0 18px,#000 18px),linear-gradient(90deg,#7A3D00 0 18px,#4A2600 18px),repeating-linear-gradient(90deg,#00000033 0 1px,transparent 1px 12.5%) !important;animation:lc-meter-a 3.2s steps(4,jump-none) infinite,lc-meter-b 2.6s steps(3,jump-none) infinite,lc-cap-cycle-sel 1.6s infinite !important;}}
{L} {SEL}:has(.lucide-circle-dot-dashed){{animation:lc-standby-sel 2s infinite,lc-wait-cap-sel 2s infinite !important;}}
/* Alerts on paper: deeper hues so the bars hold up against the light background */
{L}:has({ROW} {H}){{--lc-orange:#1E9BD7;--lc-peach:#6EC3EA;--lc-lav:#3F68B0;--lc-violet:#5B86E8;--lc-blue:#1C7FB8;--lc-gold:#2BB3C4;--lc-glow:rgba(30,140,230,.18);--lc-stop:#1E9BD7;}}
@keyframes lc-hail-cap-l{{0%,100%{{box-shadow:inset -8px 0 0 #1E9BD7}}50%{{box-shadow:inset -8px 0 0 #A8D8F0}}}}
{L} {ROW}:has({H}){{background-color:#DCEFFB !important;animation:lc-hail-cap-l 2s ease-in-out infinite !important;}}
{L} {SEL}:has({H}){{background-color:#1E9BD7 !important;}}
{L}:has({ROW} {Y}){{--lc-orange:#E0A000;--lc-peach:#EEC04A;--lc-lav:#A88412;--lc-violet:#D9AE1F;--lc-blue:#9A7A00;--lc-gold:#D49B00;--lc-glow:rgba(230,170,0,.24);--lc-stop:#E0A000;}}
@keyframes lc-yellow-cap-l{{0%,100%{{box-shadow:inset -8px 0 0 #E0A000}}50%{{box-shadow:inset -8px 0 0 #F2DC94}}}}
{L} {ROW}:has({Y}){{background-color:#FBF0C8 !important;animation:lc-yellow-cap-l 2.4s ease-in-out infinite !important;}}
{L} {SEL}:has({Y}){{background-color:#E0A000 !important;}}
{L}:has({ROW} {R}){{--lc-orange:#E02828;--lc-peach:#F08080;--lc-lav:#A02C2C;--lc-violet:#E84A4A;--lc-blue:#C03030;--lc-gold:#E05555;--lc-glow:rgba(230,30,30,.18);--lc-stop:#E02828;}}
@keyframes lc-red-cap-l{{0%,49.9%{{box-shadow:inset -8px 0 0 #E02828}}50%,100%{{box-shadow:inset -8px 0 0 #F2A8A8}}}}
{L} {ROW}:has({R}){{background-color:#FBDCDC !important;animation:lc-red-cap-l 1.2s infinite !important;}}
{L} {SEL}:has({R}){{background-color:#E02828 !important;}}
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
    t['variants'] = {**t.get('variants', {}), 'light': PALETTE}
    json.dump(t, open(p, 'w'), indent=2)
    print('ok', p)
