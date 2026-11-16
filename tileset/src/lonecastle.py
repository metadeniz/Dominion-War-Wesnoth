# Lone castle hex prototypes (D, 16 Nov): centre kept empty for the unit, dressing near the walls only.
import math, random
from PIL import Image, ImageDraw, ImageFilter, ImageFont
src = open('mock.py').read()
ns = {}
exec("import math, random\nfrom PIL import Image, ImageDraw, ImageFilter\n" + src[src.index('HEXV = ['):src.index('def _hexpoly')] + src[src.index('def _lit'):src.index('def arch')], ns)
shield_layer, HEXV, _lit, FRAME = ns['shield_layer'], ns['HEXV'], ns['_lit'], ns['FRAME']
S, SS, C = 72, 3, 36
P = lambda pts: [(x * SS, y * SS) for x, y in pts]
VERT = [(C + 36 * math.cos(math.radians(60 * i + 180)), C + 36 * math.sin(math.radians(60 * i + 180))) for i in range(6)]  # W, NW, NE, E, SE, SW
def toward(p, k):  # point moved k px from a hex vertex/edge toward the centre
    dx, dy = C - p[0], C - p[1]; L = math.hypot(dx, dy); return (p[0] + dx / L * k, p[1] + dy / L * k)
def canvas(): im = Image.new('RGBA', (S * SS, S * SS)); return im, ImageDraw.Draw(im), Image.new('RGBA', (S * SS, S * SS))
def finish(im, glow): return Image.alpha_composite(glow.filter(ImageFilter.GaussianBlur(2.5 * SS)), im).resize((S, S), Image.LANCZOS)
def scorch(d, p, r_):
    for k in range(3): d.ellipse(P([(p[0] - r_ + k, p[1] - r_ * .7 + k), (p[0] + r_ - k, p[1] + r_ * .7 - k)]), fill=(30, 22, 18, 90))

def turret(d, dg, p, ang, lit=True, wrecked=False):
    x, y = p
    if wrecked:
        d.ellipse(P([(x - 3, y - 2.5), (x + 3, y + 2.5)]), fill=(52, 48, 46, 255)); d.line(P([(x, y), (x + 4 * math.cos(ang + 2), y + 4 * math.sin(ang + 2))]), fill=(90, 88, 90, 255), width=SS); return
    d.ellipse(P([(x - 4, y - 4), (x + 4, y + 4)]), fill=_lit(FRAME, 0.5)); d.ellipse(P([(x - 3, y - 3.4), (x + 3, y + 2.4)]), fill=_lit(FRAME, 0.95))
    for o in (-1.1, 1.1):
        ox, oy = -math.sin(ang) * o, math.cos(ang) * o
        d.line(P([(x + ox, y + oy), (x + 7 * math.cos(ang) + ox, y + 7 * math.sin(ang) + oy)]), fill=_lit(FRAME, 0.8), width=SS)
    if lit: d.ellipse(P([(x - .8, y - .8), (x + .8, y + .8)]), fill=(255, 90, 70, 255)); dg.ellipse(P([(x - 3, y - 3), (x + 3, y + 3)]), fill=(255, 110, 70, 120))

# A: three corner turrets at alternate vertices, barrels outward
def corner_turrets(seed=0, ruined=False):
    im, d, G = canvas(); g = ImageDraw.Draw(G); r = random.Random(seed); lost = r.randrange(3) if ruined else -1
    for k, i in enumerate([(seed % 2) + 2 * j for j in range(3)]):
        v = VERT[i]; p = toward(v, 9); ang = math.atan2(v[1] - C, v[0] - C)
        d.polygon(P([toward(VERT[i], 3), toward(((VERT[i][0] + VERT[i - 1][0]) / 2, (VERT[i][1] + VERT[i - 1][1]) / 2), 4), p, toward(((VERT[i][0] + VERT[(i + 1) % 6][0]) / 2, (VERT[i][1] + VERT[(i + 1) % 6][1]) / 2), 4)]), fill=_lit((110, 112, 120), 0.8))
        turret(d, g, p, ang, not ruined, k == lost)
        if ruined and k == lost: scorch(d, p, 6)
    return finish(im, G)

