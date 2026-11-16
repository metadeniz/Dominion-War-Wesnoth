# python3 -I excelsior_tone.py SRCDIR NAME HUE SATMUL VALMUL
# Writes SRCDIR/tones/NAME/*.png (blue pixels of each hull texture re-hued) and
# SRCDIR/Excelsior_NAME.mtl (+ .obj symlink to Excelsior_v3.obj). nacelle_glow (engine blue,
# a plain colour, no texture) is copied unchanged.
import sys, os, re
import numpy as np
from PIL import Image
src, name, H, SM, VM = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5])
out = os.path.join(src, 'tones', name); os.makedirs(out, exist_ok=True)
def rgb2hsv(a):
    r,g,b = a[...,0],a[...,1],a[...,2]; mx=a.max(2); mn=a.min(2); d=mx-mn
    h=np.zeros_like(mx); m=d>1e-6
    rr=(mx==r)&m; gg=(mx==g)&m&~rr; bb=m&~rr&~gg
    h[rr]=((g-b)[rr]/d[rr])%6; h[gg]=((b-r)[gg]/d[gg])+2; h[bb]=((r-g)[bb]/d[bb])+4
    return h*60, np.where(mx>0,d/np.maximum(mx,1e-6),0), mx
def hsv2rgb(h,s,v):
    c=v*s; x=c*(1-np.abs((h/60)%2-1)); m=v-c; z=np.zeros_like(h); k=(h//60).astype(int)%6
    R=np.select([k==0,k==1,k==2,k==3,k==4,k==5],[c,x,z,z,x,c]); G=np.select([k==0,k==1,k==2,k==3,k==4,k==5],[x,c,c,x,z,z]); B=np.select([k==0,k==1,k==2,k==3,k==4,k==5],[z,z,x,c,c,x])
    return np.stack([R+m,G+m,B+m],2)
done={}
def tone(tex):
    if tex in done: return done[tex]
    a=np.asarray(Image.open(os.path.join(src,tex)).convert('RGB')).astype(float)/255
    h,s,v=rgb2hsv(a)
    # weight: blue hues 175-250 (soft 15deg edges), saturation above ~0.12
    hw=np.clip(1-np.maximum(0,np.maximum(175-h,h-250))/15,0,1); sw=np.clip((s-0.08)/0.12,0,1); w=(hw*sw)[...,None]
    n=hsv2rgb(np.full_like(h,H), np.clip(s*SM,0,1), np.clip(v*VM,0,1))
    o=(a*(1-w)+n*w); fn=os.path.splitext(tex)[0]+'.png'
    Image.fromarray((np.clip(o,0,1)*255+0.5).astype(np.uint8)).save(os.path.join(out,fn))
    done[tex]=f'tones/{name}/{fn}'; return done[tex]
lines=open(os.path.join(src,'Excelsior_v3.mtl')).read().split('\n'); res=[]
for L in lines:
    m=re.match(r'^(map_Kd|map_Ka)\s+(\S+)$',L.strip())
    res.append(f'{m.group(1)} {tone(m.group(2))}' if m else L)
open(os.path.join(src,f'Excelsior_{name}.mtl'),'w').write('\n'.join(res))
lk=os.path.join(src,f'Excelsior_{name}.obj')
if not os.path.lexists(lk): os.symlink('Excelsior_v3.obj',lk)
print(name, len(done), 'textures')
