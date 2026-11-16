# Rough space-tileset mockup: renders a Wesnoth .map with procedural space art,
# composited per hex the way Wesnoth would (base tile + oversized overlays, sorted by layer).
import sys, math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy.ndimage import map_coordinates, gaussian_filter

MAP = sys.argv[1]; OUT = sys.argv[2]
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
    im = Image.new('L', (size, size), 0)
    ImageDraw.Draw(im).polygon([(18, 0), (54, 0), (71, 36), (54, 71), (18, 71), (0, 36)], fill=255)
    return np.asarray(im) / 255.0

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
NEB = {'pine': ((20, 40, 90), (40, 110, 170), (150, 220, 255)),
       'mixed': ((50, 20, 80), (120, 50, 160), (230, 160, 255)),
       'great': ((70, 20, 60), (170, 60, 140), (255, 190, 230)),
       'tropical': ((80, 25, 20), (190, 80, 40), (255, 200, 140)),
       'snow': ((40, 50, 70), (130, 150, 180), (240, 245, 255))}
ION = ((20, 30, 70), (60, 100, 200), (200, 230, 255))
PLASMA = ((80, 10, 30), (200, 50, 60), (255, 170, 110))
DEEP = ((50, 5, 20), (140, 20, 40), (240, 90, 60))
ANOM = ((10, 50, 30), (40, 160, 90), (190, 255, 200))
DUST = ((40, 30, 20), (110, 85, 55), (200, 170, 120))

# ---------- map ----------
rows = [[c.strip() for c in l.split(',')] for l in open(MAP).read().strip().splitlines() if l.strip()]
H, W = len(rows), len(rows[0])
def code(x, y):
    if 0 <= y < H and 0 <= x < W: return rows[y][x].split(' ')[-1]
    return '_off^_usr'
def pix(x, y): return x * 54, y * 72 + (36 if x % 2 == 0 else 0)
def neighbours(x, y):  # 0=N,1=NE,2=SE,3=S,4=SW,5=NW (file index == 1-based wesnoth x; even x shifted down)
    if x % 2 == 0: return [(x, y - 1), (x + 1, y), (x + 1, y + 1), (x, y + 1), (x - 1, y + 1), (x - 1, y)]
    return [(x, y - 1), (x + 1, y - 1), (x + 1, y), (x, y + 1), (x - 1, y), (x - 1, y - 1)]

def classify(c):
    base, _, ov = c.partition('^'); L = []  # list of (layer, kind, param)
    if c.startswith('_off'): return [('void',)]
    b0 = base[:1]
    if base.startswith('Wwf'): L.append(('cloud', 'eddy'))
    elif base.startswith('Wo'): L.append(('cloud', 'deep'))
    elif base.startswith('Wwr'): L.append(('debris',))
    elif base.startswith('W'): L.append(('cloud', 'plasma'))
    elif b0 == 'S': L.append(('cloud', 'ion'))
    elif b0 == 'H': L.append(('rocks', 'hills'))
    elif b0 == 'M': L.append(('rocks', 'wall' if ov == 'Xm' else 'mount'))
    elif b0 == 'T': L.append(('cloud', 'anom'))
    elif b0 == 'D': L.append(('cloud', 'dust'))
    elif b0 == 'A': L.append(('ice',))
    elif base.startswith('Rr'): L.append(('beacon',))
    elif b0 in 'CK':
        if base[1:2] == 'h' and base.endswith('w'): L.append(('cloud', 'plasma'))
        L.append(('station', 'keep' if b0 == 'K' else 'castle', 'r' in base[1:]))
    if ov.startswith('F'):
        k = 'pine' if ov.startswith('Fp') else 'great' if ov.startswith('Fe') else 'tropical' if ov.startswith('Ft') else 'snow' if ov.endswith('a') else 'mixed'
        L.append(('neb', k))
    elif ov.startswith('T') or ov.startswith('Uf'): L.append(('cloud', 'anom'))
    elif ov.startswith('V'):
        k = 'ocean' if base[:1] in 'SW' else 'rock' if base[:1] in 'HM' else 'desert' if base[:1] == 'D' else 'ice' if ov.endswith('a') else 'M'
        L.append(('planet', k))
    return L

