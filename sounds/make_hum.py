# Engine hum for the LCARS sound hooks: original synthesis (filtered brown noise + low tones), no samples.
# Beeps live in make_beeps.py. Re-run either script to regenerate its WAVs next to it.
import math, wave, struct, os, random
SR=44100; OUT=os.path.dirname(os.path.abspath(__file__)); random.seed(1701)
def save(name,s):
    peak=max(1e-9,max(abs(x) for x in s)); g=0.9/peak
    with wave.open(os.path.join(OUT,name),'w') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(b''.join(struct.pack('<h',int(x*g*32767)) for x in s))
def blip(f0,f1,dur,vol=1.0,ring=0.18,buzz=0.25):
    """Hollow LCARS blip: triangle-ish tone gliding f0->f1, light ring-mod, fast attack, short release."""
    n=int(SR*dur); out=[]; ph=0.0
    for i in range(n):
        t=i/n; f=f0+(f1-f0)*(1-(1-t)**3); ph+=2*math.pi*f/SR
        tri=(2/math.pi)*math.asin(math.sin(ph))                  # triangle
        s=(1-buzz)*tri+buzz*math.copysign(1,math.sin(ph))*0.5     # touch of square = slight buzz
        s*= (1-ring)+ring*math.sin(2*math.pi*f*1.5*i/SR)          # ring-mod sheen
        a=min(1,i/(0.002*SR)); r=min(1,(n-i)/(0.012*SR))
        out.append(vol*s*a*r)
    return out
def gap(d): return [0.0]*int(SR*d)
# Engine hum: deep filtered rumble + faint pulse, 20s seamless loop
n=SR*20; hum=[0.0]*n; b=0.0; lp=0.0; lp2=0.0
noise=[]
for i in range(n):
    b=0.995*b+0.05*random.uniform(-1,1)          # brown-ish noise
    lp+=0.02*(b-lp); lp2+=0.02*(lp-lp2)          # two-pole low-pass (~140 Hz)
    noise.append(lp2)
fade=SR//2                                        # crossfade tail into head so the loop is seamless
for i in range(fade):
    w=i/fade; noise[i]=noise[i]*w+noise[n-fade+i]*(1-w)
noise=noise[:n-fade]; n=len(noise)
nm=max(abs(x) for x in noise)
for i in range(n):
    t=i/SR; pulse=0.82+0.18*(0.5+0.5*math.sin(2*math.pi*(10/ (n/SR))*t))   # whole cycles over loop
    tone=0.35*math.sin(2*math.pi*(round(41*n/SR)/(n/SR))*t)+0.15*math.sin(2*math.pi*(round(82.5*n/SR)/(n/SR))*t)
    hum[i]=pulse*(0.75*noise[i]/nm+tone)
save('hum.wav',hum[:n])


# Fade clips so the hum swells in and dies away instead of cutting (afplay cannot fade a playing file)
h=hum[:n]; k=int(SR*2.5)
save('hum_in.wav',[x*(i/k)**2 for i,x in enumerate(h[:k])])
save('hum_out.wav',[x*(1-i/k)**2 for i,x in enumerate(h[k:2*k])])
print('ok')
