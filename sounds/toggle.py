# LCARS sounds switch. Usage: toggle.py [on|off|status]  (no argument = flip)
import os, sys, signal, subprocess
D=os.path.dirname(os.path.abspath(__file__)); ST=os.path.expanduser('~/.claude/lcars-sounds-state'); os.makedirs(ST,exist_ok=True)
MUTE=os.path.join(ST,'MUTE'); PID=os.path.join(ST,'hum.pid'); ACT=os.path.join(ST,'active')
arg=(sys.argv[1] if len(sys.argv)>1 else '').strip().lower()
muted=os.path.exists(MUTE)
if arg in ('', 'toggle'): arg='on' if muted else 'off'
if arg=='status':
    print('LCARS sounds are ' + ('OFF' if muted else 'ON')); sys.exit()
if arg=='off':
    open(MUTE,'w').close()
    try: os.killpg(int(open(PID).read()), signal.SIGTERM)
    except Exception: pass
    for p in [PID]+[os.path.join(ACT,f) for f in (os.listdir(ACT) if os.path.isdir(ACT) else [])]:
        try: os.remove(p)
        except OSError: pass
    print('LCARS sounds OFF (hum silenced)')
elif arg=='on':
    try: os.remove(MUTE)
    except OSError: pass
    if os.path.exists('/usr/bin/afplay'): subprocess.Popen(['/usr/bin/afplay','-v','0.45',os.path.join(D,'ack.wav')],start_new_session=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    print('LCARS sounds ON')
else:
    print('Usage: /sounds [on|off|status]  (no argument flips it)'); sys.exit(1)
