# usage: alerts.py theme.json [hail_icon yellow_icon red_icon]
import json,sys
p=sys.argv[1]
hail,yellow,red=(sys.argv[2:5] if len(sys.argv)>4 else ('message-circle-question-mark','shield-question-mark','circle-alert'))
t=json.load(open(p)); c=t['css']
for marker in ('/* Auto red alert','/* Ship alert states'):
    if marker in c: c=c[:c.index(marker)]
H=f'.lucide-{hail}'; Y=f'.lucide-{yellow}'; R=f'.lucide-{red}'
row='[data-sidebar-row]'; sel='[data-sidebar-row][aria-current]:not([aria-current="false"])'
def has(i): return f':root:has({row} {i})'
c+=f'''/* Ship alert states (fade 1.6s): Input = incoming hail (blue), Approval = yellow alert (amber), Failed = red alert. Most severe wins. */
@property --lc-orange{{syntax:"<color>";inherits:true;initial-value:#FF9900;}}
@property --lc-peach{{syntax:"<color>";inherits:true;initial-value:#FFCC99;}}
@property --lc-lav{{syntax:"<color>";inherits:true;initial-value:#CC99CC;}}
@property --lc-violet{{syntax:"<color>";inherits:true;initial-value:#9999FF;}}
@property --lc-blue{{syntax:"<color>";inherits:true;initial-value:#99CCFF;}}
@property --lc-gold{{syntax:"<color>";inherits:true;initial-value:#FFCC66;}}
@property --lc-glow{{syntax:"<color>";inherits:true;initial-value:rgba(0,0,0,0);}}
@property --lc-p{{syntax:"<number>";inherits:true;initial-value:1;}}
:root{{transition:--lc-orange 1.6s ease,--lc-peach 1.6s ease,--lc-lav 1.6s ease,--lc-violet 1.6s ease,--lc-blue 1.6s ease,--lc-gold 1.6s ease,--lc-glow 1.6s ease;}}
@keyframes lc-breathe{{0%,100%{{--lc-p:1}}50%{{--lc-p:.4}}}}
/* App buttons that use the message-action color (Submit, send) follow the alert palette */
:root{{--message-action:var(--lc-orange) !important;--message-action-hover:var(--lc-peach) !important;}}
/* (alert glow frames the chat: an inset glow on [data-workspace-area="conversation"]; see base CSS) */

/* Incoming hail */
{has(H)}{{--lc-orange:#4FC3F7;--lc-peach:#B3E5FC;--lc-lav:#5C7FC2;--lc-violet:#7FA8FF;--lc-blue:#C8F0FF;--lc-gold:#80DEEA;--lc-glow:rgba(70,170,255,.16);--lc-stop:#4FC3F7;animation:lc-breathe 3s ease-in-out infinite;}}
@keyframes lc-hail-cap{{0%,100%{{box-shadow:inset -8px 0 0 #4FC3F7}}50%{{box-shadow:inset -8px 0 0 #123A5A}}}}
{row}:has({H}){{background-color:#0A1A2A !important;animation:lc-hail-cap 2s ease-in-out infinite !important;}}
{sel}:has({H}){{background-color:#4FC3F7 !important;animation:lc-hail-cap 2s ease-in-out infinite !important;}}

/* Yellow alert */
{has(Y)}{{--lc-orange:#FFB300;--lc-peach:#FFE082;--lc-lav:#C9A227;--lc-violet:#FFD54F;--lc-blue:#FFF1B8;--lc-gold:#FFCA28;--lc-glow:rgba(255,190,0,.24);--lc-stop:#FFB300;animation:lc-breathe 3.5s ease-in-out infinite;}}
@keyframes lc-yellow-cap{{0%,100%{{box-shadow:inset -8px 0 0 #FFB300}}50%{{box-shadow:inset -8px 0 0 #5A4000}}}}
@keyframes lc-yellow-cap-sel{{0%,100%{{box-shadow:inset -8px 0 0 #B37D00}}50%{{box-shadow:inset -8px 0 0 #FFE9A8}}}}
{row}:has({Y}){{background-color:#2A2200 !important;animation:lc-yellow-cap 2.4s ease-in-out infinite !important;}}
{sel}:has({Y}){{background-color:#FFB300 !important;animation:lc-yellow-cap-sel 2.4s ease-in-out infinite !important;}}

/* Red alert */
{has(R)}{{--lc-orange:#FF3333;--lc-peach:#FF9E9E;--lc-lav:#B33A3A;--lc-violet:#FF5C5C;--lc-blue:#FFB0B0;--lc-gold:#FF7070;--lc-glow:rgba(255,30,30,.2);--lc-stop:#FF3333;animation:lc-breathe 4s ease-in-out infinite;}}
@keyframes lc-red-cap{{0%,49.9%{{box-shadow:inset -8px 0 0 #FF3333}}50%,100%{{box-shadow:inset -8px 0 0 #5A0000}}}}
{row}:has({R}){{background-color:#2A0808 !important;animation:lc-red-cap 1.2s infinite !important;}}
{sel}:has({R}){{background-color:#FF3333 !important;animation:lc-red-cap 1.2s infinite !important;}}

@media (prefers-reduced-motion:reduce){{:root{{transition:none !important;animation:none !important;}}{row}{row}:is(:has({H}),:has({Y}),:has({R})){{animation:none !important;}}}}
'''
t['css']=c; json.dump(t,open(p,'w'),indent=2); print('ok',hail,yellow,red)
