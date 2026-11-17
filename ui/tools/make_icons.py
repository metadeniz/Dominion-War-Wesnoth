# The Dominion War's resource icons (16x16): dilithium in place of Wesnoth's gold, and a planet for villages.
# Run from ui/tools: python3 make_icons.py. Writes ../images/themes/. income.png and upkeep.png here are
# Wesnoth's own icons; only their plus and minus signs are reused.
import math, sys
from PIL import Image, ImageDraw, ImageFilter
K = 4; N = 16 * K
HERE = __import__('os').path.dirname(__import__('os').path.abspath(__file__))
OUT = HERE + '/../images/themes/'
import os; os.makedirs(OUT, exist_ok=True)

def finish(big):
    # dark outline like Wesnoth's icons, then reduce
    a = big.split()[3]
    ol = a.filter(ImageFilter.MaxFilter(5))
    base = Image.new('RGBA', big.size, (20, 14, 10, 0)); base.putalpha(ol.point(lambda v: 230 if v > 60 else 0))
    base.alpha_composite(big)
    return base.resize((16, 16), Image.LANCZOS)

def poly(d, pts, fill): d.polygon([(x * K, y * K) for x, y in pts], fill=fill)

def crystal(d, cx, base, top, w, lean, cols):
    # an elongated hexagonal prism: left face, right face, tip
    dark, mid, light = cols
    tx = cx + lean
    poly(d, [(cx - w, base), (cx, base + 1), (tx, top + 2.5), (tx - w, top + 3)], mid)
    poly(d, [(cx, base + 1), (cx + w, base), (tx + w, top + 3), (tx, top + 2.5)], dark)
    poly(d, [(tx - w, top + 3), (tx, top + 2.5), (tx + w, top + 3), (tx + 0.2, top)], light)
    poly(d, [(cx - w + 0.6, base - 0.5), (cx - w + 1.4, base - 0.3), (tx - w + 1.3, top + 3.4), (tx - w + 0.6, top + 3.4)], light)

def dilithium():
    im = Image.new('RGBA', (N, N)); d = ImageDraw.Draw(im)
    P = ((120, 30, 120), (200, 70, 190), (255, 190, 245))
    crystal(d, 4.6, 14.2, 4.5, 1.9, -1.6, P)
    crystal(d, 11.4, 14.2, 5.5, 1.8, 1.8, P)
    crystal(d, 8.0, 14.8, 1.0, 2.3, 0.0, ((140, 40, 140), (225, 95, 215), (255, 220, 250)))
    g = im.filter(ImageFilter.GaussianBlur(6)); glow = Image.new('RGBA', im.size, (255, 120, 240, 0)); glow.putalpha(g.split()[3].point(lambda v: v // 3))
    glow.alpha_composite(im)
    return finish(glow)

def latinum():
    im = Image.new('RGBA', (N, N)); d = ImageDraw.Draw(im)
    def bar(x, y, w, h):
        poly(d, [(x, y + h), (x + w, y + h), (x + w - 1, y), (x + 1, y)], (190, 140, 40))          # front
        poly(d, [(x + 1, y), (x + w - 1, y), (x + w - 2.2, y - 1.6), (x + 2.2, y - 1.6)], (250, 215, 110))  # top
        d.line([((x + 2) * K, (y + h / 2) * K), ((x + w - 2) * K, (y + h / 2) * K)], fill=(140, 95, 20), width=K)   # stamp
    bar(1, 12, 9, 3); bar(6.5, 12, 9, 3); bar(3.8, 8.2, 9, 3)
    # the latinum itself: a silver liquid gleam
    poly(d, [(6.4, 5.4), (8.2, 2.2), (10, 5.4), (8.2, 7.4)], (200, 230, 255))
    return finish(im)

def energy():
    im = Image.new('RGBA', (N, N)); d = ImageDraw.Draw(im)
    d.ellipse([1.5 * K, 1.5 * K, 14.5 * K, 14.5 * K], fill=(25, 60, 120))
    d.ellipse([2.6 * K, 2.6 * K, 13.4 * K, 13.4 * K], fill=(40, 110, 200))
    g = Image.new('RGBA', (N, N)); gd = ImageDraw.Draw(g)
    poly(gd, [(9.4, 2.4), (4.4, 9), (7.6, 9), (6.4, 13.6), (11.6, 6.6), (8.4, 6.6)], (255, 250, 200))
    halo = g.filter(ImageFilter.GaussianBlur(5)); hl = Image.new('RGBA', g.size, (140, 220, 255, 0)); hl.putalpha(halo.split()[3])
    im.alpha_composite(hl); im.alpha_composite(g)
    return finish(im)

def antimatter():
    # an antimatter pod: a capsule with a glowing blue core
    im = Image.new('RGBA', (N, N)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([4 * K, 1.2 * K, 12 * K, 14.8 * K], radius=3.6 * K, fill=(90, 96, 110))
    d.rounded_rectangle([4.8 * K, 2 * K, 11.2 * K, 14 * K], radius=3 * K, fill=(150, 158, 172))
    d.rectangle([5.6 * K, 4.4 * K, 10.4 * K, 11.6 * K], fill=(30, 90, 200))
    g = Image.new('RGBA', (N, N)); gd = ImageDraw.Draw(g); gd.ellipse([6.2 * K, 5.4 * K, 9.8 * K, 10.6 * K], fill=(190, 240, 255))
    halo = g.filter(ImageFilter.GaussianBlur(4)); im.alpha_composite(halo); im.alpha_composite(g)
    d = ImageDraw.Draw(im)
    for y in (4.2, 11.6): d.rectangle([4.4 * K, y * K, 11.6 * K, (y + 0.7) * K], fill=(60, 64, 76))
    return finish(im)

def planet():
    src = Image.open(HERE + '/../../terrain/images/terrain/dw/planet-M-1.png').convert('RGBA')
    from PIL import ImageEnhance; src = ImageEnhance.Brightness(src).enhance(1.35)
    bb = src.getbbox(); src = src.crop(bb)
    s = max(src.size); sq = Image.new('RGBA', (s, s)); sq.paste(src, ((s - src.size[0]) // 2, (s - src.size[1]) // 2))
    return sq.resize((15, 15), Image.LANCZOS), sq

# income / upkeep: the new icon with Wesnoth's own plus and minus over it
def with_sign(icon, orig):
    o = Image.open(orig).convert('RGBA'); out = Image.new('RGBA', o.size); out.alpha_composite(icon, (0, 0))
    for y in range(o.size[1]):
        for x in range(11, o.size[0]):
            p = o.getpixel((x, y))
            if p[3] < 128: continue
            r, g, b = p[:3]
            coin = (r > b + 40 and g > b + 10 and not (g > r + 30))
            if not coin: out.putpixel((x, y), p)
    return out

def bw(path):
    im = Image.open(path).convert('RGBA'); a = im.split()[3]
    g = im.convert('L').point(lambda v: int(60 + v * 0.55)); out = Image.merge('RGBA', (g, g, g, a))
    out.save(path.replace('.png', '-bw.png'))

if __name__ == '__main__':
    ic = dilithium(); ic.save(OUT + 'gold.png')
    with_sign(ic, HERE + '/income.png').save(OUT + 'income.png')
    with_sign(ic, HERE + '/upkeep.png').save(OUT + 'upkeep.png')
    p, _ = planet(); v = Image.new('RGBA', (16, 16)); v.alpha_composite(p, (0, 1)); v.save(OUT + 'villages.png')
    for n in ('gold', 'income', 'upkeep', 'villages'): bw(OUT + n + '.png')
