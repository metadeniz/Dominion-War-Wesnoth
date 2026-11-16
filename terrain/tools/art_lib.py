# Art helpers shared by the terrain generator (taken from the mockup renderer, tileset/src/mock.py).
import sys, math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy.ndimage import map_coordinates, gaussian_filter

rng = np.random.default_rng(7)

# ---------- helpers ----------
def noise(h, w, scale, octaves=5, seed=0, persist=0.55):
    r = np.random.default_rng(seed); out = np.zeros((h, w)); amp = 1; tot = 0
    for o in range(octaves):
        s = max(2, int(scale * 2 ** o))
        g = r.random((s + 3, s + 3))
        ys = np.linspace(1, s + 1, h)[:, None] * np.ones((1, w))
        xs = np.linspace(1, s + 1, w)[None, :] * np.ones((h, 1))
        out += amp * map_coordinates(g, [ys, xs], order=3, mode='wrap'); tot += amp; amp *= persist
    out /= tot
    return (out - out.min()) / (out.max() - out.min() + 1e-9)

def rgba(arr):
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), 'RGBA')

def hexmask(size=72):
    import os   # Wesnoth's own hard-edged hex mask, so neighbouring hexes meet without hairline gaps
    m = Image.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'hexmask.png')).convert('RGBA')
    return np.asarray(m, np.float32)[..., 3] / 255

HEX = hexmask()

# lighting per design/lighting-preferences.md: one low key light from the right (Wesnoth: upper right),
# weak rim from back left, small front-left fill, no sky light. Screen coords: x right, y down, z to viewer.
def nrm(v): v = np.array(v, float); return v / np.linalg.norm(v)
KEY = nrm([1.0, -0.45, 0.55]); RIM = nrm([-0.8, -0.7, -0.15]); FILL = nrm([-0.6, 0.4, 0.7])
def shade(height, albedo, alpha, key=1.15, rim=0.35, fill=0.14, spec=0.25):
    gy, gx = np.gradient(height)
    n = np.dstack([-gx, -gy, np.ones_like(height)]); n /= np.linalg.norm(n, axis=2, keepdims=True)
    d = lambda L: np.clip((n * L).sum(2), 0, 1)
    lk = d(KEY); h = nrm(KEY + [0, 0, 1])
    sp = np.clip((n * h).sum(2), 0, 1) ** 24 * spec
    rimv = d(RIM) * (1 - n[..., 2]) ** 1.5
    light = key * lk + rim * rimv + fill * d(FILL)
    col = albedo * light[..., None] + 255 * sp[..., None]
    return np.dstack([col, alpha * 255])

# ---------- art generators ----------
def starfield(seed):
    r = np.random.default_rng(100 + seed); a = np.zeros((72, 72, 4)); a[..., :3] = (5, 6, 12); a[..., 3] = 255
    im = rgba(a); dr = ImageDraw.Draw(im)
    for _ in range(r.integers(5, 10)):
        x, y = r.uniform(6, 66), r.uniform(6, 66)
        if HEX[int(y), int(x)] == 0: continue
        b = r.uniform(70, 230) * (1 if r.random() < .85 else 1.1); tint = r.choice([(1, 1, 1), (0.8, 0.9, 1), (1, 0.9, 0.75)])
        c = tuple(int(min(255, b * t)) for t in tint)
        if r.random() < 0.12:
            dr.ellipse([x - 1, y - 1, x + 1, y + 1], fill=c + (255,))
        else:
            dr.point((x, y), fill=c + (255,))
    arr = np.asarray(im).copy(); arr[..., 3] = (HEX * 255).astype(np.uint8)
    return Image.fromarray(arr)

def cloud(seed, size, palette, sigma, dens=1.0, contrast=1.6, wisp=False):
    n = noise(size, size, 3, 6, seed)
    yy, xx = np.mgrid[0:size, 0:size] - size / 2
    # domain warp for wispy, non-blobby shapes
    wx = (noise(size, size, 2, 3, seed + 5) - .5) * size * .35; wy = (noise(size, size, 2, 3, seed + 6) - .5) * size * .35
    n = map_coordinates(n, [np.clip(yy + size / 2 + wy, 0, size - 1), np.clip(xx + size / 2 + wx, 0, size - 1)], order=1)
    rad = np.exp(-(xx ** 2 + yy ** 2) / (2 * sigma ** 2))
    if wisp:
        n2 = noise(size, size, 2, 4, seed + 50)
        n = (1 - np.abs(np.sin(n2 * 10 + n * 5))) ** 2 * (0.4 + n)
    d = np.clip((n * rad * 1.25 - 0.18) * contrast * 0.8, 0, 1) * dens
    p = np.array(palette, float)  # dark, mid, bright
    t = np.clip(d * 1.1, 0, 1)[..., None] ** 1.3
    col = np.where(t < 0.5, p[0] + (p[1] - p[0]) * (t * 2), p[1] + (p[2] - p[1]) * (t * 2 - 1))
    return rgba(np.dstack([col, np.clip(d * 1.1, 0, 0.72) * 255]))

def rock(seed, R, albedo=(100, 95, 90)):
    r = np.random.default_rng(seed); S = int(R * 3) + 4
    yy, xx = np.mgrid[0:S, 0:S] - S / 2
    a = r.uniform(0, 3.14); el = r.uniform(1.0, 1.5)
    u = (xx * np.cos(a) + yy * np.sin(a)) / el; v = -xx * np.sin(a) + yy * np.cos(a)
    th = np.arctan2(v, u); dist = np.hypot(u, v)
    k = r.uniform(0, 6.28, 4)
    Rt = R * (1 + 0.12 * np.sin(2 * th + k[0]) + 0.07 * np.sin(3 * th + k[1]) + 0.04 * np.sin(5 * th + k[2]))
    inside = np.clip(Rt - dist + 0.5, 0, 1)
    h = np.sqrt(np.clip(Rt ** 2 - dist ** 2, 0, None)) * 0.9
    bump = noise(S, S, 4, 4, seed) * R * 0.07
    cr = noise(S, S, 5, 2, seed + 9); h = h + bump * inside - np.clip(cr - 0.75, 0, 1) * R * 0.5 * inside
    alb = np.array(albedo) * (0.8 + 0.35 * noise(S, S, 4, 3, seed + 3))[..., None]
    return rgba(shade(gaussian_filter(h, 0.8), alb, inside, spec=0.05))

