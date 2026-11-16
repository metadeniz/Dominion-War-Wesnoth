# python3 -I exp_abcd.py -> at equal brightness and equal shadow-side brightness, which light positions keep the most shape and detail
import sys, os, json, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lightlab import metrics, at_lum, scaled, U
KEY = 'K1f'
BASE = {KEY: 3.4, 'O': 0.5, 'R': 1.0}
def solve(uid, base, fill, p10_t, lum_t):
    """fill strength (bisection) and overall exposure so the sprite hits both the target shadow side (p10) and brightness"""
    lo, hi = 0.0, 4.0
    for _ in range(9):
        f = (lo + hi) / 2; mix = dict(base, **{fill: base.get(fill, 0) + f}); s, m = at_lum(uid, mix, lum_t)
        if m['p10'] < p10_t: lo = f
        else: hi = f
    return f, s, m
out = {}
for uid in U:
    ref_mix = dict(BASE, F1=0.6); ref = metrics(uid, ref_mix); r = {'ref': ref}
    for fill in ('F1', 'F2', 'F3', 'H'):                                   # A: where the fill comes from
        f, s, m = solve(uid, BASE, fill, ref['p10'], ref['lum']); r['A_' + fill] = dict(m, f=f, s=s)
    for key in ('K2f', 'K4f', 'K3f'):                                       # B: where the key comes from (fill F1 re-solved)
        base = {key: 3.4, 'O': 0.5, 'R': 1.0}; f, s, m = solve(uid, base, 'F1', ref['p10'], ref['lum']); r['B_' + key] = dict(m, f=f, s=s)
    base = {KEY: 1.7, 'K4f': 1.7, 'O': 0.5, 'R': 1.0}; f, s, m = solve(uid, base, 'F1', ref['p10'], ref['lum']); r['B_K1f+K4f'] = dict(m, f=f, s=s)
    for o in (0.0, 0.25, 1.0):                                              # C: how much overhead light
        base = {KEY: 3.4, 'O': o, 'R': 1.0}; f, s, m = solve(uid, base, 'F1', ref['p10'], ref['lum']); r['C_O%g' % o] = dict(m, f=f, s=s)
    for rr in (0.0, 0.5, 2.0):                                              # D: how much rim light
        base = {KEY: 3.4, 'O': 0.5, 'R': rr}; f, s, m = solve(uid, base, 'F1', ref['p10'], ref['lum']); r['D_R%g' % rr] = dict(m, f=f, s=s)
    out[uid] = r; print(uid, 'done', flush=True)
json.dump(out, open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'lab/exp_abcd.json'), 'w'), indent=1)
