# python3 -I mixsheet.py OUT.png SCALE ids|all "LABEL=MIXJSON" ...   -> ships (rows) x light mixes (columns), 72px sprites composited from passes
# MIXJSON: {"K1":3.4,"O":0.5,...} or {"@ship-id": {...}, "*": {...}} for per-ship mixes. Env BG=dark|mid, HDR=title, COLS=n (wrap ships)
import sys, os, json, numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lightlab import sprite, metrics, U
OUT, SC = sys.argv[1], int(sys.argv[2]); ids = list(U) if sys.argv[3] == 'all' else sys.argv[3].split(',')
cols = [(a.split('=', 1)[0], json.loads(a.split('=', 1)[1])) for a in sys.argv[4:]]
def mixfor(m, uid):
    if '*' in m or any(k.startswith('@') for k in m): return m.get('@' + uid, m.get('*'))
    return m
try: F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 13); FB = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 15)
except Exception: F = FB = ImageFont.load_default()
bg = (14, 16, 28) if os.environ.get('BG', 'dark') == 'dark' else (70, 60, 90)
cw = 72 * SC + 12; lw = 150; hh = 46 if os.environ.get('HDR') else 24; rh = 72 * SC + 20
W = lw + cw * len(cols); H = hh + rh * len(ids)
im = Image.new('RGB', (W, H), bg); d = ImageDraw.Draw(im)
if os.environ.get('HDR'): d.text((8, 6), os.environ['HDR'], fill=(235, 235, 235), font=FB)
for j, (lab, m) in enumerate(cols): d.text((lw + j * cw + 6, hh - 20), lab, fill=(220, 220, 160), font=F)
for i, uid in enumerate(ids):
    y = hh + i * rh; d.text((6, y + rh // 2 - 8), U[uid].get('name', uid)[:20], fill=(210, 210, 210), font=F)
    for j, (lab, m) in enumerate(cols):
        mx = mixfor(m, uid); s = sprite(uid, mx); me = metrics(uid, img=s)
        big = s.resize((72 * SC, 72 * SC), Image.NEAREST); im.paste(big, (lw + j * cw, y), big)
        d.text((lw + j * cw + 4, y + 72 * SC + 2), 'lum %.0f  con %.0f' % (me['lum'], me['std']), fill=(150, 150, 170), font=F)
im.save(OUT); print(OUT, im.size)
