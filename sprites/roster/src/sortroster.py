"""Order each faction's ships for the sprite sheet (D's rules):
1. by cost from the design doc, cheapest first; equal cost puts the level 0 ship first;
2. a ship with no cost yet goes where its size fits between its neighbours: the first gap whose ship before
   is smaller and ship after is larger (size = sprite area, opaque pixels of the 72px sprite); smaller than all
   of them puts it first after the level 0 ships, larger than all puts it last;
3. leader-only ships last.
Also stores each ship's price as "cost" (leader-only prices come from the doc's **Leader-only:** lines) for the sheet.
Usage: python3 -I sortroster.py roster2.json faction-rosters.md SPRITEDIR [--write]"""
import json, sys, re
import numpy as np
from PIL import Image

def doc_costs(md):
    out = {}; L = open(md).read().split('\n')
    for i, l in enumerate(L):
        if l.startswith('| Ship |') and i + 1 < len(L) and L[i + 1].startswith('|---'):
            h = [c.strip() for c in l.strip('|').split('|')]; ci, li = h.index('Cost'), h.index('Lvl')
            for r in L[i + 2:]:
                if not r.startswith('| '): break
                c = [x.strip() for x in r.strip('|').split('|')]
                out[c[0]] = (int(c[ci]) if c[ci].isdigit() else None, int(c[li]) if c[li].isdigit() else 1)
        m = re.match(r'\*\*Leader-only:\*\* ([^:]+): [^,]+, (\d+)', l)
        if m: out[m.group(1).strip()] = (int(m.group(2)), 1)
    return out

def cost_of(u, costs):
    n = u['name']; c = costs.get(n) or costs.get(re.sub(r' \(leader\)$', '', n))
    return c[0] if c else None

def area(path):
    a = np.asarray(Image.open(path).convert('RGBA')); return int((a[..., 3] > 230).sum())

def order(units, costs, sprites):
    lead = [u for u in units if u.get('leader')]; rest = [u for u in units if not u.get('leader')]
    info = {}
    for u in rest:
        if u['name'] not in costs: raise SystemExit('not in design doc: ' + u['name'])
        info[u['id']] = costs[u['name']] + (area(f"{sprites}/{u['id']}.png"),)
    costed = sorted([u for u in rest if info[u['id']][0] is not None], key=lambda u: (info[u['id']][0], info[u['id']][1] != 0))
    for u in sorted([u for u in rest if info[u['id']][0] is None], key=lambda u: info[u['id']][2]):
        s = info[u['id']][2]; sizes = [info[c['id']][2] for c in costed]; at = len(costed)
        for k in range(1, len(costed)):
            if sizes[k - 1] <= s <= sizes[k]: at = k; break
        else:
            if sizes and s < min(sizes): at = sum(1 for c in costed if info[c['id']][1] == 0)   # smallest: first after the level 0 ships
        costed.insert(at, u)
    lead = sorted(lead, key=lambda u: cost_of(u, costs) if cost_of(u, costs) is not None else 999)   # leader-only ships last, cheapest first
    return costed + lead, info

if __name__ == '__main__':
    rj, md, sp = sys.argv[1:4]; d = json.load(open(rj)); costs = doc_costs(md)
    for f in d:
        f['units'], info = order(f['units'], costs, sp)
        for u in f['units']:
            c = cost_of(u, costs)
            if c is None: u.pop('cost', None); print('  no price:', u['name'])
            else: u['cost'] = c
        print(f['faction'], [(u['id'],) + info.get(u['id'], ('leader',)) for u in f['units']])
    if '--write' in sys.argv:
        json.dump(d, open(rj, 'w'), indent=2, ensure_ascii=False)
        # put the design doc's ship tables in the same order
        rank = {u['name']: i for f in d for i, u in enumerate(f['units'])}
        L = open(md).read().split('\n'); i = 0
        while i < len(L):
            if L[i].startswith('| Ship |') and i + 1 < len(L) and L[i + 1].startswith('|---'):
                j = i + 2
                while j < len(L) and L[j].startswith('| '): j += 1
                L[i + 2:j] = sorted(L[i + 2:j], key=lambda r: rank.get(r.strip('|').split('|')[0].strip(), 999)); i = j
            else: i += 1
        open(md, 'w').write('\n'.join(L))
