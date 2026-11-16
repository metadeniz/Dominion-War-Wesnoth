"""Shrink a 288px render to the 72px game sprite.
pop=True keeps the lights where they are but stops the shrink from washing them out: in each 4x4 block, pixels that are
already strongly red/orange or blue/cyan in the big render are averaged and mixed back in, weighted by how much of the
block they cover (x K). No pixel without red or blue in the big render is coloured."""
import numpy as np
from PIL import Image
def _hsv(a):
    r, g, b = a[..., 0], a[..., 1], a[..., 2]; mx = a[..., :3].max(-1); mn = a[..., :3].min(-1); d = mx - mn + 1e-6
    h = np.where(mx == r, ((g - b) / d) % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4)) * 60
    return h, d / (mx + 1e-6), mx
def light_mask(a):
    h, s, v = _hsv(a)
    redish = ((h < 35) | (h > 340)) & (s > 0.45) & (v > 0.45)
    blueish = (h > 180) & (h < 245) & (s > 0.4) & (v > 0.45)
    return (redish | blueish) & (a[..., 3] > 0.5)
def make72(im, pop=False, K=4.0, sat=1.25, n=None):
    im = im.convert('RGBA'); n = n or im.size[0] // 4; small = im.resize((n, n), Image.LANCZOS)
    if not pop: return small
    a = np.asarray(im).astype(np.float32) / 255; s = np.asarray(small).astype(np.float32) / 255
    m = light_mask(a).astype(np.float32)
    f = a.shape[0] // n
    blk = lambda x: x.reshape(n, f, n, f, *x.shape[2:]).sum((1, 3))
    cov = blk(m) / (f * f); col = blk(a[..., :3] * m[..., None]) / np.maximum(blk(m), 1e-6)[..., None]
    mx = col.max(-1, keepdims=True); mn = col.min(-1, keepdims=True)
    col = np.clip(mx - (mx - col) * sat, 0, 1)                      # a little more saturated, same hue
    col = col / np.maximum(mx, 1e-6) * np.maximum(mx, 0.92)         # and bright
    w = np.clip(cov * K, 0, 1)[..., None]
    out = s.copy(); out[..., :3] = s[..., :3] * (1 - w) + col * w
    return Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8), 'RGBA')
