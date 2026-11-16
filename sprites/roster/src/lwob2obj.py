"""Convert a LightWave 5 (LWOB) object with planar/cylindrical image maps to OBJ + MTL + PNG.
Usage: python3 -I lwob2obj.py IN.lwo IMGDIR OUTDIR [vflip]
UVs come from each surface's colour-texture projection; the luminosity map, if it shares the projection
axis, is remapped into the same UV space and written as the emissive map (warm window light).
LightWave is left-handed, so z is negated on output.
"""
import sys, os, math
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lwob import parse
from ilbm import load as load_ilbm

IN, IMGDIR, OUT = sys.argv[1:4]
os.makedirs(OUT, exist_ok=True)
pts, srfs, polys, surfs = parse(IN)
AX = {1: 0, 2: 1, 4: 2}

def img_path(name):
    return os.path.join(IMGDIR, name.replace('\\', '/').split('/')[-1])

_imgs = {}
def get_img(name):
    if name not in _imgs:
        p = img_path(name)
        try: _imgs[name] = load_ilbm(p).convert('RGB')
        except Exception as e: print('no image', name, e); _imgs[name] = None
    return _imgs[name]

def proj(t, P):
    """UV for points P (N,3, LightWave coords) under texture t."""
    ax = AX.get(t.get('flg', 0) & 7, 1)
    c = np.array(t.get('tctr', (0, 0, 0))); s = np.array(t.get('tsiz', (1, 1, 1))); s[s == 0] = 1
    q = (P - c) / s
    if t['type'].startswith('Planar'):
        if ax == 0: u, v = q[:, 2], q[:, 1]
        elif ax == 1: u, v = q[:, 0], -q[:, 2]
        else: u, v = q[:, 0], q[:, 1]
        return np.stack([u + 0.5, v + 0.5], 1)
    if t['type'].startswith('Cylindrical'):
        r = P - c
        if ax == 0: a, h = np.arctan2(r[:, 2], r[:, 1]), q[:, 0]
        elif ax == 1: a, h = np.arctan2(r[:, 0], r[:, 2]), q[:, 1]
        else: a, h = np.arctan2(r[:, 0], r[:, 1]), q[:, 2]
        return np.stack([a / (2 * math.pi) + 0.5, h + 0.5], 1)
    return np.zeros((len(P), 2))

mtl = []; obj = ['mtllib model.mtl']
obj += ['v %.6f %.6f %.6f' % (p[0], p[1], -p[2]) for p in pts]
vt_n = 0; by_s = {}
for vs, s in polys: by_s.setdefault(s, []).append(vs)
for si, plist in sorted(by_s.items()):
    name = srfs[si] if si < len(srfs) else 'default'; d = surfs.get(name, {'tex': []})
    mname = 'm%d' % si
    col = np.array(d.get('colr', (200, 200, 200))) / 255
    lumi = d.get('lumi', 0.0)
    ctex = next((t for t in d['tex'] if t['slot'] == 'CTEX' and 'img' in t and get_img(t['img']) is not None), None)
    ltex = next((t for t in d['tex'] if t['slot'] == 'LTEX' and 'img' in t and get_img(t['img']) is not None), None)
    mtl += ['newmtl ' + mname, 'Kd %.4f %.4f %.4f' % tuple(col), 'Ka 0 0 0', 'Ks 0.1 0.1 0.1']
    em = col * lumi
    synth = False
    if ctex is None:   # no colour image: use a grey detail map (diffuse/bump) to shade the surface colour
        ctex = next((t for t in d['tex'] if t['slot'] in ('DTEX', 'BTEX', 'STEX') and 'img' in t and get_img(t['img']) is not None), None)
        synth = ctex is not None
    if ctex is not None:
        im = get_img(ctex['img'])
        if synth:
            g = np.asarray(im.convert('L'), np.float32); g = g / max(g.mean(), 1)
            im = Image.fromarray((col[None, None, :] * 255 * (0.82 + 0.18 * g[..., None])).clip(0, 255).astype(np.uint8))
        fn = mname + '_kd.png'; im.save(os.path.join(OUT, fn)); mtl.append('map_Kd ' + fn)
        if ltex is not None and (ltex.get('flg', 0) & 7) == (ctex.get('flg', 0) & 7):
            # remap luminosity image into the colour image's UV space
            W, H = im.size; uu, vv = np.meshgrid((np.arange(W) + 0.5) / W, 1 - (np.arange(H) + 0.5) / H)
            ax = AX.get(ctex.get('flg', 0) & 7, 1); ins = [i for i in range(3) if i != ax]
            c1 = np.array(ctex.get('tctr', (0, 0, 0))); s1 = np.array(ctex.get('tsiz', (1, 1, 1)))
            # invert proj for the two in-plane coords: build points with axis coord = centre
            P = np.zeros((W * H, 3)); P[:, ax] = c1[ax]
            U = uu.ravel() - 0.5; V = vv.ravel() - 0.5
            if ax == 0: P[:, 2] = U * s1[2] + c1[2]; P[:, 1] = V * s1[1] + c1[1]
            elif ax == 1: P[:, 0] = U * s1[0] + c1[0]; P[:, 2] = -V * s1[2] + c1[2]
            else: P[:, 0] = U * s1[0] + c1[0]; P[:, 1] = V * s1[1] + c1[1]
            luv = proj(ltex, P); L = np.asarray(get_img(ltex['img']).convert('L'), np.float32) / 255
            lh, lw = L.shape; lx = np.mod(np.floor(luv[:, 0] * lw), lw).astype(int); ly = np.mod(np.floor((1 - luv[:, 1]) * lh), lh).astype(int)
            lum = L[ly, lx].reshape(H, W)
            warm = np.array([255, 226, 160], np.float32)
            emi = (lum[..., None] * warm).clip(0, 255).astype(np.uint8)
            fe = mname + '_ke.png'; Image.fromarray(emi).save(os.path.join(OUT, fe))
            mtl += ['map_Ke ' + fe, 'Ke 1 1 1']; em = None
        elif ltex is not None: print('luminosity map on another axis, skipped:', name)
    if em is not None and lumi > 0: mtl.append('Ke %.4f %.4f %.4f' % tuple(em))
    mtl.append('')
    obj.append('usemtl ' + mname); obj.append('g s%d' % si)
    for vs in plist:
        if len(vs) < 3: continue
        if ctex is not None:
            uv = proj(ctex, pts[list(vs)])
            obj += ['vt %.5f %.5f' % (a, b) for a, b in uv]
            obj.append('f ' + ' '.join('%d/%d' % (v + 1, vt_n + k + 1) for k, v in enumerate(vs))); vt_n += len(vs)
        else:
            obj.append('f ' + ' '.join(str(v + 1) for v in vs))
open(os.path.join(OUT, 'model.obj'), 'w').write('\n'.join(obj) + '\n')
open(os.path.join(OUT, 'model.mtl'), 'w').write('\n'.join(mtl) + '\n')
print('wrote', len(pts), 'points', len(polys), 'polygons', len(by_s), 'materials')
