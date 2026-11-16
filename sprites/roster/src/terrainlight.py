# python3 -I terrainlight.py IMAGES_DIR  -> which side Wesnoth terrain art is lit from, and where shadows fall
import sys, glob, os
import numpy as np
from PIL import Image
B = sys.argv[1]
def lr(p):
    a = np.asarray(Image.open(p).convert('RGBA')).astype(float); m = a[..., 3] > 200
    L = 0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2]; ys, xs = np.nonzero(m); cx = xs.mean()
    X = np.arange(a.shape[1])[None, :]
    return L[m & (X < cx)].mean(), L[m & (X >= cx)].mean(), np.corrcoef(xs, L[m])[0, 1], np.corrcoef(ys, L[m])[0, 1]
for pat in ['terrain/mountains/basic*.png', 'terrain/mountains/dry*.png', 'terrain/mountains/snow*.png', 'terrain/hills/regular*.png', 'terrain/hills/desert*.png', 'terrain/hills/dry*.png']:
    fs = [f for f in sorted(glob.glob(os.path.join(B, pat))) if not any(t in os.path.basename(f) for t in ('-n', '-s', 'castle', '-e', '-w'))][:6]
    if not fs: continue
    r = np.array([lr(f) for f in fs]); print('%-30s n=%d left %.0f right %.0f  corr(L,x) %+.2f corr(L,y) %+.2f' % (pat, len(fs), *r.mean(0)))
def shadow(p):
    a = np.asarray(Image.open(p).convert('RGBA')).astype(float); al = a[..., 3]
    sh = (al > 40) & (al < 210) & (a[..., :3].max(2) < 70); obj = al >= 230
    if sh.sum() < 5: return None
    ys, xs = np.nonzero(obj); sy, sx = np.nonzero(sh)
    return 'shadow offset x %+.1f y %+.1f px, %d px, colour %s, alpha %.0f' % (sx.mean() - xs.mean(), sy.mean() - ys.mean(), sh.sum(), tuple(a[sh][:, :3].mean(0).round()), al[sh].mean())
for p in ['terrain/village/human.png', 'terrain/village/elven.png', 'terrain/castle/castle-convex-bl.png', 'terrain/castle/castle-concave-tr.png', 'terrain/forest/pine.png', 'units/human-loyalists/spearman.png', 'units/drakes/glider.png', 'units/monsters/gryphon.png']:
    print('%-40s %s' % (p, shadow(os.path.join(B, p))))