def planet(seed, R, kind):
    S = int(R * 2 + 12); yy, xx = (np.mgrid[0:S, 0:S] - S / 2 + 0.5) / R
    d2 = xx ** 2 + yy ** 2; inside = np.clip((1 - np.sqrt(d2)) * R + 0.5, 0, 1)
    z = np.sqrt(np.clip(1 - d2, 0, 1))
    tilt = 0.35; X, Y, Z = xx, yy * math.cos(tilt) - z * math.sin(tilt), yy * math.sin(tilt) + z * math.cos(tilt)
    lon = (np.arctan2(X, Z) + math.pi) / (2 * math.pi); lat = (np.arcsin(np.clip(Y, -1, 1)) + math.pi / 2) / math.pi
    tex = noise(256, 512, 4, 6, seed); clouds = noise(256, 512, 6, 5, seed + 1)
    sm = lambda T: map_coordinates(T, [lat * 255, lon * 511], order=1, mode='wrap')
    t = sm(tex); c = sm(clouds)
    if kind == 'M':
        land = t > 0.52
        col = np.where(land[..., None], np.dstack([70 + 60 * t, 110 + 40 * t, 50 + 20 * t]), np.dstack([20 + 0 * t, 55 + 30 * t, 120 + 60 * t]))
        ice = np.abs(lat - 0.5) > 0.42; col[ice] = (230, 235, 240)
        cl = np.clip((c - 0.55) * 3, 0, 0.9)[..., None]; col = col * (1 - cl) + 245 * cl; atm = (120, 170, 255)
    elif kind == 'ocean':
        col = np.dstack([25 + 40 * t, 80 + 60 * t, 110 + 50 * t]); cl = np.clip((c - 0.5) * 3, 0, 0.9)[..., None]; col = col * (1 - cl) + 235 * cl; atm = (120, 200, 220)
    elif kind == 'desert':
        col = np.dstack([170 + 60 * t, 120 + 50 * t, 70 + 30 * t]); atm = (230, 180, 120)
    elif kind == 'ice':
        col = np.dstack([200 + 40 * t, 215 + 30 * t, 230 + 20 * t]); atm = (180, 220, 255)
    elif kind == 'rock':
        col = np.dstack([110 + 70 * t, 100 + 60 * t, 95 + 50 * t]); atm = None
    else:  # gas
        band = np.sin(lat * 30 + t * 3) * 0.5 + 0.5
        col = np.dstack([180 + 50 * band, 130 + 50 * band, 90 + 40 * band]); atm = (255, 210, 150)
    n = np.dstack([xx, yy, z]); lam = np.clip((n * KEY).sum(2), 0, 1)
    light = 0.04 + 1.15 * lam ** 0.8 + 0.06 * np.clip((n * FILL).sum(2), 0, 1)
    out = np.dstack([col * light[..., None], inside * 255])
    if atm is not None:  # thin atmosphere limb, brighter on the lit side
        dd = np.sqrt(d2); halo = np.exp(-((dd - 1.0) * R / 2.2) ** 2) * np.clip(0.25 + (xx * KEY[0] - yy * 0.3), 0, 1)
        a = np.clip(inside + halo * 0.8, 0, 1); hc = np.array(atm) * halo[..., None]
        out[..., :3] = out[..., :3] * inside[..., None] + hc * (1 - inside[..., None]) + hc * 0.35 * inside[..., None]
        out[..., 3] = a * 255
    return rgba(out)

def station(kind, ruined=False, seed=0):
    # kind 'castle' = docking module, 'keep' = starbase hub. Height map, lit like the ships.
    S = 72; yy, xx = np.mgrid[0:S, 0:S] - S / 2 + 0.5; d = np.hypot(xx, yy); th = np.arctan2(yy, xx)
    if kind == 'keep':
        h = np.where(d < 30, 3, 0.0) + np.where(d < 22, 3, 0) + np.where(d < 13, 6, 0) + np.where(d < 6, 5, 0)
        h += np.where((d > 25) & (d < 30) & (np.cos(th * 8) > 0.6), 1.5, 0)
        alpha = np.clip(31 - d, 0, 1)
    else:
        ring = (d > 11) & (d < 19); hub = d < 6.5
        h = np.where(ring, 3 + np.sqrt(np.clip(16 - (d - 15) ** 2, 0, None)) * 0.7, 0.0) + np.where(hub, 5, 0)
        alpha = np.clip(np.where(ring | hub, 1.0, 0), 0, 1)
    alb = np.ones((S, S, 3)) * (150, 155, 165)
    alb *= (0.85 + 0.25 * noise(S, S, 8, 2, seed + 4))[..., None]
    out = shade(gaussian_filter(h, 0.7), alb, alpha, spec=0.35)
    im = rgba(out); dr = ImageDraw.Draw(im)
    # running lights
    nl = 8 if kind == 'keep' else 6; rr = 27 if kind == 'keep' else 15
    for i in range(nl):
        a = i * 2 * math.pi / nl; x, y = S / 2 + rr * math.cos(a), S / 2 + rr * math.sin(a)
        dr.ellipse([x - 1, y - 1, x + 1, y + 1], fill=(255, 210, 120, 255) if kind == 'keep' else (150, 210, 255, 255))
    if kind == 'keep':
        dr.ellipse([S / 2 - 2, S / 2 - 2, S / 2 + 2, S / 2 + 2], fill=(255, 240, 200, 255))
    if ruined:
        arr = np.asarray(im).copy(); m = noise(S, S, 5, 3, seed + 20) > 0.62
        arr[m, 3] = 0; arr[..., :3] = (arr[..., :3] * 0.7).astype(np.uint8); im = Image.fromarray(arr)
    return im

