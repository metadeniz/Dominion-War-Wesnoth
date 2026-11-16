"""Recolour an OBJ with per-vertex colours to a new base colour, keeping the light/dark pattern.
Usage: python3 -I recolor_vc.py in.obj out.obj BASE_HEX MARK_HEX [contrast=1.0]
Grey vertices become BASE scaled by their brightness relative to the mean; reddish vertices (markings) become MARK."""
import sys, numpy as np
src, dst, base, mark = sys.argv[1:5]; k = float(sys.argv[5]) if len(sys.argv) > 5 else 1.0
hx = lambda h: np.array([int(h[i:i+2], 16) for i in (1, 3, 5)]) / 255
B, M = hx(base), hx(mark)
lines = open(src).read().split('\n'); vi = [i for i, l in enumerate(lines) if l.startswith('v ')]
P = np.array([lines[i].split()[1:7] for i in vi], float); C = P[:, 3:6]
lum = C.mean(1); rel = (lum / lum.mean()) ** k
redness = np.clip((C[:, 0] - (C[:, 1] + C[:, 2]) / 2 - 0.05) / 0.10, 0, 1)[:, None]
new = np.clip((B * (1 - redness) + M * redness) * rel[:, None], 0, 1)
for j, i in enumerate(vi):
    lines[i] = 'v %s %s %s %.3f %.3f %.3f' % (*lines[i].split()[1:4], *new[j])
open(dst, 'w').write('\n'.join(lines))
print('vertices', len(vi), 'marked', int((redness[:, 0] > 0.5).sum()))