SC = '/mnt/user-data/uploads/Star_Control_TC/images/terrain/sc/'
BIG = ['black-hole-big', 'red-supergiant', 'blue-giant', 'dark-star', 'protostar', 'brown-dwarf', 'globular-cluster', 'star', 'disk-star-orange', 'black-hole-small']
imp = {(x, y) for y in range(H) for x in range(W) if code(x, y).endswith('^Xm') or code(x, y)[:1] == 'X'}
centres = set(); seen = set(); k = 0
for p in sorted(imp):
    if p in seen: continue
    comp = []; st = [p]; seen.add(p)
    while st:
        q = st.pop(); comp.append(q)
        for nb in neighbours(*q):
            if nb in imp and nb not in seen: seen.add(nb); st.append(nb)
    cx = sum(q[0] for q in comp) / len(comp); cy = sum(q[1] for q in comp) / len(comp)
    best = min(comp, key=lambda q: (q[0] - cx) ** 2 + (q[1] - cy) ** 2 - 2 * sum(nb in imp for nb in neighbours(*q)))
    centres.add((best, BIG[k % len(BIG)] if len(comp) > 2 else 'black-hole-small')); k += 1
centre_of = dict(centres)

canvas = Image.new('RGBA', (W * 54 + 18, H * 72 + 36), (0, 0, 0, 255))
stars = [starfield(i) for i in range(8)]
cache = {}
def get(key, fn):
    if key not in cache: cache[key] = fn()
    return cache[key]

layers = {k: [] for k in ['cloud', 'rocks', 'neb', 'station', 'planet', 'fx']}
for y in range(H):
    for x in range(W):
        c = code(x, y); px, py = pix(x, y); L = classify(c)
        if L and L[0][0] == 'void': continue
        canvas.alpha_composite(stars[(x * 7 + y * 13) % 8], (px, py))
        v = (x * 31 + y * 17) % 4
        for item in L:
            t = item[0]
            if t == 'cloud':
                pal = {'ion': ION, 'plasma': PLASMA, 'deep': DEEP, 'anom': ANOM, 'dust': DUST, 'eddy': PLASMA}[item[1]]
                dens = {'eddy': 0.9, 'deep': 2.2, 'plasma': 1.7}.get(item[1], 1.0)
                im = get(('cl', item[1], v), lambda: cloud(200 + v * 11 + hash(item[1]) % 97, 170, pal, 36, dens, wisp=item[1] in ('plasma', 'eddy', 'deep')))
                layers['cloud'].append((im, px + 36 - 85, py + 36 - 85))
                if item[1] == 'ion':
                    layers['fx'].append((get(('lt', v), lambda: lightning(v, 72)), px, py))
            elif t == 'neb':
                im = get(('neb', item[1], v), lambda: cloud(500 + v * 13 + len(item[1]), 190, NEB[item[1]], 40, 1.0))
                layers['neb'].append((im, px + 36 - 95, py + 36 - 95))
            elif t == 'rocks' and (x, y) in centre_of:
                im = get(('sc', centre_of[(x, y)]), lambda: Image.open(SC + centre_of[(x, y)] + '.png').convert('RGBA'))
                layers['planet'].append((im, px + 36 - im.width // 2, py + 36 - im.height // 2))
            elif t == 'rocks':
                r = random.Random(x * 1000 + y)
                spec = {'hills': (6, 3, 6.5), 'mount': (4, 9, 14), 'wall': (3, 15, 21)}[item[1]]
                for i in range(spec[0]):
                    R = r.uniform(spec[1], spec[2]); sd = r.randrange(40)
                    im = get(('rock', int(R), sd), lambda: rock(sd, R))
                    ox = r.uniform(-20, 20) if item[1] != 'wall' else r.uniform(-8, 8); oy = r.uniform(-18, 18) if item[1] != 'wall' else r.uniform(-8, 8)
                    layers['rocks'].append((im, int(px + 36 + ox - im.width / 2), int(py + 36 + oy - im.height / 2)))
            elif t == 'planet':
                im = get(('pl', item[1], v), lambda: planet(900 + v * 7 + len(item[1]), 23, item[1]))
                layers['planet'].append((im, px + 36 - im.width // 2, py + 36 - im.height // 2))
            elif t == 'station':
                for dI, (nx, ny) in enumerate(neighbours(x, y)):
                    if code(nx, ny)[:1] in 'CK':
                        layers['station'].append((get(('st', dI), lambda: strut(dI)), px, py))
                layers['station'].append((get(('stn', item[1], item[2]), lambda: station(item[1], item[2], x)), px, py))
            elif t == 'beacon':
                layers['fx'].append((get('bc', beacon), px, py))
            elif t == 'ice':
                pass
            elif t == 'debris':
                pass

for k in ['cloud', 'rocks', 'neb', 'station', 'planet', 'fx']:
    for im, ax, ay in layers[k]:
        canvas.alpha_composite(im, (int(ax), int(ay)))
canvas = canvas.convert('RGB')
canvas.save(OUT)
print(canvas.size)