# B: battlements, armour plates along the inside of each wall, running light at each plate's middle
def battlements(seed=0, ruined=False):
    im, d, G = canvas(); g = ImageDraw.Draw(G); r = random.Random(seed)
    for i in range(6):
        a, b = VERT[i], VERT[(i + 1) % 6]
        if ruined and r.random() < 0.35: scorch(d, toward(((a[0] + b[0]) / 2, (a[1] + b[1]) / 2), 7), 5); continue
        a1, b1 = toward(a, 5), toward(b, 5); a2, b2 = toward(a, 10), toward(b, 10)
        t0, t1 = (0.12, 0.88) if not ruined else (r.uniform(.1, .35), r.uniform(.6, .9))
        L = lambda p, q, t: (p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t)
        mx, my = (a[0] + b[0]) / 2 - C, (a[1] + b[1]) / 2 - C; f = 0.6 + 0.5 * max(0, (mx * .8 - my * .6) / 31)
        d.polygon(P([L(a1, b1, t0), L(a1, b1, t1), L(a2, b2, t1), L(a2, b2, t0)]), fill=_lit((150, 152, 160), f))
        d.line(P([L(a2, b2, t0), L(a2, b2, t1)]), fill=_lit((80, 82, 90), 1), width=SS)
        m = L(L(a1, b1, .5), L(a2, b2, .5), .5)
        if not ruined: d.ellipse(P([(m[0] - .9, m[1] - .9), (m[0] + .9, m[1] + .9)]), fill=(255, 200, 110, 255)); g.ellipse(P([(m[0] - 3, m[1] - 3), (m[0] + 3, m[1] + 3)]), fill=(255, 190, 90, 110))
    return finish(im, G)

# C: six emitter pylons at the corners, joined by a faint field line close to the wall
def pylons(seed=0, ruined=False):
    im, d, G = canvas(); g = ImageDraw.Draw(G); r = random.Random(seed); pts = [toward(v, 8) for v in VERT]
    dead = {r.randrange(6), r.randrange(6)} if ruined else set()
    for i in range(6):
        a, b = pts[i], pts[(i + 1) % 6]
        if i in dead or (i + 1) % 6 in dead: continue
        g.line(P([a, b]), fill=(90, 190, 255, 120), width=2 * SS); d.line(P([a, b]), fill=(170, 225, 255, 140), width=1)
    for i, p in enumerate(pts):
        x, y = p
        if i in dead: d.ellipse(P([(x - 2.5, y - 2), (x + 2.5, y + 2)]), fill=(50, 47, 46, 255)); scorch(d, p, 5); continue
        d.polygon(P([(x, y - 4.5), (x + 3.5, y), (x, y + 4.5), (x - 3.5, y)]), fill=_lit(FRAME, 0.6)); d.polygon(P([(x, y - 4.5), (x + 3.5, y), (x, y)]), fill=_lit(FRAME, 1.0))
        if not ruined or r.random() < .5: d.ellipse(P([(x - 1, y - 1), (x + 1, y + 1)]), fill=(210, 245, 255, 255)); g.ellipse(P([(x - 3.5, y - 3.5), (x + 3.5, y + 3.5)]), fill=(90, 190, 255, 150))
    return finish(im, G)

# D: two torpedo bunkers on opposite walls and a sensor dish on a third
def bunkers(seed=0, ruined=False):
    im, d, G = canvas(); g = ImageDraw.Draw(G); r = random.Random(seed); e0 = seed % 3
    def edge_frame(i):
        a, b = VERT[i], VERT[(i + 1) % 6]; m = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
        ux, uy = (b[0] - a[0]) / 36, (b[1] - a[1]) / 36; nx, ny = (C - m[0]) / 31, (C - m[1]) / 31; return m, (ux, uy), (nx, ny)
    for k, i in enumerate([e0, e0 + 3]):
        m, (ux, uy), (nx, ny) = edge_frame(i % 6)
        Q = lambda s, t: (m[0] + ux * s + nx * t, m[1] + uy * s + ny * t)
        if ruined and k == 1:
            d.polygon(P([Q(-7, 4), Q(2, 3), Q(5, 9), Q(-6, 10)]), fill=(70, 66, 64, 255)); scorch(d, Q(0, 8), 6); continue
        d.polygon(P([Q(-9, 4), Q(9, 4), Q(7, 11), Q(-7, 11)]), fill=_lit((140, 142, 150), 0.9))
        d.polygon(P([Q(-9, 4), Q(9, 4), Q(8.4, 6), Q(-8.4, 6)]), fill=_lit((170, 172, 180), 1.0))
        for s in (-4, 0, 4):
            d.ellipse(P([(Q(s, 8.5)[0] - 1.3, Q(s, 8.5)[1] - 1.3), (Q(s, 8.5)[0] + 1.3, Q(s, 8.5)[1] + 1.3)]), fill=(35, 35, 42, 255))
            if not ruined: g.ellipse(P([(Q(s, 8.5)[0] - 2, Q(s, 8.5)[1] - 2), (Q(s, 8.5)[0] + 2, Q(s, 8.5)[1] + 2)]), fill=(255, 120, 60, 110))
    m, (ux, uy), (nx, ny) = edge_frame((e0 + 1) % 6 if seed % 2 else (e0 + 4) % 6)
    x, y = m[0] + nx * 8, m[1] + ny * 8
    d.line(P([(x, y), (x - nx * 3, y - ny * 3)]), fill=_lit(FRAME, .7), width=SS)
    if not (ruined and r.random() < .5):
        d.ellipse(P([(x - 3.5, y - 2.5), (x + 3.5, y + 2.5)]), fill=_lit(FRAME, 1.0)); d.ellipse(P([(x - 2, y - 1.5), (x + 1, y + .5)]), fill=_lit(FRAME, .6))
    return finish(im, G)