def drydock(seed=0, ruined=False):
    S = 72; h = np.zeros((S, S)); a = np.zeros((S, S))
    x0, x1, y0, y1 = 13, 59, 21, 51
    def box(xa, xb, ya, yb, hh):
        h[ya:yb, xa:xb] = np.maximum(h[ya:yb, xa:xb], hh); a[ya:yb, xa:xb] = 1
    box(x0, x1, y0, y0 + 4, 4); box(x0, x1, y1 - 4, y1, 4)          # two long girders
    for xx in range(x0, x1 + 1, 9): box(xx, xx + 2, y0, y1, 2.5)       # cross ribs (open frame)
    box(x0 - 2, x0 + 4, y0 - 2, y1 + 2, 5); box(x1 - 4, x1 + 2, y0 - 2, y1 + 2, 5)  # end blocks
    if ruined:
        r = np.random.default_rng(seed); 
        for _ in range(4):
            cx = r.integers(x0, x1); a[:, cx:cx + r.integers(3, 8)] *= (np.arange(S)[:, None] > y1 - 6) | (np.arange(S)[:, None] < y0 + 6) if r.random() < .5 else 0
    alb = np.ones((S, S, 3)) * (150, 152, 160) * (0.85 + 0.25 * noise(S, S, 8, 2, seed + 4))[..., None]
    im = rgba(shade(gaussian_filter(h, 0.6), alb, a, spec=0.3)); dr = ImageDraw.Draw(im)
    for xx in range(x0 + 4, x1 - 2, 9):
        for yy in (y0 + 1, y1 - 2):
            if a[yy, xx] > 0: dr.point((xx, yy), fill=(255, 200, 110, 255))
    return im

def platform(seed=0, ruined=False):
    S = 72; yy, xx = np.mgrid[0:S, 0:S] - S / 2 + 0.5; d = np.maximum(np.abs(xx), np.abs(yy)) * 0.7 + np.hypot(xx, yy) * 0.3
    R = 14; a = np.clip(R - d, 0, 1); h = np.where(d < R, 3, 0.0) + np.where(d < 8, 3, 0) + np.where(d < 4, 2, 0)
    for ang in (-0.6, 2.5):  # two turret barrels
        u = xx * np.cos(ang) + yy * np.sin(ang); v = -xx * np.sin(ang) + yy * np.cos(ang)
        bar = (u > 4) & (u < 21) & (np.abs(v) < 1.6); h = np.where(bar, 7, h); a = np.maximum(a, bar * 1.0)
    alb = np.ones((S, S, 3)) * (140, 135, 130) * (0.85 + 0.25 * noise(S, S, 8, 2, seed + 4))[..., None]
    im = rgba(shade(gaussian_filter(h, 0.6), alb, a, spec=0.3)); dr = ImageDraw.Draw(im)
    dr.ellipse([34.5, 34.5, 37.5, 37.5], fill=(255, 70, 50, 255))
    if ruined:
        arr = np.asarray(im).copy(); m = noise(S, S, 5, 3, seed + 20) > 0.6; arr[m, 3] = 0; im = Image.fromarray(arr)
    return im

def debris(seed):
    r = random.Random(seed); im = Image.new('RGBA', (72, 72)); d = ImageDraw.Draw(im)
    for _ in range(6):
        cx, cy = r.uniform(14, 58), r.uniform(14, 58); L = r.uniform(4, 11); W = r.uniform(2, 4.5); a = r.uniform(0, 3.14)
        ca, sa = math.cos(a), math.sin(a)
        pts = [(cx + ca * u - sa * v, cy + sa * u + ca * v) for u, v in [(-L, -W), (L, -W * r.uniform(.3, 1)), (L * r.uniform(.6, 1), W), (-L, W)]]
        lit = 0.55 + 0.45 * max(0, ca)
        d.polygon(pts, fill=tuple(int(c * lit) for c in (165, 168, 175)) + (255,))
        d.line(pts[:2], fill=(215, 220, 228, 255), width=1)
        if r.random() < 0.5: d.line(pts[2:], fill=(255, 140, 60, 220), width=1)  # scorched edge
    return im

def buoys(dirc):
    im = Image.new('RGBA', (72, 72)); d = ImageDraw.Draw(im)
    v = {'|': (0, 1), '/': (0.83, -0.55), '\\': (0.83, 0.55)}.get(dirc, (0, 1))
    pts = [(36 + v[0] * t, 36 + v[1] * t) for t in (-26, 0, 26)]
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        for k in range(1, 6): d.point((ax + (bx - ax) * k / 6, ay + (by - ay) * k / 6), fill=(140, 230, 255, 160))
    g = Image.new('RGBA', (72, 72)); dg = ImageDraw.Draw(g)
    for x, y in pts: dg.ellipse([x - 5, y - 5, x + 5, y + 5], fill=(120, 220, 255, 120))
    g = g.filter(ImageFilter.GaussianBlur(2.5)); out = Image.alpha_composite(g, im); d = ImageDraw.Draw(out)
    for x, y in pts: d.ellipse([x - 2, y - 2, x + 2, y + 2], fill=(110, 115, 125, 255)); d.point((x, y), fill=(230, 250, 255, 255))
    return out

