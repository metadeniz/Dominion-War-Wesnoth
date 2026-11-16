# python3 -I oldsheet.py ROSTER ROSTER_DIR OUT -> contact sheet of every retired sprite in ROSTER_DIR/old, one row per ship (current sprite first)
import sys, os, json
from PIL import Image, ImageDraw, ImageFont
ROS, RD, OUT = sys.argv[1:4]; OLD = os.path.join(RD, 'old')
F = lambda s, b=False: ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf' % ('-Bold' if b else ''), s)
units = [(u['id'], u['name']) for f in json.load(open(ROS)) for u in f['units']]
files = sorted(f for f in os.listdir(OLD) if f.endswith('.png'))
rows = []; used = set()
for uid, name in units:
    mine = [f for f in files if f == uid + '.png' or f.startswith(uid + '-')]
    used.update(mine)
    if mine: rows.append((name, [('now (sheet v42)', os.path.join(RD, uid + '.png'))] + [(f[len(uid):].strip('-.').replace('.png', '') or '(no label)', os.path.join(OLD, f)) for f in mine]))
rest = [f for f in files if f not in used]
if rest: rows.append(('Ships no longer on the roster', [(f[:-4], os.path.join(OLD, f)) for f in rest]))
pre = os.path.join(OLD, 'prescale')
if os.path.isdir(pre): rows.append(('old/prescale (before the size change)', [(f[:-4], os.path.join(pre, f)) for f in sorted(os.listdir(pre)) if f.endswith('.png')]))
CW, CH, PER, LW = 168, 186, 7, 210
H = 70 + sum(((len(c) + PER - 1) // PER) * CH + 34 for _, c in rows); W = LW + PER * CW + 20
im = Image.new('RGB', (W, H), (16, 18, 30)); d = ImageDraw.Draw(im)
d.text((14, 12), 'Retired sprites in sprites/roster/old (%d files), shown at 2x' % (sum(len(c) for _, c in rows) - sum(1 for n, c in rows if c[0][0].startswith('now'))), font=F(20, True), fill=(235, 235, 240))
d.text((14, 40), 'First in each ship row: the sprite on sheet v42 now, for comparison. Labels are the file name after the ship id.', font=F(13), fill=(170, 170, 185))
y = 70
for name, cells in rows:
    import textwrap
    for li, line in enumerate(textwrap.wrap(name, 22)): d.text((14, y + 6 + li * 18), line, font=F(14, True), fill=(240, 210, 120))
    for k, (lab, p) in enumerate(cells):
        x = LW + (k % PER) * CW; yy = y + (k // PER) * CH
        s = Image.open(p).convert('RGBA'); n = min(s.size[0] * 2, 152); s = s.resize((n, n), Image.NEAREST)
        bg = Image.new('RGBA', (152, 152), (26, 30, 48, 255) if k or not lab.startswith('now') else (48, 42, 24, 255)); bg.alpha_composite(s, ((152 - n) // 2, (152 - n) // 2))
        im.paste(bg.convert('RGB'), (x, yy)); d.text((x + 2, yy + 156), lab[:24], font=F(11), fill=(200, 200, 210))
    y += ((len(cells) + PER - 1) // PER) * CH + 34
im.save(OUT); print(OUT, im.size, len(rows), 'rows')