def shield(ruined, seed):
    r = random.Random(seed); edges = []
    for e in range(6):
        rb = r.random() if ruined else 1
        if rb > 0.2: edges.append((0, 0, e, rb < 0.65))
    return shield_layer((S, S), edges, [] if ruined else [(0, 0)])

if __name__ == '__main__':
    import sys
    sys.path.insert(0, '.')
    bg = Image.new('RGBA', (72 * 6, 72 * 6), (5, 6, 12, 255)); rb = random.Random(4); db = ImageDraw.Draw(bg)
    for _ in range(260):
        x, y, v = rb.uniform(0, 432), rb.uniform(0, 432), rb.randint(90, 230); db.point((x, y), fill=(v, v, min(255, v + 15), 255))
    unit = Image.open('/mnt/project-files/sprites/roster/fed-miranda.png').convert('RGBA')
    hexmask = Image.new('L', (S, S)); ImageDraw.Draw(hexmask).polygon(HEXV, fill=255)
    designs = [('A  Corner turrets', corner_turrets), ('B  Battlements', battlements), ('C  Emitter pylons', pylons), ('D  Bunkers', bunkers)]
    cols = [('intact', False, False), ('intact + ship', False, True), ('ruined', True, False), ('ruined + ship', True, True)]
    Z = 3; cw, ch = S * Z + 24, S * Z + 24
    f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 20); fs = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 16)
    out = Image.new('RGB', (230 + cw * 4 + 40 + 72 * 4 + 60, 50 + ch * 4), (20, 20, 24)); d = ImageDraw.Draw(out)
    for j, (cl, _, _) in enumerate(cols): d.text((230 + j * cw + 12, 14), cl, fill=(200, 200, 200), font=fs)
    d.text((230 + cw * 4 + 40, 14), 'game scale', fill=(200, 200, 200), font=fs)
    for i, (name, fn) in enumerate(designs):
        y0 = 50 + i * ch; d.text((14, y0 + ch // 2 - 12), name, fill=(235, 235, 235), font=f)
        for j, (cl, ru, sh) in enumerate(cols):
            tile = Image.new('RGBA', (S, S)); tile.paste(bg.crop((72 * j % 360, 72 * i, 72 * j % 360 + S, 72 * i + S)), (0, 0))
            tile.alpha_composite(fn(i + j, ru)); tile.alpha_composite(shield(ru, i * 7 + j))
            if sh: tile.alpha_composite(unit)
            frame = Image.new('RGBA', (S + 8, S + 8), (10, 11, 16, 255)); frame.paste(bg.crop((0, 0, S + 8, S + 8)), (0, 0)); frame.paste(tile, (4, 4), hexmask)
            big = frame.resize(((S + 8) * Z, (S + 8) * Z), Image.LANCZOS).crop((0, 0, cw - 12, ch - 12))
            out.paste(big.convert('RGB'), (230 + j * cw, y0))
            small = frame.convert('RGB'); out.paste(small, (230 + cw * 4 + 40 + j * 72 - 4, y0 + ch // 2 - 40))
    out.save('/mnt/project-files/tileset/lone-castle-prototypes.png'); print(out.size)
