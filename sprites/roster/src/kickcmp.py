# python3 -I kickcmp.py ROSTER DIR_A DIR_B ID...  -> per-ship metrics of 72px sprites in two render dirs; listed ids are flagged
import sys, os, json
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sprite72 import make72
RO, A, B = sys.argv[1:4]; FLAG = set(sys.argv[4:])
U = [u for f in json.load(open(RO)) for u in f['units']]
def met(p, pop):
    s = np.asarray(make72(Image.open(p), pop, 6)).astype(np.float32); m = s[..., 3] > 230; rgb = s[..., :3]
    L = 0.299 * rgb[..., 0] + 0.587 * rgb[..., 1] + 0.114 * rgb[..., 2]; l = L[m]
    ys, xs = np.nonzero(m); cx = xs.mean(); left = L[m & (np.arange(m.shape[1])[None, :] < cx)].mean(); right = L[m & (np.arange(m.shape[1])[None, :] >= cx)].mean()
    g = np.abs(L - np.roll(L, 1, 1)) + np.abs(L - np.roll(L, 1, 0)); inner = m & np.roll(m, 1, 0) & np.roll(m, 1, 1)
    mx = rgb.max(2); mn = rgb.min(2); sat = ((mx - mn) / np.maximum(mx, 1))[m].mean() * 100
    return dict(lum=l.mean(), std=l.std(), p10=np.percentile(l, 10), p90=np.percentile(l, 90), rl=right / max(left, 1), det=g[inner].mean() / 2, sat=sat)
rows = []
print('%-18s %-4s %5s>%-5s %5s>%-5s %5s>%-5s %5s>%-5s %5s>%-5s %4s>%-4s' % ('ship', '', 'lum', '', 'std', '', 'p10', '', 'p90/p10', '', 'R/L', '', 'sat', ''))
for u in U:
    i = u['id']; pop = bool(u.get('pop')); a = met(os.path.join(A, i + '.png'), pop); b = met(os.path.join(B, i + '.png'), pop); rows.append((i in FLAG, a, b))
    print('%-18s %-4s %5.0f>%-5.0f %5.1f>%-5.1f %5.0f>%-5.0f %5.2f>%-5.2f %5.2f>%-5.2f %4.0f>%-4.0f' % (i, '*' if i in FLAG else '', a['lum'], b['lum'], a['std'], b['std'], a['p10'], b['p10'], a['p90'] / a['p10'], b['p90'] / b['p10'], a['rl'], b['rl'], a['sat'], b['sat']))
for flag, name in ((True, 'flagged'), (False, 'others')):
    rr = [(a, b) for f, a, b in rows if f == flag]
    if not rr: continue
    av = lambda k, j: np.mean([r[j][k] for r in rr])
    print('%-18s      lum %.0f>%.0f  std %.1f>%.1f  p10 %.0f>%.0f  p90/p10 %.2f>%.2f  R/L %.2f>%.2f  sat %.0f>%.0f' % (name + ' (%d)' % len(rr), av('lum', 0), av('lum', 1), av('std', 0), av('std', 1), av('p10', 0), av('p10', 1), np.mean([r[0]['p90'] / r[0]['p10'] for r in rr]), np.mean([r[1]['p90'] / r[1]['p10'] for r in rr]), av('rl', 0), av('rl', 1), av('sat', 0), av('sat', 1)))
