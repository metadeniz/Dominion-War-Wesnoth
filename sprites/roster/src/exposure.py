# python3 -I exposure.py ROSTER_IN DIR ROSTER_OUT [ceiling=95 keep=0.3]
# For each ship rendered in DIR ({id}.png, 288 x canvas/72), measures the 72px sprite's brightness L and, when L is above
# the ceiling, scales every light of the ship's rig by k = (T/L)^2.2 with T = ceiling + (L - ceiling) * keep,
# so very bright hulls come down while staying a little brighter than the rest. Ships at or below the ceiling are unchanged.
# Self-lit parts (emissive) are not scaled, so engine glows keep their strength.
import sys, json, os, copy
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sprite72 import make72
RI, D, RO = sys.argv[1:4]; CEIL = float(sys.argv[4]) if len(sys.argv) > 4 else 95; KEEP = float(sys.argv[5]) if len(sys.argv) > 5 else 0.3
R = json.load(open(RI))
def lum(path, pop):
    a = np.asarray(make72(Image.open(path), pop, 6)).astype(np.float32); m = a[..., 3] > 230
    return (0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2])[m].mean()
for f in R:
    for u in f['units']:
        L = float(lum(os.path.join(D, u["id"] + ".png"), bool(u.get("pop"))))
        k0 = u.get('light', {}).get('exposure', 1.0)
        if L <= CEIL + 0.5: continue
        T = CEIL + (L - CEIL) * KEEP; k = (T / L) ** 2.2
        l = u['light'] = copy.deepcopy(u['light'])
        for x in l['lights']: x['dir'] = round(x['dir'] * k, 3)
        l['hemi'] = round(l.get('hemi', 0) * k, 3); l['exposure'] = round(k0 * k, 3)
        print('%-18s L %5.1f -> target %5.1f  lights x%.2f (total x%.2f)' % (u['id'], L, T, k, l['exposure']))
json.dump(R, open(RO, 'w'), indent=1)
