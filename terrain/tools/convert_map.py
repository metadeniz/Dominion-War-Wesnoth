#!/usr/bin/env python3
"""Converts a Wesnoth .map file to the space terrain, the same way the game does at the start
(terrain/lua/space_terrain.lua). Use it to look at a map in the editor, or as a start for a
hand-polished space version of a map.

    python3 convert_map.py IN.map OUT.map

Keep this file and space_terrain.lua in step: they hold the same table and the same rules.
"""
import sys

def neighbours(x, y):
    """The six neighbours of (x, y) in 1-based map coordinates (even columns sit half a hex lower)."""
    if x % 2 == 0:
        return [(x, y - 1), (x + 1, y), (x + 1, y + 1), (x, y + 1), (x - 1, y + 1), (x - 1, y)]
    return [(x, y - 1), (x + 1, y - 1), (x + 1, y), (x, y + 1), (x - 1, y), (x - 1, y - 1)]

def bridge_dir(o):
    for c in '|/\\':
        if c in o: return c
    return '|'

def convert_overlay(o):
    """Returns the new overlay ('' to drop it), or 'IMP' / 'UNWALK' when the overlay makes the hex a barrier."""
    if not o: return ''
    if o.startswith('Xm') or o == 'Xo' or (o[:2] in ('Pr', 'Pw') and not o.endswith('o')): return 'IMP'
    if o in ('Qov', 'Eqf'): return 'UNWALK'
    if o[0] == 'F': return 'Zfa' if o in ('Fpa', 'Fda', 'Fma') else 'Zf'
    if o in ('Tf', 'Tfi'): return 'Zt'
    if o in ('Uf', 'Ufi'): return 'Zto'
    if o[0] == 'V': return 'Zvo' if o in ('Vm', 'Vov') else 'Zv'
    if o[0] == 'B':
        d = bridge_dir(o)
        if o.startswith('Bs') and not o.startswith('Bsb'): return 'Zw' + d
        if o.startswith('Br'): return 'Zy' + d
        return 'Zu' + d
    if o == 'Dr': return 'Zr'
    if o == 'Do': return 'Zo'
    if o == 'Cov': return 'Zco'
    if o == 'Kov': return 'Zko'
    return ''      # flowers, stones, farms, lights and other decorations: open space

CASTLE_GROUP = {'Cea': 'a', 'Coa': 'a', 'Cha': 'a', 'Kea': 'a', 'Koa': 'a', 'Kha': 'a',
                'Chw': 'w', 'Khw': 'w', 'Chs': 's', 'Khs': 's', 'Cm': 'r', 'Cme': 'r', 'Km': 'r', 'Kme': 'r'}

def convert_base(b):
    """Plain bases. Castles, keeps and impassable hexes are settled later from their neighbours."""
    c = b[:1]
    if c in 'CK': return 'CASTLE'
    if c == 'X': return 'IMP'
    if c == 'W':
        if b == 'Wwf': return 'Zsf'
        if b.startswith('Wo'): return 'Zbd'
        if b.startswith('Wwr'): return 'Zbr'
        return 'Zb'
    if c == 'S': return 'Zbs'
    if c == 'R': return 'Zsl' if b.startswith('Rr') else 'Zs'
    if c == 'U':
        if b.startswith('Uh'): return 'Zvh'
        if b.startswith('Uu'): return 'Zv'
        return 'Zs'
    if c == 'T': return 'Zt'
    if c == 'A': return 'Za'
    if c == 'D': return 'Zd'
    if c == 'H': return 'Zhd' if b == 'Hd' else 'Zha' if b == 'Ha' else 'Zh'
    if c == 'M':
        if b == 'Mv': return 'Zl'
        return 'Zma' if b == 'Ms' else 'Zm'
    if c == 'Q': return 'Zl' if b.startswith('Ql') else 'Zq'
    return 'Zs'     # grass, dirt, floors and anything unknown: open space

