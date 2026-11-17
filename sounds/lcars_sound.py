# LCARS sound hooks for Claude Code. Usage: lcars_sound.py prompt|hail|stop  (hook JSON on stdin)
# On/off: /sounds (toggle.py). Assets live next to this file; runtime state in ~/.claude/lcars-sounds-state/.
import json, os, sys, signal, subprocess, time
D=os.path.dirname(os.path.abspath(__file__)); ST=os.path.expanduser('~/.claude/lcars-sounds-state')
ACT=os.path.join(ST,'active'); PID=os.path.join(ST,'hum.pid')
STALE=30*60
def play(name,vol=0.5):
    subprocess.Popen(['/usr/bin/afplay','-v',str(vol),os.path.join(D,name)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,start_new_session=True)
def hum_alive():
    try: pid=int(open(PID).read()); os.kill(pid,0); return pid
    except Exception: return None
def prune():
    now=time.time()
    for f in os.listdir(ACT):
        p=os.path.join(ACT,f)
        try:
            if now-os.path.getmtime(p)>STALE: os.remove(p)
        except OSError: pass
def start_hum():
    if hum_alive(): return
    loop=(f'end=$((SECONDS+{STALE})); while [ $SECONDS -lt $end ] && [ -n "$(ls -A {ACT!r} 2>/dev/null)" ]; '
          f'do /usr/bin/afplay -v 0.12 {os.path.join(D,"hum.wav")!r}; done')
    loop=f'/usr/bin/afplay -v 0.12 {os.path.join(D,"hum_in.wav")!r}; '+loop
    p=subprocess.Popen(['/bin/bash','-c',loop],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,start_new_session=True)
    open(PID,'w').write(str(p.pid))
def stop_hum():
    pid=hum_alive()
    if pid:
        try: os.killpg(pid,signal.SIGTERM)
        except Exception: pass
        play('hum_out.wav',0.12)
    try: os.remove(PID)
    except OSError: pass
def main():
    if not os.path.exists('/usr/bin/afplay'): return   # macOS only; silent elsewhere
    if os.path.exists(os.path.join(ST,'MUTE')): return
    ev=sys.argv[1] if len(sys.argv)>1 else ''
    try: sid=str(json.load(sys.stdin).get('session_id') or 'default')
    except Exception: sid='default'
    sid=''.join(c for c in sid if c.isalnum() or c in '-_')[:80] or 'default'
    os.makedirs(ACT,exist_ok=True); prune()
    if ev=='prompt':
        play('ack.wav',0.45)
        open(os.path.join(ACT,sid),'w').close(); start_hum()
    elif ev=='hail':
        play('hail.wav',0.5)
    elif ev=='stop':
        try: os.remove(os.path.join(ACT,sid))
        except OSError: pass
        if not os.listdir(ACT): stop_hum()
        play('done.wav',0.4)
main()
