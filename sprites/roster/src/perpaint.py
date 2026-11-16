"""Transfer the original Peregrine's wing paint and lights onto the octave767 Peregrine's UV atlas.
Usage: python3 -I perpaint.py BAKEDIR TEXDIR OUTBASE OUTILLUM [wingmix] [glow]
BAKEDIR holds oldTop.png/oldBot.png (old model projected top/bottom, bbox-normalized) and uv0/uv1.png (new model's
UV-space position/normal bake, see bake.html). Both models are Y-up, nose +Z, so normalized (x, z) line up.
"""
import sys, numpy as np
from PIL import Image
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from uvdecode import decode

BAKE, TEX, OUTB, OUTI = sys.argv[1:5]
WINGMIX = float(sys.argv[5]) if len(sys.argv) > 5 else 0.85
GLOW = float(sys.argv[6]) if len(sys.argv) > 6 else 1.0

def grow(img, mask, it):
    """Fill pixels outside mask with the mean of masked neighbours, it times (dilation of colours)."""
    img = img.astype(np.float32).copy(); mask = mask.copy()
    for _ in range(it):
        acc = np.zeros_like(img); cnt = np.zeros(mask.shape, np.float32)
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            m = np.roll(mask, (dy, dx), (0, 1)); acc += np.roll(img * mask[..., None], (dy, dx), (0, 1)); cnt += m
        new = (~mask) & (cnt > 0)
        img[new] = acc[new] / cnt[new][:, None]; mask = mask | new
    return img, mask

def bilinear(img, u, v):
    """img HxWx3 float, u,v in [0,1] (u = column, v = row)."""
    H, W = img.shape[:2]
    fx = np.clip(u * W - 0.5, 0, W - 1.001); fy = np.clip(v * H - 0.5, 0, H - 1.001)
    x0 = fx.astype(int); y0 = fy.astype(int); ax = (fx - x0)[:, None]; ay = (fy - y0)[:, None]
    return (img[y0, x0] * (1 - ax) * (1 - ay) + img[y0, x0 + 1] * ax * (1 - ay) +
            img[y0 + 1, x0] * (1 - ax) * ay + img[y0 + 1, x0 + 1] * ax * ay)

def load_proj(p):
    a = np.asarray(Image.open(p).convert('RGB')).astype(np.float32)
    bg = (a[..., 0] > 200) & (a[..., 1] < 60) & (a[..., 2] > 200)
    a, _ = grow(a, ~bg, 12)
    return a, bg

top, topbg = load_proj(BAKE + '/oldTop.png'); bot, botbg = load_proj(BAKE + '/oldBot.png')
cov, x, y, z, ny = decode(BAKE)

base0 = np.asarray(Image.open(TEX + '/peregrine_base.png').convert('RGBA')).astype(np.float32)
alpha = base0[..., 3:]
base = np.clip(base0[..., :3] * 1.3, 0, 255)          # the +30% the user approved
illum = np.asarray(Image.open(TEX + '/peregrine_illum.png').convert('RGB')).astype(np.float32)

# projection coords: column = x, row = 1 - z
u = x; v = 1 - z
up = cov & (ny > 0.35); dn = cov & (ny < -0.35)
lat = np.abs(x - 0.5)
wing = (lat > 0.235) & (z > 0.12) & (z < 0.86)

out = base.copy()
for sel, src in ((up & wing, top), (dn & wing, bot)):
    c = bilinear(src, u[sel], v[sel])
    w = WINGMIX * np.clip((lat[sel] - 0.235) / 0.02, 0, 1)[:, None]   # soft edge next to the nacelles
    out[sel] = base[sel] * (1 - w) + c * w

# lights from the old top view: strongly red or blue pixels become paint + glow, anywhere on top surfaces
c = bilinear(top, u[up], v[up]); r, g, b = c[:, 0], c[:, 1], c[:, 2]
red = (r > 150) & (g < 90) & (b < 90); blue = (b > 150) & (b > r + 60)
lt = np.zeros(up.sum(), np.float32); lt[red | blue] = 1
gl = np.zeros_like(illum); idx = np.argwhere(up)
li = idx[red | blue]; lc = c[red | blue]
RED = np.array([255, 28, 18], np.float32); BLUE = np.array([40, 150, 255], np.float32)
lc = np.where(red[red | blue][:, None], RED, BLUE)          # pure colours, no washed-out highlights
gl[li[:, 0], li[:, 1]] = lc
out[li[:, 0], li[:, 1]] = lc
print('wing texels', int((up & wing).sum() + (dn & wing).sum()), 'old-light texels red', int(red.sum()), 'blue', int(blue.sum()))

# boost the model's own lights: saturate, brighten, and spread 3 texels so they survive the downscale
lit = illum.max(2) > 40
val = np.clip(illum.max(2) / 255 * 2.0, 0, 1)[..., None]
isblue = (illum[..., 2] > illum[..., 0])[..., None]          # model's own lights: blue strips stay blue,
sat = np.where(isblue, BLUE, RED) * val * lit[..., None]     # red and orange lamps all become signal red
ill = np.maximum(sat, gl)
ill, m2 = grow(ill, ill.max(2) > 40, int(sys.argv[7]) if len(sys.argv) > 7 else 4)
ill = ill * m2[..., None] * GLOW
# paint the lit texels into the base too, so they read even where the glow is weak
lm = ill.max(2) > 40
out[lm] = np.clip(ill[lm], 0, 255)

# bleed edited texels 4 px past UV island borders so mipmaps don't pull grey back in
edited = np.zeros(cov.shape, bool); edited[up & wing] = True; edited[dn & wing] = True; edited |= lm
ext, em = grow(out * edited[..., None], edited, 4)
ring = em & ~edited & ~cov
out[ring] = ext[ring]

Image.fromarray(np.concatenate([np.clip(out, 0, 255), alpha], 2).astype(np.uint8), 'RGBA').save(OUTB)
Image.fromarray(np.clip(ill, 0, 255).astype(np.uint8)).save(OUTI)
print('wrote', OUTB, OUTI)
