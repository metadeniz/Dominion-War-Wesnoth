# python3 -I shadowcmp.py ROSTER DIR OUT id1,id2,...   DIR/{id}/{none,above}.png are 288px renders (rigtest.js)
# Draws each ship at 72px (shown 2x, true pixels) with no shadow, shadow from straight above, and a soft dark halo,
# on a starfield hex and a nebula hex.
import sys, json, os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sprite72 import make72
R = json.load(open(sys.argv[1])); D = sys.argv[2]; OUT = sys.argv[3]; ids = sys.argv[4].split(',')
U = {u['id']: u for f in R for u in f['units']}
rng = np.random.default_rng(7)
def hexmask():
    m = Image.new('L', (72, 72), 0); ImageDraw.Draw(m).polygon([(18, 0), (54, 0), (72, 36), (54, 72), (18, 72), (0, 36)], fill=255); return m
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
    c1 = np.array([30, 18, 60]); c2 = np.array([150, 70, 150]); c3 = np.array([80, 120, 200])
    a = c1 * (1 - n[..., None]) + c2 * n[..., None]; a = a * (1 - (n[..., None] ** 3) * .5) + c3 * (n[..., None] ** 3) * .5
    for _ in range(10):
        y, x = rng.integers(0, 72, 2); a[y, x] = 220
    return a.astype(np.float32)
def tile(bg):
    t = Image.fromarray(np.clip(bg, 0, 255).astype(np.uint8)).convert('RGBA'); base = Image.new('RGBA', (72, 72), (40, 40, 48, 255))
    base.paste(t, (0, 0), hexmask()); ImageDraw.Draw(base).polygon([(18, 0), (54, 0), (71, 36), (54, 71), (18, 71), (0, 36)], outline=(0, 0, 0, 90)); return base
BG = [('Starfield', tile(starfield())), ('Nebula', tile(nebula()))]
def halo(im):
    a = im.split()[3].filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(5))
    h = Image.new('RGBA', im.size, (0, 0, 0, 0)); h.putalpha(a.point(lambda v: int(v * .6)))
    h.alpha_composite(im); return h
def F(sz, b=False):
    for p in ('/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf' % ('-Bold' if b else ''),):
        if os.path.exists(p): return ImageFont.truetype(p, sz)
    return ImageFont.load_default()
VAR = ['No shadow', 'Shadow from above', 'Soft dark halo']
S = 2; C = 72 * S; G = 8; LW = 170; TOP = 64
W = LW + len(VAR) * len(BG) * (C + G) + 2 * G; H = TOP + len(ids) * (C + G) + G
sheet = Image.new('RGBA', (W, H), (26, 26, 32, 255)); d = ImageDraw.Draw(sheet)
for vi, v in enumerate(VAR):
    x0 = LW + vi * len(BG) * (C + G) + vi * G
    d.text((x0, 10), v, font=F(16, True), fill=(235, 235, 240))
    for bi, (bn, _) in enumerate(BG): d.text((x0 + bi * (C + G), 36), bn, font=F(12), fill=(170, 170, 180))
for ri, i in enumerate(ids):
    u = U[i]; y = TOP + ri * (C + G); nm = u['name'].replace(' (leader)', '').split(); ln = ['']
    for w in nm:
        if d.textlength((ln[-1] + ' ' + w).strip(), font=F(13, True)) > LW - 18: ln.append(w)
        else: ln[-1] = (ln[-1] + ' ' + w).strip()
    for k, t in enumerate(ln): d.text((10, y + C // 2 - 9 * len(ln) + 18 * k), t, font=F(13, True), fill=(225, 225, 230))
    none = Image.open(os.path.join(D, i, 'none.png')).convert('RGBA'); above = Image.open(os.path.join(D, i, 'above.png')).convert('RGBA')
    for vi, im in enumerate([none, above, halo(none)]):
        s72 = make72(im, bool(u.get('pop')), 6)
        x0 = LW + vi * len(BG) * (C + G) + vi * G
        for bi, (_, t) in enumerate(BG):
            c = t.copy(); c.alpha_composite(s72); sheet.alpha_composite(c.resize((C, C), Image.NEAREST), (x0 + bi * (C + G), y))
sheet.convert('RGB').save(OUT); print(OUT, sheet.size)
