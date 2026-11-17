# v3 beeps: clean 'computer acknowledging' style (sine + a hint of odd harmonics, flat pitch, crisp edges)
import math, wave, struct, os
SR=44100; OUT=os.path.dirname(os.path.abspath(__file__))
def save(name,s):
    pk=max(abs(x) for x in s)
    with wave.open(os.path.join(OUT,name),'w') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(b''.join(struct.pack('<h',int(x/pk*0.9*32767)) for x in s))
def note(f,dur,sq=0.1,vol=1.0):
    n=int(SR*dur); o=[]
    for i in range(n):
        ph=2*math.pi*f*i/SR
        s=(1-sq)*math.sin(ph)+sq*(math.sin(ph)+math.sin(3*ph)/3+math.sin(5*ph)/5)
        a=min(1,i/(0.0015*SR)); r=min(1,(n-i)/(0.008*SR)); o.append(vol*s*a*r)
    return o
g=lambda d:[0.0]*int(SR*d)
C6,E6,G6,C7,A5=1046.5,1318.5,1568.0,2093.0,880.0
save('ack.wav',  note(C6,.06)+g(.02)+note(G6,.09))                       # boo-BEEP
save('hail.wav', (note(E6,.07)+g(.025)+note(C7,.07)+g(.025))*2+note(E6,.07)+g(.025)+note(C7,.11))   # incoming: bee-DEE x3
save('done.wav', note(G6,.045)+g(.015)+note(E6,.045)+g(.015)+note(G6,.045)+g(.015)+note(C7,.12))    # beep-boop-beep-BEEP, resolves up
print('ok')
