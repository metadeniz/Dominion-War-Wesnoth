# python3 -I ringcmp.py ROSTER SHADOWDIR NOSHADOWDIR OUT id1,id2,...   (288px renders, {id}.png in each dir)
# Ships at 72px (shown 2x) over a team-colour ring like Wesnoth's unit ellipse, drawn here (not the game's own image).
# Wesnoth draws the back half of the ring under the unit and the front half over it.
import sys, json, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sprite72 import make72
R = json.load(open(sys.argv[1])); SD, ND, OUT, ids = sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5].split(',')
U = {u['id']: u for f in R for u in f['units']}
rng = np.random.default_rng(7)
HEX = [(18, 0), (54, 0), (72, 36), (54, 72), (18, 72), (0, 36)]
def hexmask():
    m = Image.new('L', (72, 72), 0); ImageDraw.Draw(m).polygon(HEX, fill=255); return m
def starfield():
    a = np.zeros((72, 72, 3), np.float32) + np.array([7, 9, 18], np.float32)
    for _ in range(26):
        y, x = rng.integers(0, 72, 2); a[y, x] = rng.uniform(90, 230)
    return a
def nebula():
    n = np.zeros((72, 72), np.float32)
    for s, w in ((6, 1), (12, .5), (24, .25)):
        g = rng.random((s, s)).astype(np.float32); n += w * np.asarray(Image.fromarray((g * 255).astype(np.uint8)).resize((72, 72), Image.BICUBIC), np.float32) / 255
    n = (n - n.min()) / (n.max() - n.min())
    a = np.array([30, 18, 60]) * (1 - n[..., None]) + np.array([150, 70, 150]) * n[..., None]
    a = a * (1 - (n[..., None] ** 3) * .5) + np.array([80, 120, 200]) * (n[..., None] ** 3) * .5
    for _ in range(10):
        y, x = rng.integers(0, 72, 2); a[y, x] = 220
    return a.astype(np.float32)
def tile(bg):
    t = Image.fromarray(np.clip(bg, 0, 255).astype(np.uint8)).convert('RGBA'); base = Image.new('RGBA', (72, 72), (40, 40, 48, 255))
    base.paste(t, (0, 0), hexmask()); ImageDraw.Draw(base).polygon([(18, 0), (54, 0), (71, 36), (54, 71), (18, 71), (0, 36)], outline=(0, 0, 0, 90)); return base
CX, CY, RX, RY = 36, 50, 24, 10
def ring(col, part):
    S = 8; im = Image.new('RGBA', (72 * S, 72 * S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    box = lambda r: ((CX - RX - r) * S, (CY - RY - r) * S, (CX + RX + r) * S, (CY + RY + r) * S)
    dark = tuple(int(c * .45) for c in col)
    d.ellipse(box(1.6), outline=dark + (255,), width=int(3.2 * S)); d.ellipse(box(1.0), outline=col + (255,), width=int(2.0 * S))
    im = im.resize((72, 72), Image.LANCZOS)
    if part != 'all':
        m = Image.new('L', (72, 72), 0); ImageDraw.Draw(m).rectangle((0, 0, 72, CY) if part == 'top' else (0, CY, 72, 72), fill=255)
        a = Image.composite(im, Image.new('RGBA', (72, 72), (0, 0, 0, 0)), m); im = a
    return im
TEAMS = [('Red team, starfield', (255, 0, 0), tile(starfield())), ('Blue team, nebula', (46, 65, 155), tile(nebula()))]
VAR = [('No shadow, ring', 'none', 'split'), ('Shadow, ring', 'shadow', 'split'), ('Shadow, whole ring under the ship', 'shadow', 'all')]
F = lambda s, b=False: ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf' % ('-Bold' if b else ''), s)
S2 = 2; C = 72 * S2; G = 8; LW = 150; TOP = 78
W = LW + len(VAR) * (len(TEAMS) * (C + G) + G); H = TOP + len(ids) * (C + G) + G
sh = Image.new('RGBA', (W, H), (26, 26, 32, 255)); d = ImageDraw.Draw(sh)
d.text((10, 8), "Team rings drawn to match Wesnoth's unit ellipse (not the game's own image). Wesnoth draws the back half of the ring under the ship and the front half over it.", font=F(12), fill=(225, 225, 230))
def wrap(t, w, f):
    out = ['']
    for x in t.split():
        if d.textlength((out[-1] + ' ' + x).strip(), font=f) > w: out.append(x)
        else: out[-1] = (out[-1] + ' ' + x).strip()
    return out
for vi, (vn, _, _) in enumerate(VAR):
    x0 = LW + vi * (len(TEAMS) * (C + G) + G); d.text((x0, 30), vn, font=F(15, True), fill=(240, 210, 120))
    for ti, (tn, _, _) in enumerate(TEAMS): d.text((x0 + ti * (C + G), 54), tn, font=F(11), fill=(170, 170, 180))
for ri, i in enumerate(ids):
    u = U[i]; y = TOP + ri * (C + G)
    for j, t in enumerate(wrap(u['name'].replace(' (leader)', ''), LW - 16, F(13, True))): d.text((10, y + C // 2 - 10 + 17 * j), t, font=F(13, True), fill=(225, 225, 230))
    spr = {'shadow': make72(Image.open(os.path.join(SD, i + '.png')), bool(u.get('pop')), 6), 'none': make72(Image.open(os.path.join(ND, i + '.png')), bool(u.get('pop')), 6)}
    for vi, (_, which, part) in enumerate(VAR):
        x0 = LW + vi * (len(TEAMS) * (C + G) + G)
        for ti, (_, col, t) in enumerate(TEAMS):
            c = t.copy()
            if part == 'split': c.alpha_composite(ring(col, 'top')); c.alpha_composite(spr[which]); c.alpha_composite(ring(col, 'bottom'))
            else: c.alpha_composite(ring(col, 'all')); c.alpha_composite(spr[which])
            sh.alpha_composite(c.resize((C, C), Image.NEAREST), (x0 + ti * (C + G), y))
sh.convert('RGB').save(OUT); print(OUT, sh.size)
