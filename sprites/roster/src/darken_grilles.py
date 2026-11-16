"""Darken the two ribbed grilles behind the head of the TTS bird-of-prey texture so they stand out from the wings.
The grilles are drawn as two mirrored shapes (box with a curved inner edge), measured from the texture, then darkened.
Usage: python3 -I darken_grilles.py in.png out.png [factor]"""
import sys, numpy as np
from PIL import Image
a = np.asarray(Image.open(sys.argv[1]).convert('RGB')).astype(np.float32); K = float(sys.argv[3]) if len(sys.argv) > 3 else 0.5
H, W = a.shape[:2]; Y, X = np.mgrid[0:H, 0:W].astype(np.float32)
X0, X1, TOP, CY = 135, 237, 185, 304.0          # grille box (upper grille) and the ship's centre line
t = np.clip((X - X0) / (X1 - X0), 0, 1)
bottom = 283 - 13 * t ** 2                        # inner edge curves where the head meets the grille
up = (X >= X0) & (X <= X1) & (Y >= TOP) & (Y <= bottom)
Ym = 2 * CY - Y                                   # mirror for the lower grille
lo = (X >= X0 - 2) & (X <= X1 - 4) & (Ym >= TOP) & (Ym <= bottom)
m = (up | lo).astype(np.float32)
def box(img, r):
    c = np.cumsum(np.cumsum(np.pad(img, ((r + 1, r), (r + 1, r))), 0), 1)
    return (c[2*r+1:, 2*r+1:] - c[:-2*r-1, 2*r+1:] - c[2*r+1:, :-2*r-1] + c[:-2*r-1, :-2*r-1]) / (2*r+1)**2
w = box(m, 2)[..., None]
out = a * (1 - w) + a * K * w
Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).save(sys.argv[2])
print('grille px', int(m.sum()))
