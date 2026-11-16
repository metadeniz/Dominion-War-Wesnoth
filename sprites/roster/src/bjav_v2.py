"""Version 2 of the Bajoran assault vessel: the same visual hull as visualhull.py, built finer and less blurred so edges
stay crisp, and textured instead of vertex-coloured: each face takes the top, underside or side reference view as a
texture (projected straight on), recoloured bronze like recolor_vc.py, with a bump map from the views' panel detail.
Usage: python3 -I bjav_v2.py ref.jpg OUTDIR [step=2.0] [blur=1]
Writes OUTDIR/bj-assault-v2.obj/.mtl and its textures. Axes: +X forward (nose), +Y up, Z lateral. Units = reference px.
"""
import sys, numpy as np
from PIL import Image

import os
REF, OUTDIR = sys.argv[1], sys.argv[2]; os.makedirs(OUTDIR, exist_ok=True)
STEP = float(sys.argv[3]) if len(sys.argv) > 3 else 2.0; BLUR = int(sys.argv[4]) if len(sys.argv) > 4 else 1
im = np.asarray(Image.open(REF).convert('RGB')).astype(np.float32)
H, W, _ = im.shape
fg = im.min(2) < 238
# the rear view's wingtips reach down into the top/underside rectangles; blank them
fg[300:545, 864:1000] = False; fg[300:545, 1900:] = False

def filled(r0, r1, c0, c1):
    """Foreground mask of a sub-rectangle with interior holes filled (background = connected to border)."""
    m = fg[r0:r1, c0:c1].copy()
    bg = np.zeros_like(m); bg[0, :] = ~m[0, :]; bg[-1, :] = ~m[-1, :]; bg[:, 0] = ~m[:, 0]; bg[:, -1] = ~m[:, -1]
    free = ~m
    while True:
        g = bg.copy()
        g[1:] |= bg[:-1]; g[:-1] |= bg[1:]; g[:, 1:] |= bg[:, :-1]; g[:, :-1] |= bg[:, 1:]
        g &= free
        if (g == bg).all(): break
        bg = g
    return ~bg

# view rectangles (rows, cols) in the reference sheet
TOP = (500, 1790, 38, 878)      # nose at right
BOT = (500, 1790, 940, 1790)    # underside, nose at right
SIDE = (48, 292, 38, 864)       # nose at right
FRONT = (48, 292, 864, 2155)

def bbox(m):
    ys = np.where(m.any(1))[0]; xs = np.where(m.any(0))[0]
    return ys.min(), ys.max(), xs.min(), xs.max()

mt = filled(*TOP); mb = filled(*BOT); ms = filled(*SIDE); mf = filled(*FRONT)
t = bbox(mt); b = bbox(mb); s = bbox(ms); f = bbox(mf)
L = t[3] - t[2]                       # length in px (top view)
span = t[1] - t[0]
print('top', t, 'bot', b, 'side', s, 'front', f, 'L', L, 'span', span)
zc_t = (t[0] + t[1]) / 2; zc_b = (b[0] + b[1]) / 2; zc_f = (f[2] + f[3]) / 2
ks = (s[3] - s[2]) / L                # side-view length scale relative to top
kf = (f[3] - f[2]) / span             # front-view span scale relative to top
base = max(s[1], f[1])                # common bottom row of side and front views (same baseline)
Ytop = base - min(s[0], f[0])
print('ks', ks, 'kf', kf, 'height', Ytop)

st = STEP
X = np.arange(-6, L + 6, st); Z = np.arange(-span / 2 - 6, span / 2 + 6, st); Y = np.arange(-6, Ytop + 6, st)

def samp(m, rows, cols):
    rows = np.rint(rows).astype(int); cols = np.rint(cols).astype(int)
    ok = (rows >= 0) & (rows < m.shape[0]) & (cols >= 0) & (cols < m.shape[1])
    out = np.zeros(np.broadcast(rows, cols).shape, bool)
    rr = np.clip(rows, 0, m.shape[0] - 1); cc = np.clip(cols, 0, m.shape[1] - 1)
    out = m[rr, cc] & ok
    return out

