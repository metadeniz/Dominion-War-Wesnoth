# python3 -I wesunitstats.py UNITS_DIR -> brightness, contrast and light direction of mainline Wesnoth base unit sprites (72x72, no '-' in name)
import sys, os, glob, numpy as np
from PIL import Image
B = sys.argv[1]; rows = []
for p in sorted(glob.glob(os.path.join(B, '*', '**', '*.png'), recursive=True)):
    n = os.path.basename(p)[:-4]
    if '-' in n or 'ellipse' in n: continue
    im = Image.open(p)
    if im.size != (72, 72): continue
    a = np.asarray(im.convert('RGBA')).astype(np.float32); m = a[..., 3] > 230
    if m.sum() < 150: continue
    L = 0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2]; l = L[m]; ys, xs = np.nonzero(m)
    # light direction: correlation of brightness with x (right +) and y (down +), inside the unit
    cx = np.corrcoef(xs, l)[0, 1]; cy = np.corrcoef(ys, l)[0, 1]
    g = np.abs(L - np.roll(L, 1, 1)) + np.abs(L - np.roll(L, 1, 0)); inner = m & np.roll(m, 1, 0) & np.roll(m, 1, 1)
    mx = a[..., :3].max(2); mn = a[..., :3].min(2); sat = ((mx - mn) / np.maximum(mx, 1))[m].mean() * 100
    rows.append((os.path.relpath(p, B).split(os.sep)[0], n, l.mean(), l.std(), np.percentile(l, 10), np.percentile(l, 90), (l < 25).mean() * 100, cx, cy, g[inner].mean() / 2, sat, m.sum()))
R = np.array([r[2:] for r in rows], float)
hdr = ('lum', 'std', 'p10', 'p90', 'crush%', 'corr x', 'corr y', 'detail', 'sat', 'px')
print('%d mainline base sprites' % len(rows))
print('%-10s' % '' + ''.join('%8s' % h for h in hdr))
for q, name in ((50, 'median'), (25, 'p25'), (75, 'p75')): print('%-10s' % name + ''.join('%8.2f' % v for v in np.percentile(R, q, axis=0)))
print('%-10s' % 'mean' + ''.join('%8.2f' % v for v in R.mean(0)))
print('p90/p10 median %.2f' % np.median(R[:, 3] / np.maximum(R[:, 2], 1)))
print('share lit from right (corr x > 0): %.0f%%, from top (corr y < 0): %.0f%%' % ((R[:, 5] > 0).mean() * 100, (R[:, 6] < 0).mean() * 100))
for fac in sorted(set(r[0] for r in rows)):
    S = np.array([r[2:] for r in rows if r[0] == fac], float)
    print('%-20s n=%3d lum %5.0f std %5.1f p10 %4.0f p90 %4.0f crush %4.1f corr x %+.2f y %+.2f' % (fac, len(S), *np.median(S[:, [0, 1, 2, 3, 4, 5, 6]], 0)))
for r in rows:
    if r[0] == 'transport': print('  ', r[1], 'lum %.0f std %.1f p10 %.0f p90 %.0f' % r[2:6])
