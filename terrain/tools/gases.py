# The gas families of the space terrain, as wrapping textures (see gaslib.py).
# Each recipe follows the mockup renderers (badlands.py, impassable.py, mock.py), made periodic.
import math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from gaslib import TW, TH, pfbm, pflow, psmear, ramp, rgba, wrap_blur

FIRE = [(0.0, (40, 4, 10)), (0.35, (130, 20, 30)), (0.6, (215, 70, 40)), (0.82, (255, 150, 70)), (1.0, (255, 235, 180))]
DEEPFIRE = [(0.0, (20, 2, 10)), (0.35, (70, 6, 26)), (0.6, (125, 22, 36)), (0.82, (190, 70, 50)), (1.0, (240, 160, 120))]
NEB = ((10, 50, 25), (35, 140, 70), (170, 255, 190))       # every forest is a green nebula (D)
ANOM = ((8, 2, 16), (70, 25, 115), (180, 120, 240))        # dark matter nebula: purple (D)
DUST = ((40, 30, 20), (110, 85, 55), (200, 170, 120))
ICE = ((18, 28, 44), (90, 130, 170), (225, 240, 255))
CORONA = ((90, 40, 0), (240, 140, 20), (255, 245, 180))

def badlands(seed, kind):
    """kind: shallow, deep or swamp. Star Control's wispy currents in our reds (D: picked 'currents')."""
    rng = np.random.default_rng(seed)
    vx, vy = pflow(rng, swirl=0.6)
    body = pfbm(5, 6, 4, rng)
    strands = psmear(pfbm(54, 72, 2, rng), vx, vy, 30)
    patch = pfbm(7, 10, 3, rng)
    bodyd = psmear(body, vx, vy, 20, 2.0)
    glint = np.clip((strands - 1.0) / 1.4, 0, 1) ** 1.5
    t = 0.36 + 0.10 * bodyd + 0.05 * strands + 0.30 * glint
    if kind == 'deep':     # denser and darker, fewer glints
        a = np.clip(0.42 + 0.16 * bodyd + 0.07 * strands + 0.48, 0, 0.95)
        rgb = ramp(t - 0.22 * glint + 0.04 * strands, DEEPFIRE)
    else:
        a = np.clip(0.42 + 0.16 * bodyd + 0.07 * strands, 0, 0.95)
        rgb = ramp(t, FIRE)
    if kind == 'swamp':    # lighter and patchier, so swamp is still told apart
        a = a * (1 - np.clip(0.55 - 0.45 * patch, 0, 1)) * 0.85
    return rgba(rgb, a)

def nebula(seed, palette, dens=1.0, dark=False, floor=0.18):
    rng = np.random.default_rng(seed)
    vx, vy = pflow(rng, drift=(0.3, -0.2), swirl=0.9)
    body = psmear(pfbm(6, 8, 5, rng), vx, vy, 8, 2.0)
    wisp = psmear(pfbm(36, 48, 2, rng), vx, vy, 14, 1.5)
    c = np.clip(0.5 + 0.28 * body + 0.12 * wisp, 0, 1)
    a = np.clip((c - floor) * 1.25, 0, 0.85) * dens
    t = np.clip(c * 0.9 + 0.15 * np.clip(wisp - 0.8, 0, 2), 0, 1)
    rgb = ramp(t, [(0.0, palette[0]), (0.55, palette[1]), (1.0, palette[2])])
    if dark:   # dark matter swallows the stars behind it: a dark veil, lit faintly violet in its folds
        rgb = rgb * (0.45 + 0.6 * np.clip(wisp - 0.3, 0, 1))[..., None]
        a = np.clip(a * 1.25 + 0.1, 0, 0.92)
    return rgba(rgb, a)

