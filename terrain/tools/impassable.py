# Impassable terrain chosen by the shape of each impassable cluster (D, 16 Nov):
#   touches the map border -> the Void (never inside a map)
#   thin line / wall       -> gravitational eddies, a chain of whirlpools
#   thick blob             -> an area type: plasma storm (big), Briar Patch or radiation zone
#   lone hex               -> one eddy
import math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy.ndimage import map_coordinates, gaussian_filter
import badlands as B

def classify_clusters(imp, neighbours, W, H):
    """imp: set of (x, y). Returns list of (kind, hexes)."""
    seen = set(); out = []
    for p in sorted(imp):
        if p in seen: continue
        comp = []; st = [p]; seen.add(p)
        while st:
            q = st.pop(); comp.append(q)
            for n in neighbours(*q):
                if n in imp and n not in seen: seen.add(n); st.append(n)
        edge = any(x <= 1 or y <= 1 or x >= W - 2 or y >= H - 2 for x, y in comp)
        thick = sum(sum(n in imp for n in neighbours(*q)) >= 4 for q in comp)
        if edge: kind = 'void'
        elif len(comp) == 1: kind = 'lone'
        elif thick >= 3 or (thick >= 1 and len(comp) >= 6): kind = 'area'
        else: kind = 'line'
        out.append((kind, comp))
    # area clusters: biggest are plasma storms, the rest alternate Briar Patch / radiation zone
    k = 0
    for i, (kind, comp) in enumerate(out):
        if kind == 'area':
            out[i] = ('plasma' if len(comp) >= 12 else ['briar', 'radiation'][k % 2], comp); k += kind == 'area' and len(comp) < 12
    return out

HEXV = [(18, 0), (54, 0), (72, 36), (54, 72), (18, 72), (0, 36)]
def _mask(size, pts, sigma):
    return np.clip(B.membership(size, [(x, y, 1.0) for x, y in pts], sigma), 0, 1)

def _rgba(rgb, a):
    return Image.fromarray(np.dstack([np.clip(rgb, 0, 255), np.clip(a, 0, 1) * 255]).astype(np.uint8), 'RGBA')

def glow_lines(size, segs, core, glow, wcore=1.6, wglow=5, blur=4, ss=2):
    big = Image.new('RGBA', (size[0] * ss, size[1] * ss)); d = ImageDraw.Draw(big)
    for (a, b) in segs: d.line([(a[0] * ss, a[1] * ss), (b[0] * ss, b[1] * ss)], fill=glow, width=int(wglow * ss))
    big = big.filter(ImageFilter.GaussianBlur(blur * ss)); d = ImageDraw.Draw(big)
    for (a, b) in segs: d.line([(a[0] * ss, a[1] * ss), (b[0] * ss, b[1] * ss)], fill=core, width=max(1, int(wcore * ss)))
    return big.resize(size, Image.LANCZOS)

# ---- gravitational eddies: whirlpools that bend the starlight; alternate spin, like a vortex street ----
def eddies(canvas, centres, seed=3):
    """Bend the stars under each eddy into arcs, with silver spiral streaks. canvas: RGBA; returns a new image."""
    W_, H_ = canvas.size; arr = np.asarray(canvas.convert('RGB')).astype(float)
    yy, xx = np.mgrid[0:H_, 0:W_].astype(float)
    dx = np.zeros((H_, W_)); dy = np.zeros((H_, W_)); vx = np.full((H_, W_), 1e-6); vy = np.zeros((H_, W_)); M = np.zeros((H_, W_)); eye = np.zeros((H_, W_))
    r = random.Random(seed)
    for i, (cx, cy) in enumerate(centres):
        sgn = 1 if i % 2 == 0 else -1
        cx += r.uniform(-6, 6); cy += r.uniform(-6, 6)
        ddx, ddy = xx - cx, yy - cy; d = np.hypot(ddx, ddy) + 1e-3
        ang = sgn * 3.0 * np.exp(-(d / 26) ** 2)
        dx += ddx * (np.cos(ang) - 1) - ddy * np.sin(ang); dy += ddx * np.sin(ang) + ddy * (np.cos(ang) - 1)
        # inward-spiralling flow for the streaks
        w = np.exp(-(d / 42) ** 2); vx += (sgn * -ddy / d - 0.35 * ddx / d) * w; vy += (sgn * ddx / d - 0.35 * ddy / d) * w
        M = np.maximum(M, np.exp(-(d / 40) ** 4)); eye = np.maximum(eye, np.exp(-(d / 5) ** 2))
    warped = np.dstack([map_coordinates(arr[..., k], [yy + dy, xx + dx], order=1, mode='reflect') for k in range(3)])
    n = np.hypot(vx, vy) + 1e-6
    rng = np.random.default_rng(seed)
    streak = B.smear(B.fbm(H_, W_, 3, 2, rng), vx / n, vy / n, 30, 1.4)
    arms = np.clip((streak - 0.3) / 1.4, 0, 1) ** 1.3 * M
    col = warped * (1 - 0.45 * M[..., None]) + np.array([190, 205, 230]) * (arms * 0.95)[..., None]
    col = col * (1 - 0.85 * eye[..., None])
    out = arr * (1 - M[..., None]) + col * M[..., None]
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).convert('RGBA')

def eddy_centres(comp, ctr):
    return [ctr(q) for q in comp]

