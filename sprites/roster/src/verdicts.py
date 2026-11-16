# python3 -I verdicts.py -> metrics of every earlier lighting render D gave a verdict on
import sys, os, numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lightlab import metrics, U
from sprite72 import make72
S = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ks = ('lum', 'std', 'p10', 'p90', 'crush', 'det', 'edgeL')
def m(path, uid): return metrics(uid, img=make72(Image.open(path), bool(U[uid].get('pop')), 6))
def row(lab, ms): print('%-30s' % lab + ''.join('%7.1f' % np.mean([x[k] for x in ms]) for k in ks))
print('%-30s' % '' + ''.join('%7s' % k for k in ks))
V = {10: 'FAV', 8: 'FAV', 1: 'good', 14: 'ok', 15: 'neat', 4: 'dark ships', 3: 'no: harsh', 11: 'no: harsh', 5: 'no: flat', 12: 'no: flat', 13: 'no: flat', 7: 'no: front'}
print('Maquis raider rigs')
for n in sorted(V, key=lambda n: ('FAV good ok neat dark no'.split().index(V[n].split(':')[0].split()[0]), n)): row('  %02d %s' % (n, V[n]), [m(os.path.join(S, 'raider-rigs/rig%02d.png' % n), 'mq-raider')])
sample = ['fed-galaxy', 'fed-akira', 'kl-kvort', 'kl-ktinga', 'ca-galor', 'jh-attack', 'mq-fighter', 'mq-dreadnought']
print('8-ship sample (14 best in general; 1 too bright)')
for r in ('rig14', 'rig01', 'rig10', 'rig08', 'rig15', 'rig04'): row('  ' + r, [m(os.path.join(S, 'lightsample', i, r + '.png'), i) for i in sample])
print('flat ships (14soft best)')
for r in ('rig14soft', 'rig14', 'rig08', 'rig08b', 'rig01'): row('  ' + r, [m(os.path.join(S, 'flat', i, r + '.png'), i) for i in ('fed-defiant', 'kl-neghvar', 'cap-constellation')])
print('whole roster (14soft better than 14 almost everywhere)')
for r in ('r14soft', 'r14'): row('  ' + r, [m(os.path.join(S, 'all14', r, i + '.png'), i) for i in U if os.path.exists(os.path.join(S, 'all14', r, i + '.png'))])
