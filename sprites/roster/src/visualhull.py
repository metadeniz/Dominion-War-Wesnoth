"""Build a smooth, vertex-coloured OBJ of a ship from orthographic reference views.
Visual hull of top/side/front silhouettes -> blur -> surface nets -> colours sampled from the views.
Usage: python3 -I visualhull.py ref.jpg out.obj
Axes of the output: +X forward (nose), +Y up, Z lateral. Units = reference pixels.
"""
import sys, numpy as np
from PIL import Image

REF, OUT = sys.argv[1], sys.argv[2]
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

st = 3.0
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
    for _ in range(2):
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

# --- colours ---
def colour(img_rect, rows, cols, m):
    r0, r1, c0, c1 = img_rect
    rr = np.clip(np.rint(rows).astype(int), 0, m.shape[0] - 1); cc = np.clip(np.rint(cols).astype(int), 0, m.shape[1] - 1)
    col = im[r0 + rr, c0 + cc]; good = m[rr, cc] & (col.min(1) < 238)
    return col, good
default = np.array([196, 204, 204], np.float32)
ct, gt = colour(TOP, zc_t + Pw[:, 2], t[2] + Pw[:, 0], mt)
cb, gb = colour(BOT, zc_b - Pw[:, 2], b[2] + Pw[:, 0], mb)
cside, gs = colour(SIDE, base - Pw[:, 1], s[2] + Pw[:, 0] * ks, ms)
for c, g in ((ct, gt), (cb, gb), (cside, gs)): c[~g] = default
wt = np.clip(N[:, 1], 0, 1) ** 2; wb = np.clip(-N[:, 1], 0, 1) ** 2; ws = N[:, 2] ** 2 * 0.6 + 0.02
C = (ct * wt[:, None] + cb * wb[:, None] + cside * ws[:, None]) / (wt + wb + ws)[:, None]
C = np.clip(C / 255.0, 0, 1)

with open(OUT, 'w') as fo:
    fo.write('# visual hull built from reference views\n')
    for p, c in zip(Pw, C): fo.write('v %.2f %.2f %.2f %.3f %.3f %.3f\n' % (p[0], p[1], p[2], c[0], c[1], c[2]))
    for n in N: fo.write('vn %.4f %.4f %.4f\n' % tuple(n))
    for a, b2, c in T + 1: fo.write('f %d//%d %d//%d %d//%d\n' % (a, a, b2, b2, c, c))
print('wrote', OUT)
