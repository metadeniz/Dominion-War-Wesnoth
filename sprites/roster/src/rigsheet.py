# python3 -I rigsheet.py ROSTER RIGS.json DIR OUT id1,id2,...   DIR/{id}/{rigid}.png are 288px renders (rigtest.js)
# Rows = ships, columns = rigs. Each cell: the render at 0.75x, then the 72px sprite at 2x with its brightness and contrast.
import sys, json, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sprite72 import make72
R = json.load(open(sys.argv[1])); RIGS = json.load(open(sys.argv[2])); D = sys.argv[3]; OUT = sys.argv[4]; ids = sys.argv[5].split(',')
U = {u['id']: u for f in R for u in f['units']}
F = lambda s, b=False: ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf' % ('-Bold' if b else ''), s)
LW, CW, TOP = 130, 216, 96
RH = lambda uid: 216 + 2 * U[uid].get('canvas', 72) + 6   # a 96px sprite (bigger canvas) gets a taller row
YS = [TOP]
for uid in ids: YS.append(YS[-1] + RH(uid))
W = LW + len(RIGS) * CW; H = YS[-1]
sh = Image.new('RGBA', (W, H), (30, 30, 36, 255)); d = ImageDraw.Draw(sh)
d.text((10, 10), os.environ.get("HDR_FULL") or os.environ.get("HDR", "Light rigs on 2 ships per faction.") + " 'Now' = today's lighting and shadow; the rigs use the shadow from straight above. lum = sprite brightness, con = contrast (raider picks: lum 73-79, con 25-28).", font=F(12), fill=(225, 225, 230))
def wrap(t, w, f):
    out = ['']
    for x in t.split():
        if d.textlength((out[-1] + ' ' + x).strip(), font=f) > w: out.append(x)
        else: out[-1] = (out[-1] + ' ' + x).strip()
    return out
for k, r in enumerate(RIGS):
    x = LW + k * CW; num = r['id'].replace('rig', '').lstrip('0') if r['id'] != 'now' else 'Now'
    d.text((x + 6, 36), num, font=F(16, True), fill=(240, 210, 120))
    lab = r['label'].replace(' (your pick)', '') if r['id'] != 'now' else 'default light, usual shadow'
    for j, t in enumerate(wrap(lab, CW - 12, F(11))[:3]): d.text((x + 6, 58 + 13 * j), t, font=F(11), fill=(180, 180, 190))
for i, uid in enumerate(ids):
    u = U[uid]; y = YS[i]; n2 = 2 * u.get('canvas', 72)
    for j, t in enumerate(wrap(u.get('label', u['name'].replace(' (leader)', '')), LW - 16, F(13, True))): d.text((10, y + 90 + 17 * j), t, font=F(13, True), fill=(230, 230, 235))
    d.line((0, y, W, y), fill=(50, 50, 58))
    for k, r in enumerate(RIGS):
        x = LW + k * CW; im = Image.open(os.path.join(D, uid, r['id'] + '.png')).convert('RGBA')
        sh.alpha_composite(im.resize((216, 216), Image.LANCZOS), (x, y))
        s = make72(im, bool(u.get('pop')), 6); sh.alpha_composite(s.resize((n2, n2), Image.NEAREST), (x, y + 210))
        a = np.asarray(s).astype(np.float32); m = a[..., 3] > 230; L = (0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2])[m]
        tx = min(x + n2 + 4, x + CW - 46); d.text((tx, y + 210 + n2 - 34), f'lum {L.mean():.0f}', font=F(11), fill=(170, 170, 180)); d.text((tx, y + 210 + n2 - 20), f'con {L.std():.0f}', font=F(11), fill=(170, 170, 180))
sh.convert('RGB').save(OUT); print(OUT, sh.size)
