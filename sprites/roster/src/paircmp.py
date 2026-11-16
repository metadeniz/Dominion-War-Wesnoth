# python3 -I paircmp.py ROSTER DIR_A DIR_B LABEL_A LABEL_B OUT   (DIR_*/{id}.png are hires.js renders at 288 x canvas/72)
# Whole roster, faction by faction: each ship's render under A and B (scaled to 160px), then its game sprite under each at 2x.
import sys, json, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sprite72 import make72
R = json.load(open(sys.argv[1])); A, B, LA, LB, OUT = sys.argv[2:7]
F = lambda s, b=False: ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf' % ('-Bold' if b else ''), s)
HI = 160; PW = 2 * HI + 14; COLS = 4; G = 18; NAMEH = 22; RH = NAMEH + HI + 148 + 26
def lum(s):
    a = np.asarray(s).astype(np.float32); m = a[..., 3] > 230; return (0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2])[m].mean()
rows = sum((len(f['units']) + COLS - 1) // COLS for f in R)
W = 20 + COLS * (PW + G); H = 70 + len(R) * 40 + rows * RH
sh = Image.new('RGBA', (W, H), (28, 28, 34, 255)); d = ImageDraw.Draw(sh)
d.text((14, 12), f'Whole roster: {LA} (left of each pair) vs {LB} (right). Shadow from straight above in both. Top: render; below: the game sprite at 2x with its brightness.', font=F(13), fill=(225, 225, 230))
y = 46
for f in R:
    d.text((14, y), f['faction'], font=F(18, True), fill=(240, 210, 120)); y += 34
    for k, u in enumerate(f['units']):
        x = 14 + (k % COLS) * (PW + G); yy = y + (k // COLS) * RH
        d.text((x, yy), u['name'], font=F(12, True), fill=(230, 230, 235))
        for j, (D, L) in enumerate(((A, LA), (B, LB))):
            im = Image.open(os.path.join(D, u['id'] + '.png')).convert('RGBA')
            sh.alpha_composite(im.resize((HI, HI), Image.LANCZOS), (x + j * (HI + 14), yy + NAMEH))
            s = make72(im, bool(u.get('pop')), 6); n2 = min(2 * s.size[0], HI)
            sh.alpha_composite(s.resize((n2, n2), Image.NEAREST), (x + j * (HI + 14), yy + NAMEH + HI))
            d.text((x + j * (HI + 14) + 4, yy + NAMEH + HI + n2 + 2), f'{L}  lum {lum(s):.0f}', font=F(11), fill=(170, 170, 180))
    y += ((len(f['units']) + COLS - 1) // COLS) * RH + 6
sh = sh.crop((0, 0, W, y)); sh.convert('RGB').save(OUT); print(OUT, sh.size)
