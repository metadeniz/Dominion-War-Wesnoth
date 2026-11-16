"""Widen the blue strips in 3D: any texel whose surface point lies within R voxels of a blue light texel turns blue.
Usage: python3 -I perwiden.py BAKEDIR BASE_IN ILLUM_IN BASE_OUT ILLUM_OUT [res] [radius]"""
import sys, numpy as np
from PIL import Image
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from uvdecode import decode
B, BI, II, BO, IO = sys.argv[1:6]
RES = int(sys.argv[6]) if len(sys.argv) > 6 else 192; RAD = int(sys.argv[7]) if len(sys.argv) > 7 else 1
cov, x, y, z, ny = decode(B)
base = np.asarray(Image.open(BI).convert('RGBA')).copy(); ill = np.asarray(Image.open(II).convert('RGB')).copy()
blue = cov & (ill[..., 2] > 150) & (ill[..., 2] > ill[..., 0] + 60)
vox = lambda a: np.clip((a * RES).astype(int), 0, RES - 1)
g = np.zeros((RES, RES, RES), bool); g[vox(x[blue]), vox(y[blue]), vox(z[blue])] = True
for ax in range(3):
    for _ in range(RAD):
        g = g | np.roll(g, 1, ax) | np.roll(g, -1, ax)
sel = cov & g[vox(x), vox(y), vox(z)] & ~blue
print('blue texels', blue.sum(), 'added', sel.sum())
C = np.array([40, 150, 255], np.uint8)
ill[sel] = C; base[sel, :3] = C
Image.fromarray(base, 'RGBA').save(BO); Image.fromarray(ill).save(IO)
