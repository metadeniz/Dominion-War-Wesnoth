"""Repaint the Constellation texture for the captured (Maquis) version: tint the hull, keep the nacelle glow blue.
Usage: python3 -I const_cap.py in.png out_base.png out_emissive.png TINT_HEX BRIGHT
The hull is multiplied by the tint in sRGB (so it stays light), times BRIGHT; pixels of the blue warp-grille glow
are left untinted, saturated toward Federation blue, and also written to the emissive map."""
import sys, numpy as np
from PIL import Image, ImageFilter
src, ob, oe, tint, bright = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], float(sys.argv[5])
a = np.asarray(Image.open(src).convert('RGB')).astype(np.float32)
r, g, b = a[..., 0], a[..., 1], a[..., 2]
glow = np.clip((b - np.maximum(r, g * 0.85) - 18) / 40, 0, 1) * np.clip((b - 110) / 60, 0, 1)
glow = np.asarray(Image.fromarray((glow * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2))).astype(np.float32) / 255
t = np.array([int(tint[i:i+2], 16) for i in (1, 3, 5)], np.float32) / 255
hull = np.clip(a * t * bright, 0, 255)
FED = np.array([70, 150, 255], np.float32)
lum = (a.max(2, keepdims=True) / 255)
blue = np.clip(FED * (0.55 + 0.6 * lum), 0, 255)
out = hull * (1 - glow[..., None]) + blue * glow[..., None]
Image.fromarray(out.astype(np.uint8)).save(ob)
Image.fromarray((blue * glow[..., None]).astype(np.uint8)).save(oe)
print('glow texels', int((glow > 0.5).sum()))
