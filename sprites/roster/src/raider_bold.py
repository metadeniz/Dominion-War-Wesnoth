"""Bolder Maquis raider paint (D's studio-model reference): writes a recoloured copy of ZEO's Condor-class textures.
Hull greys: darker and more contrast; copper/tan panels: bold gold; red: glowing orange-red; cyan: glowing blue; green light glows.
Usage: python3 -I raider_bold.py SRC_DIR OUT_DIR [hull_dark hull_contrast gold_sat]"""
import sys, os, colorsys
import numpy as np
from PIL import Image
SRC, OUT = sys.argv[1], sys.argv[2]
HD = float(sys.argv[3]) if len(sys.argv) > 3 else 0.8; HC = float(sys.argv[4]) if len(sys.argv) > 4 else 1.5; GS = float(sys.argv[5]) if len(sys.argv) > 5 else 0.7
OBJ = 'Maquis_-_Condor_class_[Clean].obj'; MTL = OBJ[:-4] + '.mtl'
os.makedirs(OUT, exist_ok=True)
def hsv(a):
    r, g, b = a[..., 0], a[..., 1], a[..., 2]; mx = a.max(-1); mn = a.min(-1); d = mx - mn + 1e-6
    h = np.where(mx == r, ((g - b) / d) % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4)) / 6
    return h, (mx - mn) / (mx + 1e-6), mx
def from_hsv(h, s, v):
    i = np.floor(h * 6) % 6; f = h * 6 - np.floor(h * 6); p = v * (1 - s); q = v * (1 - f * s); t = v * (1 - (1 - f) * s)
    c = [np.select([i == k for k in range(6)], x) for x in ([v, q, p, p, t, v], [t, v, v, q, p, p], [p, p, t, v, v, q])]
    return np.stack(c, -1)
def kind(m):
    h, s, v = colorsys.rgb_to_hsv(*m); h *= 360
    if s > 0.6 and (h < 15 or h > 345) or (s > 0.4 and h < 10 and v > 0.5): return 'red'
    if s > 0.8 and 180 <= h <= 200: return 'cyan'
    if s > 0.8 and 120 <= h <= 160: return 'green'
    if s > 0.6 and 35 <= h <= 55: return 'gold'
    if s > 0.2 and 15 <= h <= 35 and v > 0.3: return 'copper'
    if v > 0.8 and s < 0.05: return 'white'
    return 'hull'
blocks = open(os.path.join(SRC, MTL)).read().split('newmtl ')[1:]; out = []; kinds = {}
for b in blocks:
    ls = [l.strip() for l in b.strip().splitlines()]; name = ls[0]
    kd = [l.split(None, 1)[1] for l in ls if l.startswith('map_Kd')]
    keep = [l for l in ls[1:] if not l.startswith(('map_Ka', 'map_Bump', 'map_Kd', 'Ke', 'map_Ke'))]
    if not kd: out.append('newmtl ' + name + '\n' + '\n'.join(keep)); continue
    t = kd[0]; im = Image.open(os.path.join(SRC, t)).convert('RGB'); a = np.asarray(im).astype(np.float32) / 255
    k = kind(a.reshape(-1, 3).mean(0)); kinds[name] = k; em = False
    if k == 'hull':
        g = a.mean(-1, keepdims=True); mean = g.mean()
        a = g * 0.75 + a * 0.25                                   # mostly neutral grey, a hint of the blue tint
        a = np.clip(((a - mean) * HC + mean) * HD, 0, 1)
    elif k in ('copper', 'gold'):
        h, s, v = hsv(a); h = np.full_like(h, 40 / 360); s = np.clip(np.maximum(s, GS) * 1.0, 0, 1)
        v = np.clip(v * (1.25 if k == 'copper' else 1.0), 0, 1); a = from_hsv(h, s, v)
    elif k == 'red':
        h, s, v = hsv(a); a = from_hsv(np.full_like(h, 12 / 360), np.full_like(s, 0.9), np.clip(v * 1.3, 0, 1)); em = True
    elif k == 'cyan':
        h, s, v = hsv(a); a = from_hsv(np.full_like(h, 200 / 360), np.full_like(s, 0.85), np.clip(v * 1.3, 0, 1)); em = True
    elif k == 'green':
        em = True
    fn = os.path.splitext(t)[0] + '_bold.png'; Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8)).save(os.path.join(OUT, fn))
    keep.append('map_Kd ' + fn)
    if em: keep += ['Ke 1 1 1', 'map_Ke ' + fn]
    out.append('newmtl ' + name + '\n' + '\n'.join(keep))
open(os.path.join(OUT, MTL), 'w').write('\n\n'.join(out) + '\n')
lnk = os.path.join(OUT, OBJ)
if not os.path.exists(lnk): os.symlink(os.path.relpath(os.path.join(SRC, OBJ), OUT), lnk)
from collections import Counter; print(Counter(kinds.values())); print({k: [n for n in kinds if kinds[n] == k] for k in ('red', 'cyan', 'green', 'gold', 'copper', 'white')})
