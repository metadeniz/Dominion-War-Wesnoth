# python3 -I tonecmp.py DIR OUT POP label1=id1 label2=id2 ...   DIR/{id}.png are 288px renders
import sys, os
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sprite72 import make72
D, OUT, POP = sys.argv[1], sys.argv[2], sys.argv[3] == '1'; items = [a.split('=', 1) for a in sys.argv[4:]]
F = lambda s, b=False: ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf' % ('-Bold' if b else ''), s)
CW = 288; COLS = 4; rows = (len(items) + COLS - 1) // COLS; TH = 40; CH = TH + 288 + 160
W = COLS * CW; H = 50 + rows * CH
sh = Image.new('RGBA', (W, H), (30, 30, 36, 255)); d = ImageDraw.Draw(sh)
d.text((10, 14), 'Excelsior hull blue: tone options. Engine glow (nacelle strips) is the same in all. 288px render, then the 72px sprite at 2x.', font=F(13), fill=(225, 225, 230))
lum = lambda im: sum(p for p, a in zip(im.convert('L').getdata(), im.split()[3].getdata()) if a > 230) / max(1, sum(1 for a in im.split()[3].getdata() if a > 230))
for k, (lab, i) in enumerate(items):
    x = (k % COLS) * CW; y = 50 + (k // COLS) * CH; im = Image.open(os.path.join(D, i + '.png')).convert('RGBA')
    d.text((x + 10, y + 8), lab, font=F(14, True), fill=(240, 210, 120) if k else (235, 235, 240))
    sh.alpha_composite(im, (x, y + TH)); s = make72(im, POP, 6); sh.alpha_composite(s.resize((144, 144), Image.NEAREST), (x + 20, y + TH + 288 + 8))
    d.text((x + 180, y + TH + 288 + 70), f'lum {lum(s):.0f}', font=F(12), fill=(170, 170, 180))
sh.convert('RGB').save(OUT); print(OUT, sh.size)
