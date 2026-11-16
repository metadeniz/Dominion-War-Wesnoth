# RJSON=roster-lab.json python3 -I buildopt.py STRATEGIES.json CAND OUT_ROSTER.json -> roster with each ship's solved light rig (real-render form)
# D's own per-ship picks (runabout option 5, Jem'Hadar battleship rig 8, Maquis raider rig 10) keep their lights; only the shadow fix and
# the brightness rule are applied to them.
import sys, os, json, copy
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lightlab import at_lum, scaled, metrics
J = json.load(open(sys.argv[1])); cand = sys.argv[2]; R = json.load(open(os.environ['RJSON']))
POS = {'K1f': [7, 2.5, -0.5], 'O': [0, 8, 0.3], 'R': [-6, 2, -4], 'F1': [-4, 2, 5]}
PICKS = {'fed-danube': {'K1f': 3.4, 'O': 0.5, 'R': 1.0, 'F1': 0.6}, 'jh-battleship': {'K1f': 3.4, 'R': 1.2}, 'mq-raider': {'K1f': 3.4, 'F1': 0.6, 'H': 0.1}}
def rig(mix):
    L = [{'dir': round(mix['K1f'], 3), 'pos': POS['K1f'], 'nb': 0, 'bias': -0.0015}]
    for k in ('O', 'R', 'F1'):
        if mix.get(k, 0) > 0.001: L.append({'dir': round(mix[k], 3), 'pos': POS[k], 'shadow': False})
    return {'hemi': round(mix.get('H', 0), 3), 'lights': L, 'shadowPos': [0, 10, 0.001], 'recvAll': True}
for f in R:
    for u in f['units']:
        if u['id'] in PICKS:
            s, m = at_lum(u['id'], PICKS[u['id']], J['target'][u['id']][1]); mix = scaled(PICKS[u['id']], s); u['light_note'] = "D's pick, brightness rule applied (x%.2f)" % s
        else: mix = J[cand][u['id']]
        u['light'] = rig(mix); u['mix'] = mix
json.dump(R, open(sys.argv[3], 'w'), indent=1); print('wrote', sys.argv[3])