# silhouettes on the grid
topXZ = samp(mt, (zc_t + Z)[None, :], (t[2] + X)[:, None])                      # (nx, nz)
sideXY = samp(ms, (base - Y)[None, :] - SIDE[0] + SIDE[0], (s[2] + X * ks)[:, None])  # (nx, ny)
frontZY = samp(mf, (base - Y)[None, :], (zc_f + Z * kf)[:, None])                 # (nz, ny)
# note: mask coords are local to their rectangles
occ = topXZ[:, None, :] & sideXY[:, :, None] & frontZY.T[None, :, :]
print('voxels', occ.sum(), occ.shape)

F = occ.astype(np.float32)
for ax in range(3):
    for _ in range(BLUR):
        F = 0.25 * np.roll(F, 1, ax) + 0.5 * F + 0.25 * np.roll(F, -1, ax)
F = np.pad(F, 1)
nx, ny, nz = F.shape
iso = 0.5
inside = F > iso

# --- surface nets ---
cell_sum = np.zeros((nx - 1, ny - 1, nz - 1, 3), np.float64)
cell_cnt = np.zeros((nx - 1, ny - 1, nz - 1), np.int32)
edges = []
for ax in range(3):
    sl0 = [slice(None)] * 3; sl1 = [slice(None)] * 3
    sl0[ax] = slice(0, -1); sl1[ax] = slice(1, None)
    a = F[tuple(sl0)]; bb = F[tuple(sl1)]
    cross = (a > iso) != (bb > iso)
    idx = np.argwhere(cross)
    tt = (iso - a[cross]) / (bb[cross] - a[cross])
    p = idx.astype(np.float64); p[:, ax] += tt
    others = [o for o in range(3) if o != ax]
    for d1 in (0, 1):
        for d2 in (0, 1):
            c = idx.copy(); c[:, others[0]] -= d1; c[:, others[1]] -= d2
            ok = (c >= 0).all(1) & (c[:, 0] < nx - 1) & (c[:, 1] < ny - 1) & (c[:, 2] < nz - 1)
            np.add.at(cell_sum, (c[ok, 0], c[ok, 1], c[ok, 2]), p[ok])
            np.add.at(cell_cnt, (c[ok, 0], c[ok, 1], c[ok, 2]), 1)
    sign = (a[cross] > iso)
    edges.append((ax, idx, sign))
active = cell_cnt > 0
vid = -np.ones(cell_cnt.shape, np.int64); vid[active] = np.arange(active.sum())
V = cell_sum[active] / cell_cnt[active][:, None]
faces = []
for ax, idx, sign in edges:
    o1, o2 = [o for o in range(3) if o != ax]
    def cell(d1, d2):
        c = idx.copy(); c[:, o1] -= d1; c[:, o2] -= d2; return c
    cs = [cell(0, 0), cell(1, 0), cell(1, 1), cell(0, 1)]
    ok = np.ones(len(idx), bool)
    for c in cs:
        ok &= (c >= 0).all(1) & (c[:, 0] < nx - 1) & (c[:, 1] < ny - 1) & (c[:, 2] < nz - 1)
    q = np.stack([vid[c[ok, 0], c[ok, 1], c[ok, 2]] for c in cs], 1)
    sg = sign[ok]
    flip = (ax == 1)  # keep consistent winding per axis
    q[sg ^ flip] = q[sg ^ flip][:, ::-1]
    faces.append(q)
