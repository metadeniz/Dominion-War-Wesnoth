# python3 -I strategies3.py OUT.json [TR_FLOOR] -> per-ship light mixes. Fill (front left) grows until the lighting ratio reaches the
# style's target OR the whole-sprite contrast falls to the floor, whichever comes first; then exposure sets the brightness.
#   lr = stops between the lit and the shadowed tenth of the hull with the paint divided out (the light alone)
#   tr = stops between the bright and the dark tenth of the hull as seen (light and paint together)
import sys, os, json, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lightlab import metrics, at_lum, scaled, U
DRAMATIC = {u for u in U if u.startswith('kl-')}
LR = {'standard': 1.25, 'dramatic': 1.85}; TR_FLOOR = float(sys.argv[2]) if len(sys.argv) > 2 else 1.6
def target_lum(L0, C=88, keep_lo=0.5, keep_hi=0.25, lo=55, hi=100):
    return float(np.clip(C + (L0 - C) * (keep_lo if L0 < C else keep_hi), lo, hi))
def ok(m, lr_t): return m['lr'] > lr_t and m['tr'] > TR_FLOOR          # still room for more fill
def fill_for(uid, base, lr_t, cap):
    if not ok(metrics(uid, base), lr_t): return 0.0
    if ok(metrics(uid, dict(base, F1=cap)), lr_t): return cap
    lo, hi = 0.0, cap
    for _ in range(8):
        f = (lo + hi) / 2
        if ok(metrics(uid, dict(base, F1=f)), lr_t): lo = f
        else: hi = f
    return (lo + hi) / 2
CANDS = {'A': {'K1f': 3.4, 'O': 0.5, 'R': 1.0}, 'C': {'K1f': 3.4, 'O': 0.0, 'R': 0.5}}
REF = {'K1f': 3.4, 'O': 0.5, 'R': 1.0, 'F1': 0.6}
out = {c: {} for c in CANDS}; out['ref_expo'] = {}; out['target'] = {}
for uid in U:
    m0 = metrics(uid, REF); L = target_lum(m0['lum']); style = 'dramatic' if uid in DRAMATIC else 'standard'
    s, _ = at_lum(uid, REF, L); out['ref_expo'][uid] = {k: round(v, 3) for k, v in scaled(REF, s).items()}; out['target'][uid] = [m0['lum'], L, style]
    line = '%-18s %-8s L0 %3.0f -> %3.0f |' % (uid, style, m0['lum'], L)
    for c, base in CANDS.items():
        f = fill_for(uid, base, LR[style], 0.4 * base['K1f']); mix = dict(base, F1=f); s, m = at_lum(uid, mix, L)
        out[c][uid] = {k: round(v, 3) for k, v in scaled(mix, s).items()}
        line += ' %s: fill %.2f exp x%.2f lr %.2f tr %.2f con %4.1f |' % (c, f, s, m['lr'], m['tr'], m['std'])
    print(line, flush=True)
json.dump(out, open(sys.argv[1], 'w'), indent=1)
