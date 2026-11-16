"""Strengthen the octave767 Peregrine's OWN lights (nothing taken from any other model).
Brightens the base +30%, pushes each lit texel of the illum map to full brightness and higher saturation with its own hue,
spreads it 4 texels inside the UV bake's coverage, and paints it into the base too.
Usage: python3 -I perlights.py BAKEDIR TEXDIR OUTBASE OUTILLUM"""
import sys, numpy as np
from PIL import Image
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from uvdecode import decode
from perpaint_util import grow
B, T, OB, OI = sys.argv[1:5]
cov = decode(B)[0]
b0 = np.asarray(Image.open(T + '/peregrine_base.png').convert('RGBA')).astype(np.float32)
base = np.clip(b0[..., :3] * 1.3, 0, 255)
il = np.asarray(Image.open(T + '/peregrine_illum.png').convert('RGB')).astype(np.float32)
lit = il.max(2) > 40
mx = np.maximum(il.max(2, keepdims=True), 1)
n = il * 255 / mx                                   # full brightness, same hue
n = np.clip(255 - (255 - n) * 1.5, 0, 255)          # more saturated, same hue
ill = n * lit[..., None]
ill, m = grow(ill, lit, 4); ill = ill * m[..., None]
lm = ill.max(2) > 40
base[lm] = ill[lm]
ext, em = grow(base * lm[..., None], lm, 4); ring = em & ~lm & ~cov; base[ring] = ext[ring]
Image.fromarray(np.concatenate([base, b0[..., 3:]], 2).astype(np.uint8), 'RGBA').save(OB)
Image.fromarray(ill.astype(np.uint8)).save(OI); print('lit texels', int(lit.sum()), '->', int(lm.sum()))
