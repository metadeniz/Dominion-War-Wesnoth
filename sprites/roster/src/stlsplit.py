import sys, struct, numpy as np
def read(p):
    b=open(p,'rb').read()
    if b[:5]==b'solid' and b'facet' in b[:400]:
        v=[list(map(float,l.split()[1:4])) for l in b.decode(errors='ignore').splitlines() if l.strip().startswith('vertex')]
        return np.array(v,dtype=np.float32).reshape(-1,3,3)
    n=struct.unpack('<I',b[80:84])[0]; a=np.frombuffer(b[84:84+n*50],dtype=np.dtype([('n','<3f4'),('v','<9f4'),('a','<u2')]))
    return a['v'].reshape(-1,3,3)
def write(p,t):
    with open(p,'wb') as f:
        f.write(b'\0'*80); f.write(struct.pack('<I',len(t)))
        rec=np.zeros(len(t),dtype=np.dtype([('n','<3f4'),('v','<9f4'),('a','<u2')])); rec['v']=t.reshape(-1,9); f.write(rec.tobytes())
def comps(t):
    q=np.round(t.reshape(-1,3),3); _,inv=np.unique(q,axis=0,return_inverse=True); inv=inv.reshape(-1,3)
    par=np.arange(inv.max()+1)
    def find(x):
        while par[x]!=x: par[x]=par[par[x]]; x=par[x]
        return x
    for a,b,c in inv:
        ra,rb,rc=find(a),find(b),find(c); par[rb]=ra; par[find(rc)]=ra
    roots=np.array([find(x) for x in inv[:,0]]); return roots
t=read(sys.argv[1]); r=comps(t); u,cnt=np.unique(r,return_counts=True); order=np.argsort(-cnt)
for i,k in enumerate(order[:25]):
    s=t[r==u[k]].reshape(-1,3); print(i,cnt[k],'min',s.min(0).round(1),'max',s.max(0).round(1))
if len(sys.argv)>3:
    keep=[u[order[int(i)]] for i in sys.argv[3].split(',')]; write(sys.argv[2],t[np.isin(r,keep)]); print('wrote',sys.argv[2])