HEXV = [(18, 0), (54, 0), (72, 36), (54, 72), (18, 72), (0, 36)]
EDGE = {0: (0, 1), 1: (1, 2), 2: (2, 3), 3: (3, 4), 4: (4, 5), 5: (5, 0)}
def shield_layer(size, edges, tints):
    glow = Image.new('RGBA', size); core = Image.new('RGBA', size); tint = Image.new('RGBA', size)
    dg, dc, dt = ImageDraw.Draw(glow), ImageDraw.Draw(core), ImageDraw.Draw(tint)
    for (px, py) in tints:
        dt.polygon([(px + vx, py + vy) for vx, vy in HEXV], fill=(90, 180, 255, 26))
    pyl = set()
    for (px, py, e, broken) in edges:
        i, j = EDGE[e]; (ax, ay), (bx, by) = HEXV[i], HEXV[j]
        # pull the line 3px inside the castle hex so neighbouring art isn't covered
        cx, cy = 36, 36; k = 3 / 36
        ax2, ay2, bx2, by2 = px + ax + (cx - ax) * k, py + ay + (cy - ay) * k, px + bx + (cx - bx) * k, py + by + (cy - by) * k
        segs = [(0, 1)] if not broken else [(0, .3), (.55, .75)]
        for s0, s1 in segs:
            p0 = (ax2 + (bx2 - ax2) * s0, ay2 + (by2 - ay2) * s0); p1 = (ax2 + (bx2 - ax2) * s1, ay2 + (by2 - ay2) * s1)
            dg.line([p0, p1], fill=(80, 190, 255, 200), width=7); dc.line([p0, p1], fill=(190, 240, 255, 230), width=2)
        pyl.add((round(ax2), round(ay2))); pyl.add((round(bx2), round(by2)))
    glow = glow.filter(ImageFilter.GaussianBlur(4))
    out = Image.alpha_composite(tint, glow); out = Image.alpha_composite(out, core); d = ImageDraw.Draw(out)
    for (x, y) in pyl:
        d.ellipse([x - 3, y - 3, x + 3, y + 3], fill=(120, 125, 135, 255)); d.ellipse([x - 1, y - 1, x + 1, y + 1], fill=(200, 245, 255, 255))
    return out

def _hexpoly(inset=0):
    c = 36; return [(c + (vx - c) * (1 - inset / 36), c + (vy - c) * (1 - inset / 36)) for vx, vy in HEXV]

