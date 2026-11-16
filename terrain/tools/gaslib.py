# Periodic ("tileable") gas textures for the space terrain.
#
# Wesnoth draws gas the way the Star Control add-on does: every gas family is one big texture that
# repeats every PX x PY hexes, and each hex shows the piece of it at its own place on the map
# (terrain_graphics rules with mod_x / mod_y). Neighbouring hexes of the same gas therefore join
# without seams. The noise here wraps around at the texture's edges so the repeat is seamless too.
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy.ndimage import map_coordinates, gaussian_filter

PX, PY = 4, 4                  # repeat: 4 hexes across, 4 down (PX must be even: odd columns sit 36px lower)
TW, TH = PX * 54, PY * 72      # texture size in pixels: 216 x 288
HEXV = [(18, 0), (54, 0), (72, 36), (54, 72), (18, 72), (0, 36)]

def hex_alpha(size=72):
    """Wesnoth's own hex mask (hard-edged), so neighbouring hexes meet without hairline gaps."""
    import os
    m = Image.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'hexmask.png')).convert('RGBA')
    return np.asarray(m, np.float32)[..., 3] / 255

HEXA = hex_alpha()

def piece_origin(mx, my):
    """Top-left pixel, inside the texture, of the hex at (mx, my) of the repeat (0-based, odd mx 36px lower)."""
    return mx * 54, my * 72 + (36 if mx % 2 else 0)

def pfbm(cells_x, cells_y, octaves, rng, persist=0.5):
    """Wrapping fractal noise over the whole texture; cells_* = lattice cells across the period."""
    out = np.zeros((TH, TW), np.float32); amp = 1.0; tot = 0
    yy, xx = np.mgrid[0:TH, 0:TW].astype(np.float32)
    for o in range(octaves):
        cx, cy = cells_x * 2 ** o, cells_y * 2 ** o
        g = rng.standard_normal((cy, cx)).astype(np.float32)
        out += amp * map_coordinates(g, [yy / TH * cy, xx / TW * cx], order=3, mode='grid-wrap'); tot += amp; amp *= persist
    out /= tot
    return (out - out.mean()) / (out.std() + 1e-6)

def pflow(rng, cells=2, drift=(1.0, 0.35), swirl=0.7):
    psi = pfbm(cells, cells, 3, rng)
    vx = (np.roll(psi, -1, 0) - np.roll(psi, 1, 0)) / 2; vy = -(np.roll(psi, -1, 1) - np.roll(psi, 1, 1)) / 2
    m = np.sqrt(vx * vx + vy * vy).mean() + 1e-6
    vx = swirl * vx / m + drift[0]; vy = swirl * vy / m + drift[1]
    n = np.maximum(np.sqrt(vx * vx + vy * vy), 1e-6)
    return vx / n, vy / n

def psmear(noise, vx, vy, length, step=1.5):
    """Smear noise along the flow (line integral convolution), wrapping at the edges."""
    y0, x0 = np.mgrid[0:TH, 0:TW].astype(np.float32)
    acc = noise.copy(); ws = np.ones_like(noise)
    for sign in (1, -1):
        x, y = x0.copy(), y0.copy()
        for i in range(length):
            cx = map_coordinates(vx, [y, x], order=1, mode='grid-wrap'); cy = map_coordinates(vy, [y, x], order=1, mode='grid-wrap')
            x = x + sign * step * cx; y = y + sign * step * cy
            wgt = 0.5 * (1 + math.cos(math.pi * (i + 1) / (length + 1)))
            acc += wgt * map_coordinates(noise, [y, x], order=1, mode='grid-wrap'); ws += wgt
    out = acc / ws
    return (out - out.mean()) / (out.std() + 1e-6)

def ramp(t, stops):
    t = np.clip(t, 0, 1); out = np.zeros(t.shape + (3,), np.float32)
    xs = [s[0] for s in stops]
    for k in range(3): out[..., k] = np.interp(t, xs, [s[1][k] for s in stops])
    return out

def rgba(rgb, a):
    return np.dstack([np.clip(rgb, 0, 255), np.clip(a, 0, 1) * 255]).astype(np.uint8)

def wrap_blur(a, sigma):
    return gaussian_filter(a, sigma, mode='wrap')

def cut(tex, mx, my):
    """The 72x72 piece of a wrapping RGBA texture for the hex at (mx, my), cut to the hex shape."""
    ox, oy = piece_origin(mx, my)
    ys = (np.arange(72) + oy) % TH; xs = (np.arange(72) + ox) % TW
    p = tex[np.ix_(ys, xs)].astype(np.float32)
    p[..., 3] *= HEXA
    return Image.fromarray(p.astype(np.uint8), 'RGBA')

# ---- spill masks: gas reaching into a neighbouring hex from one side ----
# Direction d = side of the *receiving* hex that faces the gas: 0=N 1=NE 2=SE 3=S 4=SW 5=NW.
EDGES = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 0)]
DIRS = ['n', 'ne', 'se', 's', 'sw', 'nw']

def spill_mask(d, reach=30.0, strength=0.9):
    (ax, ay), (bx, by) = HEXV[EDGES[d][0]], HEXV[EDGES[d][1]]
    yy, xx = np.mgrid[0:72, 0:72].astype(np.float32) + 0.5
    ex, ey = bx - ax, by - ay; L = math.hypot(ex, ey)
    nx, ny = -ey / L, ex / L                       # inward normal
    if (36 - ax) * nx + (36 - ay) * ny < 0: nx, ny = -nx, -ny
    dist = (xx - ax) * nx + (yy - ay) * ny         # distance from that side, into the hex
    t = np.clip(1 - dist / reach, 0, 1); t = t * t * (3 - 2 * t)
    a = strength * t * HEXA
    out = np.zeros((72, 72, 4), np.uint8); out[..., :3] = 255; out[..., 3] = (a * 255).astype(np.uint8)
    return Image.fromarray(out, 'RGBA')

# neighbour of (mx, my) in direction d, in Wesnoth's 0-based map coordinates (odd x columns lower)
def neighbour(mx, my, d):
    odd = mx % 2 == 1
    return {0: (mx, my - 1), 1: (mx + 1, my if odd else my - 1), 2: (mx + 1, my + 1 if odd else my),
            3: (mx, my + 1), 4: (mx - 1, my + 1 if odd else my), 5: (mx - 1, my if odd else my - 1)}[d]
