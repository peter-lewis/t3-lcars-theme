# LCARS sounds switch. Usage: toggle.py [on|off|status|help]  (no argument = flip)
#   toggle.py use <slot> <file>   play your own audio file for a slot (copied into ~/.claude/lcars-sounds-custom/)
#   toggle.py reset [slot|all]    go back to the built-in sound
import os, sys, signal, shutil, subprocess
D=os.path.dirname(os.path.abspath(__file__)); ST=os.path.expanduser('~/.claude/lcars-sounds-state'); os.makedirs(ST,exist_ok=True)
CU=os.path.expanduser('~/.claude/lcars-sounds-custom')
MUTE=os.path.join(ST,'MUTE'); PID=os.path.join(ST,'hum.pid'); ACT=os.path.join(ST,'active')
SLOTS={'ack':'you send a prompt','hail':'Claude asks a question or needs permission','done':'Claude finishes',
       'hum':'background loop while Claude works','hum_in':'hum fade-in','hum_out':'hum fade-out'}
EXTS=('.wav','.mp3','.m4a','.aac','.aif','.aiff','.caf')
def custom(slot):
    for e in EXTS:
        p=os.path.join(CU,slot+e)
        if os.path.isfile(p): return p
def play(p,vol=0.45):
    if os.path.exists('/usr/bin/afplay'): subprocess.Popen(['/usr/bin/afplay','-v',str(vol),p],start_new_session=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
def clear(slot):
    for e in EXTS:
        try: os.remove(os.path.join(CU,slot+e))
        except OSError: pass
args=sys.argv[1:]
arg=(args[0] if args else '').strip().lower()
muted=os.path.exists(MUTE)
if arg in ('', 'toggle'): arg='on' if muted else 'off'
if arg=='status':
    print('LCARS sounds are ' + ('OFF' if muted else 'ON') + '\n')   # blank line: chat Markdown would join the lines
    mine=[f'{s} = {os.path.basename(custom(s))}' for s in SLOTS if custom(s)]
    print('Custom sounds: ' + (', '.join(mine) if mine else 'none') + '  (~/.claude/lcars-sounds-custom)'); sys.exit()
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
    play(custom('ack') or os.path.join(D,'ack.wav'))
    print('LCARS sounds ON')
elif arg=='use' and len(args)>=3 and args[1].lower() in SLOTS:
    slot=args[1].lower(); src=os.path.expanduser(' '.join(args[2:]).strip('\'"'))
    ext=os.path.splitext(src)[1].lower()
    if not os.path.isfile(src): print(f'No file at {src}'); sys.exit(1)
    if ext not in EXTS: print(f'Use one of {" ".join(EXTS)} (got {ext or "no extension"})'); sys.exit(1)
    os.makedirs(CU,exist_ok=True); clear(slot); dst=os.path.join(CU,slot+ext); shutil.copyfile(src,dst)
    if not muted: play(dst, 0.12 if slot.startswith('hum') else 0.45)   # preview, unless sounds are off
    print(f'LCARS {slot} sound ({SLOTS[slot]}) is now {os.path.basename(src)}')
elif arg=='reset' and len(args)<=2:
    which=(args[1].lower() if len(args)==2 else 'all')
    if which!='all' and which not in SLOTS: print('Slots: '+' '.join(SLOTS)); sys.exit(1)
    for s in (SLOTS if which=='all' else [which]): clear(s)
    print('LCARS ' + ('sounds' if which=='all' else which + ' sound') + ' reset to the built-in version')
else:
    # Markdown, because /sounds output is shown in chat: a list keeps the lines apart, backticks keep <slot> visible
    print('LCARS sounds commands:\n\n'
          '- `/sounds` flips sounds on or off\n'
          '- `/sounds on`, `/sounds off`, `/sounds status`\n'
          '- `/sounds use <slot> <file>` plays your own file for a slot, e.g. `/sounds use hail ~/Downloads/hail.mp3`\n'
          '- `/sounds reset [slot]` goes back to the built-in sound (no slot resets all)\n\n'
          'Slots: ' + ', '.join(f'`{s}` ({w})' for s,w in SLOTS.items()))
    sys.exit(0 if arg in ('help','-h','--help') else 1)   # asking for help is not an error
