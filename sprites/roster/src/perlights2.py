"""Stronger version of the octave767 Peregrine's OWN lights (no other model used).
Each lit texel of the model's illum map is classed blue or red (its orange lamps become red), set to a pure colour,
then grown in 3D (texels whose surface point is within RB/RR voxels of a light take its colour), with an optional dark
halo one voxel further out for contrast at 72px.
Usage: python3 -I perlights2.py BAKEDIR TEXDIR OUTBASE OUTILLUM RR RB HALO [res]"""
import sys, numpy as np
from PIL import Image
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from uvdecode import decode
B, T, OB, OI = sys.argv[1:5]; RR, RB = int(sys.argv[5]), int(sys.argv[6]); HALO = float(sys.argv[7])
RES = int(sys.argv[8]) if len(sys.argv) > 8 else 192
cov, x, y, z, ny = decode(B)
b0 = np.asarray(Image.open(T + '/peregrine_base.png').convert('RGBA')).astype(np.float32)
base = np.clip(b0[..., :3] * 1.3, 0, 255)
il = np.asarray(Image.open(T + '/peregrine_illum.png').convert('RGB')).astype(np.float32)
lit = cov & (il.max(2) > 40)
isblue = lit & (il[..., 2] > il[..., 0] + 20)
isred = lit & (il[..., 0] > il[..., 2] + 20)
RED = np.array([255, 24, 16], np.float32)
BLUE = np.array([int(c) for c in sys.argv[9].split(",")] if len(sys.argv) > 9 else [30, 140, 255], np.float32)
vox = lambda a: np.clip((a * RES).astype(int), 0, RES - 1)
V = (vox(x), vox(y), vox(z))
def dil(g, r):
    for ax in range(3):
        for _ in range(r): g = g | np.roll(g, 1, ax) | np.roll(g, -1, ax)
    return g
def region(mask, r):
    g = np.zeros((RES,) * 3, bool); g[V[0][mask], V[1][mask], V[2][mask]] = True
    g1 = dil(g, r); g2 = dil(g1, 1)
    return cov & g1[V], cov & g2[V]
rin, rhalo = region(isred, RR); bin_, bhalo = region(isblue, RB)
ill = np.zeros_like(il)
ill[rin] = RED; ill[bin_] = BLUE                     # blue wins where both overlap
other = lit & ~isblue & ~isred; ill[other] = il[other]
halo = (rhalo | bhalo) & ~(rin | bin_)
base[halo] *= HALO
lm = rin | bin_; base[lm] = ill[lm]
print('red', int(isred.sum()), '->', int(rin.sum()), 'blue', int(isblue.sum()), '->', int(bin_.sum()), 'halo', int(halo.sum()))
Image.fromarray(np.concatenate([base, b0[..., 3:]], 2).astype(np.uint8), 'RGBA').save(OB)
Image.fromarray(ill.astype(np.uint8)).save(OI)