def ice(seed):
    out = nebula(seed, ICE, 0.65).astype(np.float32)
    r = random.Random(seed); im = Image.new('RGBA', (TW * 3, TH * 3)); d = ImageDraw.Draw(im)
    for _ in range(70):     # comet ice shards: little bright slivers
        x, y = r.uniform(0, TW), r.uniform(0, TH); L = r.uniform(1.5, 4); a = r.uniform(0, 3.14)
        for ox in (0, TW, 2 * TW):
            for oy in (0, TH, 2 * TH):
                d.line([(x + ox - math.cos(a) * L, y + oy - math.sin(a) * L), (x + ox + math.cos(a) * L, y + oy + math.sin(a) * L)], fill=(235, 248, 255, 230), width=1)
    sh = np.asarray(im, np.float32)[TH:2 * TH, TW:2 * TW]
    k = sh[..., 3:4] / 255
    out[..., :3] = out[..., :3] * (1 - k) + sh[..., :3] * k; out[..., 3] = np.maximum(out[..., 3], sh[..., 3] * 0.9)
    return out.astype(np.uint8)

def corona(seed):
    rng = np.random.default_rng(seed)
    vx, vy = pflow(rng, drift=(0.2, -0.6), swirl=1.2)
    body = psmear(pfbm(6, 8, 5, rng), vx, vy, 10, 2.0)
    fil = psmear(pfbm(40, 54, 2, rng), vx, vy, 20, 1.5)
    t = np.clip(0.5 + 0.22 * body + 0.18 * np.clip(fil - 0.5, 0, 2), 0, 1)
    rgb = ramp(t, [(0.0, CORONA[0]), (0.55, CORONA[1]), (1.0, CORONA[2])])
    return rgba(rgb, np.clip(0.72 + 0.18 * body, 0, 0.95))

def radiation(seed):
    """After Star Control's radiation zone: a glowing cloud cut by crackling veins, in yellow."""
    rng = np.random.default_rng(seed)
    body = pfbm(7, 10, 4, rng)
    v1 = 1 - np.abs(pfbm(10, 13, 3, rng)); v2 = 1 - np.abs(pfbm(24, 32, 2, rng))
    veins = np.clip((v1 - 0.86) / 0.14, 0, 1) ** 2 + 0.6 * np.clip((v2 - 0.9) / 0.1, 0, 1) ** 2
    glow = wrap_blur(veins, 2.5) * 2.2
    t = np.clip(0.28 + 0.12 * body + 0.35 * glow + 0.6 * veins, 0, 1)
    rgb = ramp(t, [(0.0, (30, 24, 2)), (0.3, (110, 92, 10)), (0.55, (205, 180, 40)), (0.8, (255, 235, 120)), (1.0, (255, 255, 225))])
    return rgba(rgb, np.clip(0.72 + 0.1 * body + 0.4 * glow, 0, 0.97))

def _bolts(seed, n):
    """Branching lightning drawn on a 3x3 tiling, folded back so it wraps."""
    r = random.Random(seed); segs = []
    def bolt(a, b, depth):
        if depth == 0: segs.append((a, b)); return
        L0 = math.hypot(b[0] - a[0], b[1] - a[1]); j = 0.18 * L0
        m = ((a[0] + b[0]) / 2 + r.uniform(-j, j), (a[1] + b[1]) / 2 + r.uniform(-j, j))
        bolt(a, m, depth - 1); bolt(m, b, depth - 1)
        if depth >= 3 and r.random() < 0.45:
            ang = math.atan2(b[1] - a[1], b[0] - a[0]) + r.choice([-1, 1]) * r.uniform(0.4, 0.9); L = 0.5 * L0
            bolt(m, (m[0] + math.cos(ang) * L, m[1] + math.sin(ang) * L), depth - 2)
    for _ in range(n):
        cx, cy = r.uniform(0, TW), r.uniform(0, TH); ang = r.uniform(0, 6.3); L = r.uniform(50, 80)
        bolt((cx - math.cos(ang) * L / 2, cy - math.sin(ang) * L / 2), (cx + math.cos(ang) * L / 2, cy + math.sin(ang) * L / 2), 4)
    ss = 2; big = Image.new('RGBA', (TW * 3 * ss, TH * 3 * ss)); d = ImageDraw.Draw(big)
    def draw(fill, width):
        for (a, b) in segs:
            for ox in (0, TW, 2 * TW):
                for oy in (0, TH, 2 * TH):
                    d.line([((a[0] + ox) * ss, (a[1] + oy) * ss), ((b[0] + ox) * ss, (b[1] + oy) * ss)], fill=fill, width=width)
    draw((120, 160, 255, 160), 6 * ss); big = big.filter(ImageFilter.GaussianBlur(4 * ss)); d = ImageDraw.Draw(big)
    draw((240, 245, 255, 255), max(1, int(1.4 * ss)))
    big = big.resize((TW * 3, TH * 3), Image.LANCZOS)
    return np.asarray(big, np.float32)[TH:2 * TH, TW:2 * TW]

