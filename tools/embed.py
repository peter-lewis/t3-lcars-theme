import json,sys,base64
p,f=sys.argv[1],sys.argv[2]
t=json.load(open(p))
b=base64.b64encode(open(f,'rb').read()).decode()
face='@font-face{font-family:"LCARS Antonio";src:url(data:font/woff2;base64,'+b+') format("woff2");font-weight:100 700;font-display:swap;}\n'
if 'LCARS Antonio";src' not in t['css']:
    t['css']=face+t['css']
json.dump(t,open(p,'w'),indent=2)
print(len(t['css']))
