# python3 -I lightmetrics.py  -> prints lighting metrics of the 72px sprites for every rig D has rated
import sys, os, json, glob
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sprite72 import make72
S = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
U = {u['id']: u for f in json.load(open(os.path.join(S, 'r3d/roster2.json'))) for u in f['units']}
def met(path, uid):
    im = Image.open(path); s = np.asarray(make72(im, bool(U.get(uid, {}).get('pop')), 6)).astype(np.float32)
    m = s[..., 3] > 230; rgb = s[..., :3]; L = 0.299 * rgb[..., 0] + 0.587 * rgb[..., 1] + 0.114 * rgb[..., 2]
    l = L[m]; mx = rgb.max(2); mn = rgb.min(2); sat = ((mx - mn) / np.maximum(mx, 1))[m]
    # local detail: mean absolute difference to 4-neighbours, inside the ship
    g = np.zeros_like(L); 
    for dy, dx in ((0, 1), (1, 0)):
        g += np.abs(L - np.roll(np.roll(L, dy, 0), dx, 1))
    inner = m & np.roll(m, 1, 0) & np.roll(m, 1, 1)
    return dict(lum=l.mean(), con=l.std(), p10=np.percentile(l, 10), p90=np.percentile(l, 90), crush=(l < 25).mean() * 100, clip=(l > 235).mean() * 100, detail=g[inner].mean() / 2, sat=sat.mean() * 100)
def show(title, rows):
    print('\n' + title); print('%-34s %5s %5s %5s %5s %6s %5s %6s %5s' % ('', 'lum', 'con', 'p10', 'p90', 'crush%', 'clip%', 'detail', 'sat'))
    for name, ms in rows:
        a = {k: np.mean([m[k] for m in ms]) for k in ms[0]}
        print('%-34s %5.0f %5.1f %5.0f %5.0f %6.1f %5.1f %6.1f %5.0f' % (name, a['lum'], a['con'], a['p10'], a['p90'], a['crush'], a['clip'], a['detail'], a['sat']))
verdict = {1: 'good', 4: 'for dark ships', 8: 'FAVOURITE', 10: 'FAVOURITE', 14: 'ok', 15: 'neat'}
show('Maquis raider, 15 rigs (usual shadow)', [(f'{n:02d} {verdict.get(n, "-")}', [met(os.path.join(S, f'raider-rigs/rig{n:02d}.png'), 'mq-raider')]) for n in range(1, 16)])
sample = ['fed-galaxy', 'fed-akira', 'kl-kvort', 'kl-ktinga', 'ca-galor', 'jh-attack', 'mq-fighter', 'mq-dreadnought']
lead = ['fed-defiant', 'kl-neghvar', 'jh-battleship', 'cap-constellation', 'mq-marauder']
for title, d, ids in (('8-ship sample (D: 14 best in general, 1 too bright)', 'lightsample', sample), ('Leaders', 'lightsample-lead', lead)):
    show(title, [(r, [met(os.path.join(S, d, i, r + '.png'), i) for i in ids]) for r in ('now', 'rig01', 'rig10', 'rig08', 'rig14', 'rig15', 'rig04')])
show('Flat ships (D: 14soft best)', [(r, [met(os.path.join(S, 'flat', i, r + '.png'), i) for i in ('fed-defiant', 'kl-neghvar', 'cap-constellation')]) for r in ('rig14', 'rig14soft', 'rig08', 'rig08b', 'rig01')])
allids = [u for u in U]
show('Whole roster (D: 14soft better almost everywhere)', [(r, [met(os.path.join(S, 'all14', r, i + '.png'), i) for i in allids]) for r in ('r14', 'r14soft')])
show('Runabout (D likes the earlier lighting)', [(n, [met(os.path.join(S, 'run', f + '.png'), 'fed-danube')]) for n, f in (('earlier default', 'earlier'), ('14', 'r14'), ('14soft', 'r14soft'))])
# spread of brightness across ships under each roster rig
for r in ('r14', 'r14soft'):
    ls = sorted((met(os.path.join(S, 'all14', r, i + '.png'), i)['lum'], i) for i in allids)
    print(r, 'brightness range across ships: %.0f..%.0f, darkest:' % (ls[0][0], ls[-1][0]), ', '.join('%s %.0f' % (i, l) for l, i in ls[:6]), '| brightest:', ', '.join('%s %.0f' % (i, l) for l, i in ls[-4:]))
