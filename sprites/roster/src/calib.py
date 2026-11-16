# python3 -I calib.py -> metrics of every ship under setup 1 (14soft) and setup 2 (14soft + front-left 0.6), from the passes
import sys, os, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lightlab import metrics, U
SOFT = {'K1': 3.4, 'O': 0.5, 'R': 1.0}; KICK = dict(SOFT, F1=0.6)
WORSE = {'kl-brel', 'kl-ktinga', 'kl-raptor', 'kl-promellian', 'kl-kvort', 'kl-neghvar'}
ks = ('lum', 'std', 'p10', 'p90', 'shape', 'paint', 'det', 'crush')
print('%-18s %2s ' % ('ship', '') + ' '.join('%11s' % k for k in ks))
rows = []
for uid in U:
    a = metrics(uid, SOFT); b = metrics(uid, KICK); rows.append((uid, a, b))
    print('%-18s %2s ' % (uid, 'W' if uid in WORSE else '') + ' '.join('%5.1f>%-5.1f' % (a[k], b[k]) for k in ks))
for name, sel in (('flagged worse', lambda u: u in WORSE), ('others', lambda u: u not in WORSE)):
    rr = [(a, b) for u, a, b in rows if sel(u)]
    print('%-21s ' % name + ' '.join('%5.1f>%-5.1f' % (np.mean([r[0][k] for r in rr]), np.mean([r[1][k] for r in rr])) for k in ks))
