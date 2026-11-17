import json,sys,re
src,dst=sys.argv[1],sys.argv[2]
t=json.load(open(src))
m={'#FF9900':'#FF2222','#CC7A00':'#990000','#FFB366':'#FF7777','#FFB040':'#FF5555','#FFCC99':'#FFB3B3',
'#CC99CC':'#B33A3A','#9999FF':'#FF4444','#99CCFF':'#FFAAAA','#BFE0FF':'#FFD0D0','#FFCC66':'#FF6666',
'#2A1800':'#2A0505','#1A1420':'#200808','#2A1E30':'#2A0A0A','#F4E3D0':'#FFE6E6','#AFAFD8':'#D89999',
'#7A7AA0':'#A06A6A','#553377':'#661111','#1A1424':'#1F0A0A','#0D0D14':'#120505','#07070D':'#0A0303',
'#15151F':'#1A0808','#1A1A26':'#1F0A0A','#2A2A3A':'#3A1515','#0A0A12':'#0F0404','#CC99CC88':'#B33A3A88','#5A3600':'#5A0000','#FFE0B0':'#FFD0D0','#3A2400':'#3A0000','#6B3A00':'#6B0000','#8A4E00':'#8A0000','#FF9966':'#FF8080','#7A3D00':'#7A0000','#4A2600':'#4A0000','#7A4A00':'#7A0000','#FFB84D':'#FF6060','#2A2A4A':'#3A0F0F','#3A3A66':'#4A1010','#B86E00':'#B80000','#8A5200':'#8A0000'}
s=json.dumps(t).replace('rgba(255,153,0,','rgba(255,34,34,').replace('rgba(255,240,215,','rgba(255,215,215,')
for k in sorted(m,key=len,reverse=True):
    s=re.sub(re.escape(k)+r'(?![0-9A-Fa-f])',m[k],s,flags=re.I)
t=json.loads(s)
t['name']='LCARS Red Alert'
t['css']=t['css'].replace('LCARS - TNG-style theme.','LCARS Red Alert. Back to normal: switch theme to lcars.')
t['css']+='''
/* Red alert pulse */
@keyframes lc-alert-bars{0%,100%{border-color:#FF2222}50%{border-color:#5A0000}}
@keyframes lc-alert-glow{0%,100%{box-shadow:inset 0 0 140px rgba(255,20,20,.16)}50%{box-shadow:inset 0 0 60px rgba(255,20,20,.03)}}
[data-slot="sidebar-inner"]{animation:lc-alert-bars 1.8s ease-in-out infinite;}
[data-slot="composer-host"]{animation:lc-alert-bars 1.8s ease-in-out infinite;}
[data-workspace-area="conversation"]{animation:lc-alert-glow 1.8s ease-in-out infinite,lc-drift 300s steps(1400) infinite;}
[data-workspace-area="conversation"]:is(:root:has(button[aria-label="Stop generation"]) *){animation:lc-alert-glow 1.8s ease-in-out infinite,lc-drift 300s steps(1400) infinite;}
@media (prefers-reduced-motion:reduce){[data-slot="sidebar-inner"],[data-slot="composer-host"],[data-workspace-area="conversation"]{animation:none !important;}}
'''
json.dump(t,open(dst,'w'),indent=2)
left=[h for h in set(re.findall(r'#[0-9A-Fa-f]{6}\b',json.dumps({k:v for k,v in t.items() if k!='css'})+re.sub(r'base64,[^)]*','',t['css'])))]
print(sorted(left))
