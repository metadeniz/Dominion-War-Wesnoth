# python3 -I exp_ratio.py KEY -> lighting ratio (stops between the lit tenth and the shadowed tenth of the hull, paint removed) under setups 1 and 2
import sys, os, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lightlab import metrics, U
K = sys.argv[1] if len(sys.argv) > 1 else 'K1'
S1 = {K: 3.4, 'O': 0.5, 'R': 1.0}; S2 = dict(S1, F1=0.6)
W = {'kl-brel', 'kl-ktinga', 'kl-raptor', 'kl-promellian', 'kl-kvort', 'kl-neghvar'}
r = {u: (metrics(u, S1)['lr'], metrics(u, S2)['lr']) for u in U}
for u, (a, b) in r.items(): print('%-18s %s setup1 %.2f stops (%.1f:1)  setup2 %.2f stops (%.1f:1)' % (u, 'W' if u in W else ' ', a, 2 ** a, b, 2 ** b))
for n, sel in (('flagged', lambda u: u in W), ('others', lambda u: u not in W)):
    v = np.array([r[u] for u in r if sel(u)]); print(n, 'setup1 %.2f stops, setup2 %.2f stops' % tuple(v.mean(0)))
