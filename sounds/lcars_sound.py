# LCARS sound hooks for Claude Code. Usage: lcars_sound.py prompt|hail|stop  (hook JSON on stdin)
# On/off: /sounds (toggle.py). Assets live next to this file; runtime state in ~/.claude/lcars-sounds-state/.
# A file in ~/.claude/lcars-sounds-custom/ named after a slot (ack, hail, done, hum, hum_in, hum_out; any afplay format)
# replaces the built-in sound. /sounds use <slot> <file> puts it there.
import json, os, sys, signal, subprocess, time, shlex
D=os.path.dirname(os.path.abspath(__file__)); ST=os.path.expanduser('~/.claude/lcars-sounds-state')
CU=os.path.expanduser('~/.claude/lcars-sounds-custom'); EXTS=('.wav','.mp3','.m4a','.aac','.aif','.aiff','.caf')
ACT=os.path.join(ST,'active'); PID=os.path.join(ST,'hum.pid')
STALE=30*60
def custom(slot):
    for e in EXTS:
        p=os.path.join(CU,slot+e)
        if os.path.isfile(p): return p
def sound(slot):
    # A custom hum gets no built-in fade-in/out unless those are custom too: the synth swells would not match it.
    if slot in ('hum_in','hum_out') and custom('hum') and not custom(slot): return None
    return custom(slot) or os.path.join(D,slot+'.wav')
def play(slot,vol=0.5):
    p=sound(slot)
    if p: subprocess.Popen(['/usr/bin/afplay','-v',str(vol),p],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,start_new_session=True)
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
          f'do /usr/bin/afplay -v 0.12 {shlex.quote(sound("hum"))}; done')
    if sound('hum_in'): loop=f'/usr/bin/afplay -v 0.12 {shlex.quote(sound("hum_in"))}; '+loop
    p=subprocess.Popen(['/bin/bash','-c',loop],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,start_new_session=True)
    open(PID,'w').write(str(p.pid))
def stop_hum():
    pid=hum_alive()
    if pid:
        try: os.killpg(pid,signal.SIGTERM)
        except Exception: pass
        play('hum_out',0.12)
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
        play('ack',0.45)
        open(os.path.join(ACT,sid),'w').close(); start_hum()
    elif ev=='hail':
        play('hail',0.5)
    elif ev=='stop':
        try: os.remove(os.path.join(ACT,sid))
        except OSError: pass
        if not os.listdir(ACT): stop_hum()
        play('done',0.4)
main()
