# python3 -I exp_abcd_report.py -> summary of exp_abcd.json: each variant vs the reference (setup 2 with the shadow fix), at equal brightness and shadow side
import sys, os, json, numpy as np
S = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J = json.load(open(os.path.join(S, 'lab/exp_abcd.json')))
sh = json.load(open(os.path.join(S, 'shapestats.json')))
ks = ('std', 'det', 'shape', 'edgeL', 'p90', 'crush')
names = [k for k in next(iter(J.values())) if k != 'ref']
print('%-12s' % 'variant' + ''.join('%8s' % k for k in ks) + '   fill  wins(std)  lum-err p10-err')
for n in names:
    d = {k: np.mean([J[u][n][k] - J[u]['ref'][k] for u in J]) for k in ks}
    wins = sum(J[u][n]['std'] > J[u]['ref']['std'] + 0.3 for u in J)
    le = np.mean([abs(J[u][n]['lum'] - J[u]['ref']['lum']) for u in J]); pe = np.mean([abs(J[u][n]['p10'] - J[u]['ref']['p10']) for u in J])
    print('%-12s' % n + ''.join('%+8.2f' % d[k] for k in ks) + '   %4.2f   %2d/%d   %5.1f %5.1f' % (np.mean([J[u][n]['f'] for u in J]), wins, len(J), le, pe))
# shape groups
groups = {'flat top (up>0.8)': [u for u in J if sh[u]['up'] > 0.8], 'angled (up<0.6)': [u for u in J if sh[u]['up'] < 0.6], 'middle': [u for u in J if 0.6 <= sh[u]['up'] <= 0.8]}
for g, us in groups.items():
    print('\n' + g, len(us), ', '.join(us))
    for n in names:
        print('  %-12s' % n + ''.join('%+8.2f' % np.mean([J[u][n][k] - J[u]['ref'][k] for u in us]) for k in ks))
