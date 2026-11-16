"""Decode the UV-space bake (uv0/uv1.png) into per-texel normalized position + normal.y, and splat a top view."""
import numpy as np
from PIL import Image
def decode(d):
    a=np.asarray(Image.open(d+'/uv0.png').convert('RGB')).astype(np.float64)
    b=np.asarray(Image.open(d+'/uv1.png').convert('RGB')).astype(np.float64)
    cov=(a.sum(2)+b.sum(2))>0
    x=(a[...,0]+a[...,1]/255)/255; z=(a[...,2]+b[...,0]/255)/255
    ny=b[...,1]/255*2-1; y=b[...,2]/255
    return cov,x,y,z,ny
def splat(cov,x,y,z,ny,tex,N=512,up=True):
    sel=cov&((ny>0.2) if up else (ny<-0.2))
    xi=np.clip((x[sel]*N).astype(int),0,N-1); zi=np.clip(((1-z[sel])*N).astype(int),0,N-1)
    yy=y[sel] if up else -y[sel]
    col=tex[sel]
    o=np.argsort(yy)  # later (higher) wins
    img=np.full((N,N,3),[255,0,255],np.uint8)
    img[zi[o],xi[o]]=col[o]
    return img