Q = np.concatenate(faces)
Q = Q[(Q >= 0).all(1)]
T = np.concatenate([Q[:, [0, 1, 2]], Q[:, [0, 2, 3]]])
# grid -> world (px units): index i corresponds to X[i-1] because of the pad
Pw = np.stack([X[0] + (V[:, 0] - 1) * st, Y[0] + (V[:, 1] - 1) * st, Z[0] + (V[:, 2] - 1) * st], 1)
# orient outward: make winding agree with gradient direction
fn = np.cross(Pw[T[:, 1]] - Pw[T[:, 0]], Pw[T[:, 2]] - Pw[T[:, 0]])
cen = Pw[T].mean(1)
gi = np.clip(((cen - [X[0], Y[0], Z[0]]) / st + 1).round().astype(int), 0, np.array(F.shape) - 1)
gx = np.gradient(F, axis=0)[gi[:, 0], gi[:, 1], gi[:, 2]]; gy = np.gradient(F, axis=1)[gi[:, 0], gi[:, 1], gi[:, 2]]; gz = np.gradient(F, axis=2)[gi[:, 0], gi[:, 1], gi[:, 2]]
outward = -np.stack([gx, gy, gz], 1)
bad = (fn * outward).sum(1) < 0
T[bad] = T[bad][:, ::-1]
fn = np.cross(Pw[T[:, 1]] - Pw[T[:, 0]], Pw[T[:, 2]] - Pw[T[:, 0]])
N = np.zeros_like(Pw)
for k in range(3): np.add.at(N, T[:, k], fn)
N /= np.linalg.norm(N, axis=1, keepdims=True) + 1e-9
print('verts', len(Pw), 'tris', len(T))

# --- recesses: the black canopy and the reddish vent panels seen in the top view are sunk into the hull ---
from PIL import ImageFilter
ta = im[TOP[0]:TOP[1], TOP[2]:TOP[3]] / 255.0
canopy = (ta.max(2) < 0.25) & mt
vent = (np.clip((ta[..., 0] - (ta[..., 1] + ta[..., 2]) / 2 - 0.05) / 0.10, 0, 1) > 0.5) & mt
CAN_D = float(os.environ.get('CAN_D', 5)); VENT_D = float(os.environ.get('VENT_D', 1.5))
dep = canopy * CAN_D + vent * VENT_D
dep = np.asarray(Image.fromarray((dep / max(CAN_D, VENT_D) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2)), np.float32) / 255 * max(CAN_D, VENT_D)
rr = np.clip(np.rint(zc_t + Pw[:, 2]).astype(int), 0, dep.shape[0] - 1); cc = np.clip(np.rint(t[2] + Pw[:, 0]).astype(int), 0, dep.shape[1] - 1)
up = np.clip((N[:, 1] - 0.4) / 0.3, 0, 1)
Pw[:, 1] -= dep[rr, cc] * up
print('recessed verts', int((dep[rr, cc] * up > 0.5).sum()), 'canopy px', int(canopy.sum()), 'vent px', int(vent.sum()))
fn = np.cross(Pw[T[:, 1]] - Pw[T[:, 0]], Pw[T[:, 2]] - Pw[T[:, 0]])
N = np.zeros_like(Pw)
for k in range(3): np.add.at(N, T[:, k], fn)
N /= np.linalg.norm(N, axis=1, keepdims=True) + 1e-9

# --- textures ---
from PIL import ImageFilter
BASE = np.array([0x8c, 0x66, 0x50]) / 255; MARK = np.array([0x5c, 0x2e, 0x24]) / 255; K = 1.8   # as bj-assault-bronze.obj
def crop(rect, m):
    r0, r1, c0, c1 = rect; a = im[r0:r1, c0:c1] / 255.0; mm = m & (a.min(2) < 238 / 255)
    return a, mm