# ---- the Void: no stars at all; only at the map's cut-off outer parts ----
def void(size, pts):
    M = _mask(size, pts, 16); H_, W_ = size[1], size[0]
    inner = np.clip((M - 0.35) / 0.35, 0, 1); rim = np.exp(-((M - 0.33) / 0.12) ** 2)
    ripple = 0.55 + 0.45 * np.sin(B.fbm(H_, W_, 12, 2, np.random.default_rng(9)) * 5)
    rgb = np.zeros((H_, W_, 3)) + np.array([70, 85, 120]) * (rim * ripple)[..., None]
    return _rgba(rgb, inner + rim * 0.6)

# ---- radiation zone: after Star Control's, a glowing cloud cut by crackling veins; yellow (green is our nebula) ----
def radiation(size, pts, seed=5):
    H_, W_ = size[1], size[0]; rng = np.random.default_rng(seed); M = _mask(size, pts, 10)
    edge = np.clip((M - 0.15) / 0.55, 0, 1); edge = edge * edge * (3 - 2 * edge)
    body = B.fbm(H_, W_, 30, 4, rng)
    v1 = 1 - np.abs(B.fbm(H_, W_, 22, 3, rng)); v2 = 1 - np.abs(B.fbm(H_, W_, 9, 2, rng))
    veins = np.clip((v1 - 0.86) / 0.14, 0, 1) ** 2 + 0.6 * np.clip((v2 - 0.9) / 0.1, 0, 1) ** 2
    glow = gaussian_filter(veins, 2.5) * 2.2
    t = np.clip(0.28 + 0.12 * body + 0.35 * glow + 0.6 * veins, 0, 1)
    rgb = B.ramp(t, [(0.0, (30, 24, 2)), (0.3, (110, 92, 10)), (0.55, (205, 180, 40)), (0.8, (255, 235, 120)), (1.0, (255, 255, 225))])
    a = np.clip(0.72 + 0.1 * body + 0.4 * glow, 0, 0.97) * edge
    return _rgba(rgb, a)

# ---- plasma storm (big zones): a deep blue storm front with lightning ----
def plasma_storm(size, pts, seed=7):
    H_, W_ = size[1], size[0]; rng = np.random.default_rng(seed); M = _mask(size, pts, 12)
    edge = np.clip((M - 0.15) / 0.55, 0, 1); edge = edge * edge * (3 - 2 * edge)
    vx, vy = B.flow_field(H_, W_, rng, drift=(0.6, 0.2), swirl=1.0)
    body = B.smear(B.fbm(H_, W_, 34, 4, rng), vx, vy, 10, 2.0)
    wisp = B.smear(B.fbm(H_, W_, 6, 2, rng), vx, vy, 16, 1.5)
    t = np.clip(0.42 + 0.2 * body + 0.08 * wisp, 0, 1)
    rgb = B.ramp(t, [(0.0, (6, 8, 30)), (0.4, (22, 40, 120)), (0.7, (70, 110, 220)), (1.0, (200, 220, 255))])
    a = np.clip(0.78 + 0.15 * body, 0, 0.96) * edge
    gas = _rgba(rgb, a)
    # lightning: a few branching bolts inside the storm
    r = random.Random(seed); segs = []
    inside = [p for p in pts]
    def bolt(a_, b_, depth):
        if depth == 0: segs.append((a_, b_)); return
        L0 = math.hypot(b_[0] - a_[0], b_[1] - a_[1]); j = 0.18 * L0
        mx = (a_[0] + b_[0]) / 2 + r.uniform(-j, j); my = (a_[1] + b_[1]) / 2 + r.uniform(-j, j)
        bolt(a_, (mx, my), depth - 1); bolt((mx, my), b_, depth - 1)
        if depth >= 3 and r.random() < 0.45:
            ang = math.atan2(b_[1] - a_[1], b_[0] - a_[0]) + r.choice([-1, 1]) * r.uniform(0.4, 0.9); L = 0.5 * L0
            bolt((mx, my), (mx + math.cos(ang) * L, my + math.sin(ang) * L), depth - 2)
    for i in range(max(1, len(inside) // 6)):
        px, py = r.choice(inside); c = (px + 36, py + 36); ang = r.uniform(0, 6.3); L = r.uniform(50, 80)
        bolt((c[0] - math.cos(ang) * L / 2, c[1] - math.sin(ang) * L / 2), (c[0] + math.cos(ang) * L / 2, c[1] + math.sin(ang) * L / 2), 4)
    gas.alpha_composite(glow_lines(size, segs, (240, 245, 255, 255), (120, 160, 255, 160), 1.4, 6, 4))
    return gas

# ---- Briar Patch (toned down): a soft, dense amber-rose nebula with a few metaphasic sparkles ----
def briar(size, pts, seed=61):
    g = B.render_gas(size, pts, ((40, 18, 14), (170, 105, 75), (240, 205, 170)), seed, 1.05)
    g2 = B.render_gas(size, pts, ((25, 8, 22), (130, 55, 95), (220, 160, 190)), seed + 2, 0.6)
    out = Image.alpha_composite(g2, g)
    a = np.asarray(out).astype(float); r = np.random.default_rng(seed); M = _mask(size, pts, 8)
    sp = (r.random(M.shape) < 0.0025) * (M > 0.6); spk = np.clip(gaussian_filter(sp.astype(float), 0.9) * 7, 0, 1)
    a[..., :3] = a[..., :3] * (1 - spk[..., None]) + np.array([255, 240, 215]) * spk[..., None]
    a[..., 3] = np.clip(a[..., 3] * 1.12 + spk * 220, 0, 255)
    return Image.fromarray(a.astype(np.uint8), 'RGBA')
