# python3 redglow.py BASE.png EMIS_IN.png EMIS_OUT.png GAIN : make the large red patches (bussard fronts, impulse grilles) self-lit, brighter and pinker
import sys, numpy as np
from PIL import Image
from scipy import ndimage
b=np.asarray(Image.open(sys.argv[1]).convert('RGB')).astype(float)/255; e=np.asarray(Image.open(sys.argv[2]).convert('RGB')).astype(float)/255; G=float(sys.argv[4])
r=b[...,0]; mx=b.max(-1); s=(mx-b.min(-1))/(mx+1e-6)
red=(r>=mx-1e-6)&(s>0.45)&(r>0.25)&(b[...,1]<0.6*r+0.02)
lab,k=ndimage.label(ndimage.binary_closing(red,iterations=2)); keep=np.zeros_like(red)
for i,sl in enumerate(ndimage.find_objects(lab)):
    m=lab[sl]==i+1; h,w=m.shape
    skip=len(sys.argv)>6 and sys.argv[6]=='bussards' and sl[0].start>=200 and sl[0].stop<=360 and sl[1].start>=1580 and sl[1].stop<=1790
    if m.sum()>300 and e[sl][m].mean()>0.05 and not skip: keep[sl]|=m     # only patches the author already made self-lit (skips pinstripes, lettering)
v=np.clip(r/max(r[keep].max(),1e-6),0,1)
glow=np.stack([np.ones_like(v), 0.10+0.45*v**3, 0.08+0.40*v**3],-1)*(0.45+0.75*v)[...,None]*G
m=ndimage.gaussian_filter(keep.astype(float),1.0)[...,None]
out=np.maximum(e, np.clip(glow,0,1)*m)
Image.fromarray((out*255+0.5).astype(np.uint8)).save(sys.argv[3]); print('self-lit red px', int(keep.sum()))
# impulse engine grilles: light the whole slatted panel (red slats full, grey bars dimmer), like the STO model
if len(sys.argv)>5 and not (len(sys.argv)>6 and sys.argv[6]=='bussards'):
    GI=float(sys.argv[6]) if len(sys.argv)>6 else G   # impulse panel strength (defaults to GAIN)
    y0,y1,x0,x1=map(int,sys.argv[5].split(','))
    zone=np.zeros_like(red); zone[y0:y1,x0:x1]=True; rz=red&zone
    hull=np.zeros_like(red); ys=np.nonzero(rz.any(1))[0]          # the slatted panel, row by row between its outermost red slats
    for y in range(ys.min(),ys.max()+1):
        w=rz[max(y-5,0):y+6]; xs=np.nonzero(w.any(0))[0]; c=np.nonzero(w.any(1))[0]
        if len(xs): sk=(w.shape[0]//2-c.mean())*0.0; hull[y,xs.min()+0:xs.max()+1]=True
    hull=ndimage.binary_closing(hull,iterations=2)&zone
    lvl=np.where(red,1.0,0.55)
    col=np.stack([np.ones_like(v),0.12+0.10*lvl,0.10+0.08*lvl],-1)*lvl[...,None]*GI
    hm=ndimage.gaussian_filter(hull.astype(float),1.0)[...,None]
    out=np.maximum(out,np.clip(col,0,1)*hm)
    Image.fromarray((out*255+0.5).astype(np.uint8)).save(sys.argv[3]); print('impulse panel px',int(hull.sum()))