crops = {'top': crop(TOP, mt), 'bot': crop(BOT, mb), 'side': crop(SIDE, ms)}
allpx = np.concatenate([a[mm] for a, mm in crops.values()]); lum_mean = allpx.mean(1).mean()
def bronze(a, mm):
    lum = a.mean(2); rel = (lum / lum_mean) ** K
    red = np.clip((a[..., 0] - (a[..., 1] + a[..., 2]) / 2 - 0.05) / 0.10, 0, 1)[..., None]
    out = np.clip((BASE * (1 - red) + MARK * red) * rel[..., None], 0, 1)
    # grow the colours past the outline so texture edges never pick up the white background
    filled = mm.copy(); out[~filled] = 0
    for _ in range(12):
        acc = np.zeros_like(out); cnt = np.zeros(filled.shape)
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            sh = np.roll(np.roll(out * filled[..., None], dy, 0), dx, 1); sf = np.roll(np.roll(filled, dy, 0), dx, 1)
            acc += sh; cnt += sf
        new = (~filled) & (cnt > 0); out[new] = acc[new] / cnt[new][:, None]; filled = filled | new
    out[~filled] = BASE
    return out
def bump(a, mm):
    lum = Image.fromarray((a.mean(2) * 255).astype(np.uint8)); bl = np.asarray(lum.filter(ImageFilter.GaussianBlur(5)), np.float32)
    d = np.asarray(lum, np.float32) - bl; d[~mm] = 0; d = np.clip(128 + d * 2.2, 0, 255)
    return Image.fromarray(d.astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.6))
for k, (a, mm) in crops.items():
    Image.fromarray((bronze(a, mm) * 255 + 0.5).astype(np.uint8)).save(os.path.join(OUTDIR, f'bjv2_{k}.png'))
    bump(a, mm).save(os.path.join(OUTDIR, f'bjv2_{k}_bump.png'))
# planar UVs, one set per view (texture pixel = the reference pixel the colour came from)
def uv(rect, rows, cols):
    r0, r1, c0, c1 = rect; return np.stack([cols / (c1 - c0), 1 - rows / (r1 - r0)], 1)
UVT = uv(TOP, zc_t + Pw[:, 2], t[2] + Pw[:, 0])
UVB = uv(BOT, zc_b - Pw[:, 2], b[2] + Pw[:, 0])
UVS = uv(SIDE, base - Pw[:, 1], s[2] + Pw[:, 0] * ks)
fnu = fn / (np.linalg.norm(fn, axis=1, keepdims=True) + 1e-9)
grp = np.where(fnu[:, 1] > 0.3, 0, np.where(fnu[:, 1] < -0.3, 1, 2))   # 0 top, 1 underside, 2 side
nv = len(Pw)
with open(os.path.join(OUTDIR, 'bj-assault-v2.mtl'), 'w') as fo:
    for k in ('top', 'bot', 'side'):
        fo.write(f'newmtl bj_{k}\nKa 0 0 0\nKd 1 1 1\nKs 0.2 0.2 0.2\nNs 30\nillum 2\nmap_Kd bjv2_{k}.png\nbump bjv2_{k}_bump.png\n\n')
with open(os.path.join(OUTDIR, 'bj-assault-v2.obj'), 'w') as fo:
    fo.write('# Bajoran assault vessel v2: visual hull from the reference views, textured by projection (bjav_v2.py)\nmtllib bj-assault-v2.mtl\n')
    for p in Pw: fo.write('v %.2f %.2f %.2f\n' % tuple(p))
    for U in (UVT, UVB, UVS):
        for q in U: fo.write('vt %.5f %.5f\n' % tuple(q))
    for n in N: fo.write('vn %.4f %.4f %.4f\n' % tuple(n))
    for g, k in enumerate(('top', 'bot', 'side')):
        fo.write(f'usemtl bj_{k}\n'); off = g * nv
        for a, b2, c in T[grp == g] + 1: fo.write('f %d/%d/%d %d/%d/%d %d/%d/%d\n' % (a, a + off, a, b2, b2 + off, b2, c, c + off, c))
print('wrote', OUTDIR, 'tris per group', [(grp == g).sum() for g in range(3)])