def classify_impassable(imp, W, H):
    """Impassable hexes are drawn by the shape of their cluster (D, 16 Nov):
    touching the map's edge -> the Void; a lone hex -> black hole, pulsar or eddy;
    a thick blob -> plasma storm (12+ hexes) or, alternating, Briar Patch / radiation zone;
    a thin line -> a chain of gravitational eddies."""
    out = {}; seen = set(); lone_i = 0; area_i = 0
    LONE = ['Zxk', 'Zxj', 'Zxk', 'Zxe']
    for p in sorted(imp):
        if p in seen: continue
        comp = []; st = [p]; seen.add(p)
        while st:
            q = st.pop(); comp.append(q)
            for n in neighbours(*q):
                if n in imp and n not in seen: seen.add(n); st.append(n)
        edge = any(x <= 1 or y <= 1 or x >= W or y >= H for x, y in comp)
        thick = sum(sum(n in imp for n in neighbours(*q)) >= 4 for q in comp)
        if edge: code = 'Zxn'
        elif len(comp) == 1: code = LONE[lone_i % len(LONE)]; lone_i += 1
        elif thick >= 3 or (thick >= 1 and len(comp) >= 6):
            if len(comp) >= 12: code = 'Zxp'
            else: code = ['Zxq', 'Zxr'][area_i % 2]; area_i += 1
        else: code = 'Zxe'
        for q in comp: out[q] = code
    return out

def convert(rows):
    """rows: list of lists of terrain codes, including the border (row 0 and column 0 are border)."""
    Hf, Wf = len(rows), len(rows[0])
    W, H = Wf - 2, Hf - 2                  # playable size
    def parse(c):
        c = c.strip(); start = ''
        if ' ' in c: start, c = c.split(' ', 1)
        b, _, o = c.partition('^')
        return start, b, o
    cells = {}; imp = set(); castles = {}
    for y in range(Hf):
        for x in range(Wf):
            start, b, o = parse(rows[y][x])
            if b.startswith('_') or (o and o.startswith('_')):          # off-map, fog and shroud markers stay
                cells[(x, y)] = (start, b + ('^' + o if o else '')); continue
            nb, no = convert_base(b), convert_overlay(o)
            if no == 'IMP' or nb == 'IMP': imp.add((x, y)); cells[(x, y)] = (start, None); continue
            if no == 'UNWALK': nb, no = 'Zq', ''
            if nb == 'CASTLE': castles[(x, y)] = b; cells[(x, y)] = (start, None, no); continue
            cells[(x, y)] = (start, nb + ('^' + no if no else ''))
    # castles: drydocks when joined to a keep, outposts when not (D)
    joined = set()
    for p, b in castles.items():
        if b[0] != 'K' or p in joined: continue
        st = [p]; joined.add(p)
        while st:
            q = st.pop()
            for n in neighbours(*q):
                if n in castles and n not in joined: joined.add(n); st.append(n)
    for p, b in castles.items():
        g = CASTLE_GROUP.get(b, ''); ruined = 'r' in b[1:]
        if b[0] == 'K': code = 'Zk' + ('x' if ruined else '') + g
        elif p in joined: code = 'Zc' + ('b' if ruined else 'd') + g
        else: code = 'Zc' + ('x' if ruined else 'o') + g
        start, _, no = cells[p]
        cells[p] = (start, code + ('^' + no if no else ''))
    for p, code in classify_impassable(imp, W, H).items():
        cells[p] = (cells[p][0], code)
    return [[(cells[(x, y)][0] + ' ' if cells[(x, y)][0] else '') + cells[(x, y)][1] for x in range(Wf)] for y in range(Hf)]

def read_map(path):
    return [[c.strip() for c in l.split(',')] for l in open(path).read().strip().splitlines() if l.strip()]

if __name__ == '__main__':
    rows = read_map(sys.argv[1])
    out = convert(rows)
    open(sys.argv[2], 'w').write('\n'.join(', '.join(r) for r in out) + '\n')
