# python3 -I multicmp.py ROSTER OUT "LABEL=DIR" "LABEL=DIR" ...   (DIR/{id}.png are hires.js renders at 288 x canvas/72)
# Whole roster, faction by faction: for each ship, its render (scaled) under each setup, then the game sprite at 2x with its brightness.
import sys, json, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sprite72 import make72
R = json.load(open(sys.argv[1])); OUT = sys.argv[2]; SETS = [a.split('=', 1) for a in sys.argv[3:]]
F = lambda s, b=False: ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf' % ('-Bold' if b else ''), s)
HI = 144; GAP = 8; SW = len(SETS) * HI + (len(SETS) - 1) * GAP; COLS = int(os.environ.get('COLS', 3)); G = 26; NAMEH = 22; RH = NAMEH + HI + 144 + 22
def lum(s):
    a = np.asarray(s).astype(np.float32); m = a[..., 3] > 230; return (0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2])[m].mean()
rows = sum((len(f['units']) + COLS - 1) // COLS for f in R)
W = 28 + COLS * (SW + G); H = 90 + len(R) * 40 + rows * RH
sh = Image.new('RGBA', (W, H), (28, 28, 34, 255)); d = ImageDraw.Draw(sh)
d.text((14, 12), 'Whole roster, left to right in each group: ' + '  |  '.join(f'{i + 1} = {l}' for i, (l, _) in enumerate(SETS)), font=F(13, True), fill=(225, 225, 230))
d.text((14, 32), os.environ.get('NOTE', 'Shadow from straight above in all. Top: render; below: the game sprite at 2x with its brightness (your picks: 75-85).'), font=F(12), fill=(180, 180, 190))
y = 60
for f in R:
    d.text((14, y), f['faction'], font=F(18, True), fill=(240, 210, 120)); y += 34
    for k, u in enumerate(f['units']):
        x = 14 + (k % COLS) * (SW + G); yy = y + (k // COLS) * RH
        d.text((x, yy), u['name'], font=F(12, True), fill=(230, 230, 235))
        for j, (L, D) in enumerate(SETS):
            xx = x + j * (HI + GAP); im = Image.open(os.path.join(D, u['id'] + '.png')).convert('RGBA')
            sh.alpha_composite(im.resize((HI, HI), Image.LANCZOS), (xx, yy + NAMEH))
            s = make72(im, bool(u.get('pop')), 6); n2 = min(2 * s.size[0], HI)
            sh.alpha_composite(s.resize((n2, n2), Image.NEAREST), (xx, yy + NAMEH + HI))
            d.text((xx + 2, yy + NAMEH + HI + n2 + 2), f'{j + 1}  lum {lum(s):.0f}', font=F(11), fill=(170, 170, 180))
    y += ((len(f['units']) + COLS - 1) // COLS) * RH + 6
sh = sh.crop((0, 0, W, y)); sh.convert('RGB').save(OUT); print(OUT, sh.size)
