# Lighting lab: composite any light mix from passes (comp.py), shrink to the 72px sprite, and measure it.
import os, json, numpy as np
from PIL import Image
import comp
from sprite72 import make72
S = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PD = os.path.join(S, 'passes')
U = {u['id']: u for f in json.load(open(os.environ.get('RJSON') or os.path.join(S, 'r3d/roster2.json'))) for u in f['units']}
FACTION = {}
for f in json.load(open(os.environ.get('RJSON') or os.path.join(S, 'r3d/roster2.json'))):
    for u in f['units']: FACTION[u['id']] = u['id'].split('-')[0]
def lumf(a): return 0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2]
_A = {}
def albedo72(uid):
    """paint brightness (linear luminance) at 72px from the uniform-light pass, and the emissive mask"""
    if uid not in _A:
        A = np.asarray(make72(Image.open(os.path.join(PD, uid, 'A.png')), False)).astype(np.float32) / 255
        E = np.asarray(make72(Image.open(os.path.join(PD, uid, 'E.png')), False)).astype(np.float32) / 255
        _A[uid] = (comp.s2l(lumf(A)), lumf(comp.s2l(E[..., :3])))
    return _A[uid]
def sprite(uid, mix, emis=1.0):
    return make72(comp.compose(PD, uid, mix, emis), bool(U[uid].get('pop')), 6)
def scaled(mix, s): return {k: v * s for k, v in mix.items()}
def at_lum(uid, mix, target, iters=4):
    """scale every light of mix (not the self-lit parts) so the sprite's brightness is target; returns (scale, metrics)"""
    s = 1.0; m = metrics(uid, mix)
    for _ in range(iters):
        if abs(m['lum'] - target) < 0.4: break
        s *= (target / max(m['lum'], 1)) ** 2.2; m = metrics(uid, scaled(mix, s))
    return s, m
def delivered(uid, mix):
    """share of the light reaching the hull that each light delivers (linear luminance, whole hull)"""
    E, al = comp.load(PD, uid, 'E'); msk = al > 0.9; out = {}
    for n, k in mix.items():
        P, _ = comp.load(PD, uid, n); out[n] = float((k / (1.0 if n in ('H', 'A') else comp.PI_)) * lumf(np.maximum(P - E, 0))[msk].mean())
    t = sum(out.values()); return {n: v / t for n, v in out.items()}
def metrics(uid, mix=None, img=None):
    img = img if img is not None else sprite(uid, mix)
    s = np.asarray(img).astype(np.float32); m = s[..., 3] > 230; L = lumf(s[..., :3]); l = L[m]
    Alin, Elin = albedo72(uid)
    Llin = comp.s2l(L / 255)
    ok = m & (Alin > 0.004) & (Elin < 0.02)                       # paint not black, not self-lit
    sh = np.log2(np.maximum(Llin[ok], 1e-4) / Alin[ok])            # shading (light reaching each pixel), in stops
    pt = np.log2(np.maximum(Alin[ok], 1e-4))                       # paint, in stops
    g = np.abs(L - np.roll(L, 1, 1)) + np.abs(L - np.roll(L, 1, 0)); inner = m & np.roll(m, 1, 0) & np.roll(m, 1, 1)
    # silhouette: the outer 2px ring of the hull, against dark space; 'edgeL' = the ring on the shadow (left) half
    er = m.copy()
    for _ in range(2): er = er & np.roll(er, 1, 0) & np.roll(er, -1, 0) & np.roll(er, 1, 1) & np.roll(er, -1, 1)
    ring = m & ~er; ys, xs = np.nonzero(m); cx = xs.mean()
    left = np.arange(m.shape[1])[None, :] < cx
    edge = float(L[ring].mean()); edgeL = float(L[ring & left].mean()) if (ring & left).any() else edge
    return dict(edge=edge, edgeL=edgeL, lum=float(l.mean()), std=float(l.std()), p10=float(np.percentile(l, 10)), p90=float(np.percentile(l, 90)),
                crush=float((l < 25).mean() * 100), clip=float((l > 235).mean() * 100),
                shape=float(sh.std()), lr=float(np.percentile(sh, 90) - np.percentile(sh, 10)), tot=float(np.log2(np.maximum(Llin[ok], 1e-4)).std()), tr=float(np.percentile(np.log2(np.maximum(Llin[ok], 1e-4)), 90) - np.percentile(np.log2(np.maximum(Llin[ok], 1e-4)), 10)), paint=float(pt.std()), det=float(g[inner].mean() / 2))