def deck(seed=0, ruined=False):
    # continuous hangar-deck plating: fills the hex so neighbouring castle hexes form one floor
    S = 72; m = Image.new('L', (S, S), 0); ImageDraw.Draw(m).polygon(_hexpoly(0), fill=255); mask = np.asarray(m) / 255.0
    yy, xx = np.mgrid[0:S, 0:S]
    h = np.zeros((S, S)); h += ((xx % 12) < 1) * -0.8 + ((yy % 12) < 1) * -0.8      # panel seams
    h += noise(S, S, 6, 2, seed) * 0.6
    alb = np.ones((S, S, 3)) * (78, 84, 96)
    alb[((xx // 12 + yy // 12) % 3 == 0)] *= 1.12
    if ruined:
        holes = noise(S, S, 4, 3, seed + 30) > 0.62; mask = mask * (~holes)
        alb *= (0.7 + 0.3 * noise(S, S, 5, 2, seed + 31))[..., None]
    im = rgba(shade(gaussian_filter(h, 0.5), alb, mask, key=0.9, rim=0.2, fill=0.3, spec=0.15)); d = ImageDraw.Draw(im)
    if not ruined:
        d.ellipse([22, 22, 50, 50], outline=(230, 190, 90, 150), width=1)           # landing ring
        for t in (-14, -7, 7, 14): d.point((36 + t, 36), fill=(255, 210, 120, 255)); d.point((36, 36 + t), fill=(120, 200, 255, 255))
    return im

def clamp(seed=0, ruined=False):
    # docking clamps: two curved arms holding the berth, with a tractor-beam glow between them
    S = 72; im = Image.new('RGBA', (S, S)); g = Image.new('RGBA', (S, S))
    if not ruined:
        ImageDraw.Draw(g).ellipse([20, 26, 52, 46], fill=(100, 200, 255, 70)); g = g.filter(ImageFilter.GaussianBlur(5))
    yy, xx = np.mgrid[0:S, 0:S] - S / 2 + 0.5; d = np.hypot(xx * 0.8, yy); th = np.arctan2(yy, xx)
    arm = (d > 17) & (d < 22) & (np.abs(np.cos(th)) > 0.45)
    if ruined: arm &= ~((yy < 0) & (xx > 0))
    h = np.where(arm, 3 + np.sqrt(np.clip(6.25 - (d - 19.5) ** 2, 0, None)), 0.0)
    pads = ((np.abs(np.abs(xx) - 22) < 3) & (np.abs(yy) < 4)) & (~((xx > 0) & ruined))
    h = np.where(pads, 5, h); a = (arm | pads) * 1.0
    alb = np.ones((S, S, 3)) * (155, 158, 168)
    out = Image.alpha_composite(g, rgba(shade(gaussian_filter(h, 0.6), alb, a, spec=0.35)))
    dr = ImageDraw.Draw(out)
    for x in (13.5, 58.5): dr.point((x, 36), fill=(150, 230, 255, 255))
    return out

def grid(seed=0, ruined=False):
    # defence grid: phaser emplacements on two corners, a faint emitter lattice in between
    S = 72; im = Image.new('RGBA', (S, S)); d = ImageDraw.Draw(im)
    if not ruined:
        for k in range(-3, 4):
            d.line([(36 + k * 9 - 20, 16), (36 + k * 9 + 20, 56)], fill=(90, 190, 255, 35)); d.line([(36 + k * 9 + 20, 16), (36 + k * 9 - 20, 56)], fill=(90, 190, 255, 35))
    for (cx, cy) in [(18, 14), (54, 58)] if not ruined else [(18, 14)]:
        yy, xx = np.mgrid[0:S, 0:S] - np.array([cy, cx])[:, None, None]
        dd = np.hypot(xx, yy); dome = dd < 6.5
        h = np.where(dome, np.sqrt(np.clip(42 - dd ** 2, 0, None)), 0.0)
        bar = (xx > 2) & (xx < 13) & (np.abs(yy + xx * 0.25) < 1.3) if cx < 36 else (xx < -2) & (xx > -13) & (np.abs(yy + xx * 0.25) < 1.3)
        h = np.where(bar, 6, h); a = (dome | bar) * 1.0
        im = Image.alpha_composite(im, rgba(shade(gaussian_filter(h, 0.6), np.ones((S, S, 3)) * (150, 150, 158), a, spec=0.4)))
        ImageDraw.Draw(im).point((cx, cy), fill=(255, 90, 60, 255))
    return im

def gantry(seed=0, ruined=False):
    # repair gantry: a truss crane arm reaching over the berth, with work lights
    S = 72; im = Image.new('RGBA', (S, S)); d = ImageDraw.Draw(im)
    base = (14, 54); elbow = (22, 22); tip = (46, 18) if not ruined else (40, 30)
    for (a, b) in [(base, elbow), (elbow, tip)]:
        (ax, ay), (bx, by) = a, b; L = math.hypot(bx - ax, by - ay); ux, uy = (bx - ax) / L, (by - ay) / L; px, py = -uy * 2.5, ux * 2.5
        d.line([(ax + px, ay + py), (bx + px, by + py)], fill=(185, 188, 196, 255), width=1)
        d.line([(ax - px, ay - py), (bx - px, by - py)], fill=(110, 112, 120, 255), width=1)
        n = int(L // 4)
        for i in range(n + 1):
            t = i / max(n, 1); x, y = ax + (bx - ax) * t, ay + (by - ay) * t; s = 1 if i % 2 else -1
            d.line([(x + px * s, y + py * s), (x + (bx - ax) / n - px * s, y + (by - ay) / n - py * s)], fill=(150, 152, 160, 255))
    d.ellipse([base[0] - 4, base[1] - 4, base[0] + 4, base[1] + 4], fill=(120, 122, 130, 255))
    tx, ty = tip; d.line([(tx, ty), (tx + 4, ty + 6)], fill=(170, 170, 178, 255), width=2); d.line([(tx, ty), (tx - 3, ty + 6)], fill=(170, 170, 178, 255), width=2)
    if not ruined:
        g = Image.new('RGBA', (S, S)); ImageDraw.Draw(g).polygon([(tx, ty + 4), (tx - 10, ty + 26), (tx + 12, ty + 26)], fill=(255, 220, 150, 40))
        im = Image.alpha_composite(g.filter(ImageFilter.GaussianBlur(3)), im); d = ImageDraw.Draw(im)
        d.point((tx, ty + 3), fill=(255, 240, 200, 255)); d.point(elbow, fill=(255, 80, 60, 255))
    return im

def wall_layer(size, edges, seed=0):
    # physical perimeter for ruined castles: armour plates and girders along the outer edge, broken in places
    r = random.Random(seed); out = Image.new('RGBA', size); d = ImageDraw.Draw(out)
    glow = Image.new('RGBA', size); dg = ImageDraw.Draw(glow)
    for (px, py, e) in edges:
        i, j = EDGE[e]; (ax, ay), (bx, by) = HEXV[i], HEXV[j]; k = 4 / 36
        ax, ay, bx, by = px + ax + (36 - ax) * k, py + ay + (36 - ay) * k, px + bx + (36 - bx) * k, py + by + (36 - by) * k
        L = math.hypot(bx - ax, by - ay); ux, uy = (bx - ax) / L, (by - ay) / L; nx, ny = -uy, ux
        nseg = 3
        for sgi in range(nseg):
            if r.random() < 0.3: continue  # breach
            t0, t1 = sgi / nseg + 0.02, (sgi + 1) / nseg - 0.02
            off = r.uniform(-1.5, 1.5); w = 3.2
            p = lambda t, o: (ax + (bx - ax) * t + nx * o, ay + (by - ay) * t + ny * o)
            poly = [p(t0, off - w), p(t1, off - w + r.uniform(-1, 1)), p(t1, off + w), p(t0, off + w)]
            lit = 0.55 + 0.45 * max(0, nx * 0.8 - ny * 0.5)
            d.polygon(poly, fill=tuple(int(c * lit) for c in (140, 140, 146)) + (255,))
            d.line(poly[:2], fill=(200, 202, 208, 255), width=1)
            if r.random() < 0.35:
                q = p(t1, off); dg.ellipse([q[0] - 3, q[1] - 3, q[0] + 3, q[1] + 3], fill=(255, 130, 40, 180))
        for t in (0.0, 1.0):
            q = (ax + (bx - ax) * t, ay + (by - ay) * t); d.rectangle([q[0] - 3, q[1] - 3, q[0] + 3, q[1] + 3], fill=(95, 95, 102, 255))
    return Image.alpha_composite(glow.filter(ImageFilter.GaussianBlur(2)), out)

def _lit(c, f): return tuple(int(min(255, v * f)) for v in c) + (255,)
FRAME = (196, 198, 204)

def arch(seed=0, ruined=False):
    # Utopia Planitia drydock as seen around Voyager: a spine of arched ribs over the berth
    S = 72; im = Image.new('RGBA', (S, S)); d = ImageDraw.Draw(im); r = random.Random(seed)
    ribs = [14, 25, 36, 47, 58]
    if ruined: ribs = [y for y in ribs if r.random() > 0.4]
    for x in (15, 57):  # side rails
        segs = [(10, 62)] if not ruined else [(10, 30), (42, 62)]
        for a, b in segs:
            d.line([(x, a), (x, b)], fill=_lit(FRAME, 0.65 if x < 36 else 1.0), width=2)
    for y in ribs:
        # an arch seen from above at 45 degrees: a shallow curve bowing up-screen
        pts = [(15 + 42 * t, y - 7 * math.sin(math.pi * t)) for t in [i / 16 for i in range(17)]]
        if ruined and r.random() < 0.5: pts = pts[:r.randint(5, 11)]
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            d.line([(x0, y0), (x1, y1)], fill=_lit(FRAME, 0.6 + 0.45 * (x0 / 72)), width=2)
        if not ruined or r.random() < 0.5:
            d.point(pts[len(pts) // 2], fill=(255, 210, 110, 255))
        for (x, yy) in (pts[0], pts[-1]): d.point((x, yy + 1), fill=(255, 190, 90, 255))
    if not ruined:
        g = Image.new('RGBA', (S, S)); dg = ImageDraw.Draw(g)
        for y in ribs: dg.ellipse([33, y - 9, 39, y - 3], fill=(255, 220, 140, 90))
        im = Image.alpha_composite(g.filter(ImageFilter.GaussianBlur(2)), im)
    return im

def cage(seed=0, ruined=False):
    # TNG-style lattice drydock: an open box of girders with floodlights at the corners
    S = 72; im = Image.new('RGBA', (S, S)); d = ImageDraw.Draw(im); r = random.Random(seed)
    x0, x1, y0, y1 = 14, 58, 16, 56
    glow = Image.new('RGBA', (S, S)); dg = ImageDraw.Draw(glow)
    if not ruined:
        for (cx, cy) in [(x0, y0), (x1, y0), (x0, y1), (x1, y1)]:
            dg.polygon([(cx, cy), (36 + (cx - 36) * 0.15 - 6, 36 + (cy - 36) * 0.15), (36 + (cx - 36) * 0.15 + 6, 36 + (cy - 36) * 0.15)], fill=(255, 245, 220, 45))
    for k in range(5):  # lattice
        x = x0 + (x1 - x0) * k / 4; y = y0 + (y1 - y0) * k / 4
        if not (ruined and r.random() < 0.4): d.line([(x, y0), (x, y1)], fill=_lit(FRAME, 0.55), width=1)
        if not (ruined and r.random() < 0.4): d.line([(x0, y), (x1, y)], fill=_lit(FRAME, 0.55), width=1)
    for (a, b, f) in [((x0, y0), (x1, y0), 0.95), ((x1, y0), (x1, y1), 1.05), ((x1, y1), (x0, y1), 0.8), ((x0, y1), (x0, y0), 0.6)]:
        if ruined and r.random() < 0.35: continue
        d.line([a, b], fill=_lit(FRAME, f), width=2)
    for (cx, cy) in [(x0, y0), (x1, y0), (x0, y1), (x1, y1)]:
        d.rectangle([cx - 2, cy - 2, cx + 2, cy + 2], fill=_lit(FRAME, 0.8))
        if not ruined: d.point((cx, cy), fill=(255, 255, 235, 255))
    for k in range(1, 4):
        if not ruined: d.point((x0 + (x1 - x0) * k / 4, y0), fill=(255, 200, 100, 255)); d.point((x0 + (x1 - x0) * k / 4, y1), fill=(255, 200, 100, 255))
    return Image.alpha_composite(glow.filter(ImageFilter.GaussianBlur(3)), im)

def bastion(seed=0, ruined=False):
    # defensive outpost for castle hexes with no keep: an armoured plate with point-defence turrets, no berth (D)
    S = 72; ss = 3; im = Image.new('RGBA', (S * ss, S * ss)); d = ImageDraw.Draw(im); r = random.Random(seed)
    P = lambda pts: [(x * ss, y * ss) for x, y in pts]
    c = 36; hexp = lambda k, rot=0: [(c + k * math.cos(math.radians(60 * i + rot)), c + k * math.sin(math.radians(60 * i + rot))) for i in range(6)]
    outer = hexp(17, 30); inner = hexp(12, 30)
    d.polygon(P(outer), fill=_lit((120, 122, 130), 0.75))
    for i in range(6):  # bevel: lit from the upper right
        a, b = outer[i], outer[(i + 1) % 6]; mx, my = (a[0] + b[0]) / 2 - c, (a[1] + b[1]) / 2 - c
        f = 0.6 + 0.55 * max(0, (mx * 0.8 - my * 0.6) / 17)
        d.polygon(P([a, b, inner[(i + 1) % 6], inner[i]]), fill=_lit((150, 152, 160), f))
    d.polygon(P(inner), fill=_lit((95, 97, 105), 1.0))
    for i in range(3):  # armour seams
        a = inner[i]; b = inner[i + 3]; d.line(P([a, b]), fill=_lit((70, 72, 80), 1.0), width=ss)
    lost = r.randrange(3) if ruined else -1
    glow = Image.new('RGBA', im.size); dg = ImageDraw.Draw(glow)
    for k in range(3):  # turrets at alternate corners, barrels pointing out
        ang = math.radians(-90 + 120 * k + 30 + (seed % 2) * 60)
        tx, ty = c + 22 * math.cos(ang), c + 22 * math.sin(ang)
        if k == lost:
            d.ellipse(P([(tx - 2.5, ty - 2.5), (tx + 2.5, ty + 2.5)]), fill=(55, 50, 48, 255)); continue
        d.line(P([(c + 15 * math.cos(ang), c + 15 * math.sin(ang)), (tx, ty)]), fill=_lit(FRAME, 0.7), width=2 * ss)
        d.ellipse(P([(tx - 4.5, ty - 4.5), (tx + 4.5, ty + 4.5)]), fill=_lit(FRAME, 0.55))
        d.ellipse(P([(tx - 3.2, ty - 3.8), (tx + 3.2, ty + 2.6)]), fill=_lit(FRAME, 0.95))
        bx, by = tx + 8 * math.cos(ang), ty + 8 * math.sin(ang)
        for o in (-1.2, 1.2):
            ox, oy = -math.sin(ang) * o, math.cos(ang) * o
            d.line(P([(tx + ox, ty + oy), (bx + ox, by + oy)]), fill=_lit(FRAME, 0.8), width=ss)
        if not ruined:
            dg.ellipse(P([(bx - 2.5, by - 2.5), (bx + 2.5, by + 2.5)]), fill=(255, 120, 60, 170))
            d.ellipse(P([(tx - 0.8, ty - 0.8), (tx + 0.8, ty + 0.8)]), fill=(255, 90, 70, 255))
    # centre: shield emitter dome
    d.ellipse(P([(c - 5.5, c - 5.5), (c + 5.5, c + 5.5)]), fill=_lit((110, 115, 128), 1.0))
    d.ellipse(P([(c - 3.5, c - 4.5), (c + 3, c + 1.5)]), fill=_lit((170, 180, 195), 1.0) if not ruined else (60, 58, 56, 255))
    if not ruined:
        dg.ellipse(P([(c - 7, c - 7), (c + 7, c + 7)]), fill=(90, 190, 255, 120))
        d.ellipse(P([(c - 1.2, c - 2.2), (c + 1.2, c + 0.2)]), fill=(220, 250, 255, 255))
    else:  # scorch and a breach
        dg.ellipse(P([(c + 3, c + 2), (c + 13, c + 10)]), fill=(255, 110, 30, 60))
        d.polygon(P([(c + 6, c + 3), (c + 12, c + 6), (c + 8, c + 10), (c + 4, c + 7)]), fill=(25, 22, 22, 255))
    im = Image.alpha_composite(glow.filter(ImageFilter.GaussianBlur(3 * ss)), im)
    return im.resize((S, S), Image.LANCZOS)

def ancient(seed=0):
    # ancient base (Iconian / Tkon style ruin) for lone ruined castle hexes: weathered concentric walls, faint glyph light (D)
    S = 72; ss = 3; im = Image.new('RGBA', (S * ss, S * ss)); d = ImageDraw.Draw(im); r = random.Random(seed * 31 + 7)
    P = lambda pts: [(x * ss, y * ss) for x, y in pts]; c = 36
    STONE = (170, 150, 118)
    glow = Image.new('RGBA', im.size); dg = ImageDraw.Draw(glow)
    # foundation disc, pitted
    d.ellipse(P([(c - 20, c - 18), (c + 20, c + 18)]), fill=_lit(STONE, 0.38))
    for _ in range(14):
        x, y, k = r.uniform(c - 16, c + 16), r.uniform(c - 14, c + 14), r.uniform(0.8, 2.2)
        d.ellipse(P([(x - k, y - k), (x + k, y + k)]), fill=_lit(STONE, 0.28))
    t = math.radians(r.uniform(0, 360)); d.ellipse(P([(c + 21 * math.cos(t) - 8, c + 19 * math.sin(t) - 7), (c + 21 * math.cos(t) + 8, c + 19 * math.sin(t) + 7)]), fill=(0, 0, 0, 0))
    # two broken ring walls, lit from the upper right
    for R, w, gaps in [(18, 2.6, 3), (10.5, 2.2, 2)]:
        a = r.uniform(0, 360)
        for g in range(gaps):
            span = 360 / gaps; a0 = a + g * span; a1 = a0 + span * r.uniform(0.45, 0.75)
            steps = 18
            for k in range(steps):
                t0 = math.radians(a0 + (a1 - a0) * k / steps); t1 = math.radians(a0 + (a1 - a0) * (k + 1) / steps)
                lit = 0.6 + 0.5 * max(0, math.cos(t0 + math.radians(40)))
                pa = (c + R * math.cos(t0), c + R * 0.9 * math.sin(t0)); pb = (c + R * math.cos(t1), c + R * 0.9 * math.sin(t1))
                d.line(P([pa, pb]), fill=_lit(STONE, lit), width=int(w * ss))
            # fallen block beside each broken end
            t = math.radians(a1 + 8); bx, by = c + (R + r.uniform(-2, 3)) * math.cos(t), c + R * 0.9 * math.sin(t)
            d.rectangle(P([(bx - 1.5, by - 1.2), (bx + 1.5, by + 1.2)]), fill=_lit(STONE, 0.8))
    # radial causeways
    for k in range(4):
        if r.random() < 0.3: continue
        t = math.radians(45 + 90 * k + r.uniform(-8, 8))
        d.line(P([(c + 11 * math.cos(t), c + 10 * math.sin(t)), (c + 17 * math.cos(t), c + 16 * math.sin(t))]), fill=_lit(STONE, 0.7), width=2 * ss)
    # central hexagonal dais with a dim glyph circle
    hx = [(c + 5.5 * math.cos(math.radians(60 * i)), c + 5 * math.sin(math.radians(60 * i))) for i in range(6)]
    d.polygon(P(hx), fill=_lit(STONE, 0.85))
    d.polygon(P([(x - 0.8, y - 0.8) for x, y in hx[3:] + hx[:1]]), fill=_lit(STONE, 1.1))
    dg.ellipse(P([(c - 8, c - 7), (c + 8, c + 7)]), fill=(70, 230, 200, 150))
    for i in range(6):
        if r.random() < 0.35: continue
        t = math.radians(60 * i + 30); x, y = c + 3.2 * math.cos(t), c + 3 * math.sin(t)
        d.ellipse(P([(x - 0.7, y - 0.7), (x + 0.7, y + 0.7)]), fill=(160, 255, 230, 255))
    im = Image.alpha_composite(glow.filter(ImageFilter.GaussianBlur(3 * ss)), im)
    return im.resize((S, S), Image.LANCZOS)

def bees(seed=0):
    # work bees and tugs: tiny pods with running lights
    S = 72; im = Image.new('RGBA', (S, S)); d = ImageDraw.Draw(im); r = random.Random(seed)
    for _ in range(3):
        x, y = r.uniform(18, 54), r.uniform(18, 54)
        d.rectangle([x - 1.5, y - 1, x + 1.5, y + 1], fill=(220, 220, 225, 255)); d.point((x + 2, y), fill=(255, 170, 60, 255))
    return im

def conduit(direction):
    S = 72; im = Image.new('RGBA', (S, S)); d = ImageDraw.Draw(im)
    ang = -math.pi / 2 + direction * math.pi / 3; ex, ey = 36 + 37 * math.cos(ang), 36 + 37 * math.sin(ang)
    d.line([(36, 36), (ex, ey)], fill=(120, 220, 255, 150), width=3)
    g = im.filter(ImageFilter.GaussianBlur(2)); d2 = ImageDraw.Draw(im); d2.line([(36, 36), (ex, ey)], fill=(220, 245, 255, 220), width=1)
    return Image.alpha_composite(g, im)

def mars_layer(size, hexes):
    # the red planet far below the yard: one continuous surface under all castle and keep hexes
    W, H = size; rng = np.random.default_rng(42)
    n = noise(H, W, 6, 6, 42); n2 = noise(H, W, 18, 4, 43)
    col = np.dstack([150 + 70 * n, 62 + 40 * n, 32 + 22 * n]) * (0.75 + 0.35 * n2)[..., None]
    yy, xx = np.mgrid[0:H, 0:W]
    for _ in range(int(W * H / 9000)):
        cx, cy, rr = rng.uniform(0, W), rng.uniform(0, H), rng.uniform(3, 14)
        dd = np.hypot(xx[int(max(0, cy - rr - 2)):int(cy + rr + 2), int(max(0, cx - rr - 2)):int(cx + rr + 2)] - cx, yy[int(max(0, cy - rr - 2)):int(cy + rr + 2), int(max(0, cx - rr - 2)):int(cx + rr + 2)] - cy)
        sl = (slice(int(max(0, cy - rr - 2)), int(cy + rr + 2)), slice(int(max(0, cx - rr - 2)), int(cx + rr + 2)))
        col[sl] *= (1 - 0.25 * np.exp(-((dd - rr * 0.6) / (rr * 0.25)) ** 2) * (dd < rr))[..., None]
        col[sl] *= (1 + 0.2 * np.exp(-((dd - rr) / 1.5) ** 2))[..., None]
    col *= 0.62  # far below, in shadow
    m = Image.new('L', size, 0); dm = ImageDraw.Draw(m)
    for (px, py) in hexes: dm.polygon([(px + vx, py + vy) for vx, vy in HEXV], fill=255)
    a = np.asarray(m, np.float32)
    return rgba(np.dstack([col, a]))

INTERIOR = {'dock': drydock, 'deck': deck, 'clamp': clamp, 'grid': grid, 'gantry': gantry, 'arch': arch, 'cage': cage, 'marsarch': arch, 'yard': cage}

def strut(direction):
    # a connecting truss from centre to the hex edge in one of 6 directions (0=N, clockwise)
    S = 72; im = Image.new('RGBA', (S, S)); dr = ImageDraw.Draw(im)
    ang = -math.pi / 2 + direction * math.pi / 3; L = 37
    cx, cy = S / 2, S / 2; ex, ey = cx + L * math.cos(ang), cy + L * math.sin(ang)
    px, py = -math.sin(ang) * 2.2, math.cos(ang) * 2.2
    lit = 0.6 + 0.4 * max(0, math.cos(ang) * 0.5 + 0.5)
    c = tuple(int(v * lit) for v in (150, 155, 165)) + (255,)
    dr.polygon([(cx + px, cy + py), (ex + px, ey + py), (ex - px, ey - py), (cx - px, cy - py)], fill=c)
    dr.line([(cx + px, cy + py), (ex + px, ey + py)], fill=(200, 205, 215, 255), width=1)
    return im

def lightning(seed, size):
    r = random.Random(seed); im = Image.new('RGBA', (size, size)); dr = ImageDraw.Draw(im)
    for _ in range(2):
        x, y = size / 2 + r.uniform(-15, 15), size / 2 + r.uniform(-15, 15); pts = [(x, y)]
        ang = r.uniform(0, 6.28)
        for _ in range(7):
            ang += r.uniform(-0.9, 0.9); x += 5 * math.cos(ang); y += 5 * math.sin(ang); pts.append((x, y))
        dr.line(pts, fill=(170, 210, 255, 200), width=2)
    glow = im.filter(ImageFilter.GaussianBlur(3)); sharp = Image.new('RGBA', (size, size)); ImageDraw.Draw(sharp)
    out = Image.alpha_composite(glow, glow); out = Image.alpha_composite(out, im)
    return out

def beacon():
    im = Image.new('RGBA', (72, 72)); dr = ImageDraw.Draw(im)
    g = Image.new('RGBA', (72, 72)); ImageDraw.Draw(g).ellipse([31, 31, 41, 41], fill=(255, 170, 60, 110)); g = g.filter(ImageFilter.GaussianBlur(3))
    dr.ellipse([34.5, 34.5, 37.5, 37.5], fill=(255, 200, 110, 255)); return Image.alpha_composite(g, im)

# ---------- palettes ----------
NEB = {k: ((10, 50, 25), (35, 140, 70), (170, 255, 190)) for k in ('pine', 'mixed', 'great', 'tropical', 'snow')}  # D: all forests are green nebulae
ION = ((20, 30, 70), (60, 100, 200), (200, 230, 255))
PLASMA = ((80, 10, 30), (200, 50, 60), (255, 170, 110))
DEEP = ((50, 5, 20), (140, 20, 40), (240, 90, 60))
ANOM = ((8, 2, 16), (70, 25, 115), (180, 120, 240))  # dark matter nebula: purple (D)
DUST = ((40, 30, 20), (110, 85, 55), (200, 170, 120))