def plasma(seed):
    """Plasma storm (big zones): a deep blue storm front with lightning."""
    rng = np.random.default_rng(seed)
    vx, vy = pflow(rng, drift=(0.6, 0.2), swirl=1.0)
    body = psmear(pfbm(6, 8, 4, rng), vx, vy, 10, 2.0)
    wisp = psmear(pfbm(36, 48, 2, rng), vx, vy, 16, 1.5)
    t = np.clip(0.42 + 0.2 * body + 0.08 * wisp, 0, 1)
    rgb = ramp(t, [(0.0, (6, 8, 30)), (0.4, (22, 40, 120)), (0.7, (70, 110, 220)), (1.0, (200, 220, 255))])
    out = rgba(rgb, np.clip(0.78 + 0.15 * body, 0, 0.96)).astype(np.float32)
    bl = _bolts(seed, 7); k = bl[..., 3:4] / 255
    out[..., :3] = out[..., :3] * (1 - k) + bl[..., :3] * k; out[..., 3] = np.maximum(out[..., 3], bl[..., 3])
    return out.astype(np.uint8)

def briar(seed):
    """The Briar Patch, toned down (D): a soft amber-rose nebula with a few metaphasic sparkles."""
    g = nebula(seed, ((40, 18, 14), (170, 105, 75), (240, 205, 170)), 1.05).astype(np.float32)
    g2 = nebula(seed + 2, ((25, 8, 22), (130, 55, 95), (220, 160, 190)), 0.6).astype(np.float32)
    a1, a2 = g[..., 3:4] / 255, g2[..., 3:4] / 255
    rgb = g[..., :3] * a1 + g2[..., :3] * a2 * (1 - a1); a = a1 + a2 * (1 - a1)
    rgb = rgb / np.maximum(a, 1e-3)
    r = np.random.default_rng(seed)
    sp = (r.random((TH, TW)) < 0.0025).astype(np.float32); spk = np.clip(wrap_blur(sp, 0.9) * 7, 0, 1)
    rgb = rgb * (1 - spk[..., None]) + np.array([255, 240, 215]) * spk[..., None]
    a = np.clip(a[..., 0] * 1.12 + spk * 0.86, 0, 1)
    return rgba(rgb, a)

def void(seed):
    """The Void: no stars at all, only faint ripples. Only at a map's cut-off outer parts (D)."""
    rng = np.random.default_rng(seed)
    ripple = 0.5 + 0.5 * np.sin(pfbm(18, 24, 2, rng) * 5)
    rgb = np.zeros((TH, TW, 3), np.float32) + np.array([2, 2, 5]) + np.array([30, 36, 55]) * (ripple ** 6)[..., None]
    return rgba(rgb, np.full((TH, TW), 0.97, np.float32))

FAMILIES = {   # name: (recipe, spill strength)
    'bad':    (lambda: badlands(3, 'shallow'), 0.9),
    'deep':   (lambda: badlands(5, 'deep'), 0.9),
    'swamp':  (lambda: badlands(7, 'swamp'), 0.8),
    'neb':    (lambda: nebula(12, NEB, 0.9, floor=0.3), 0.85),   # holes, so a forest's hex outline does not show
    'dark':   (lambda: nebula(21, ANOM, 1.0, dark=True, floor=0.28), 0.85),
    'dust':   (lambda: nebula(31, DUST, 0.55), 0.8),
    'ice':    (lambda: ice(41), 0.8),
    'corona': (lambda: corona(51), 0.9),
    'rad':    (lambda: radiation(5), 0.9),
    'plasma': (lambda: plasma(7), 0.9),
    'briar':  (lambda: briar(61), 0.9),
    'void':   (lambda: void(9), 0.95),
}
