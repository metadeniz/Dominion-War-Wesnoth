# Composite one-light-at-a-time passes (passes.js) into any light mix, in linear light. Import from other tools.
# mix = {pass_name: intensity, ...}; passes were rendered at intensity PI_ (1.5); 'E' (emissive) and 'SH' (ground shadow) are added automatically.
import os, numpy as np
from PIL import Image
PI_ = 1.5
_cache = {}
def s2l(x): return np.where(x <= 0.04045, x / 12.92, ((x + 0.055) / 1.055) ** 2.4)
def l2s(x): x = np.clip(x, 0, 1); return np.where(x <= 0.0031308, x * 12.92, 1.055 * x ** (1 / 2.4) - 0.055)
def load(d, uid, name):
    k = (d, uid, name)
    if k not in _cache:
        a = np.asarray(Image.open(os.path.join(d, uid, name + '.png')).convert('RGBA')).astype(np.float32) / 255
        _cache[k] = (s2l(a[..., :3]), a[..., 3])
    return _cache[k]
def compose(d, uid, mix, emis=1.0, shadow=True):
    E, alpha = load(d, uid, 'E'); lin = E * emis
    for n, k in mix.items():
        if k == 0: continue
        P, _ = load(d, uid, n); lin = lin + (k / (1.0 if n in ('H', 'A') else PI_)) * np.maximum(P - E, 0)
    rgb = l2s(lin)
    if shadow:
        S = np.asarray(Image.open(os.path.join(d, uid, 'SH.png')).convert('RGBA')).astype(np.float32) / 255
        a = alpha[..., None]; out_a = alpha + S[..., 3] * (1 - alpha)
        out = (rgb * a + S[..., :3] * S[..., 3:4] * (1 - a)) / np.maximum(out_a[..., None], 1e-6)
    else: out, out_a = rgb, alpha
    return Image.fromarray((np.dstack([out, out_a]) * 255 + 0.5).clip(0, 255).astype(np.uint8), 'RGBA')
