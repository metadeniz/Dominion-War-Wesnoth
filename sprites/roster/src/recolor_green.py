"""Repaint the TTS bird-of-prey texture in the bright green K'Vort scheme D supplied (studio photo of a model).
Each pixel's brightness is mapped onto a green ramp sampled from that photo, so panel lines and grilles keep their detail.
Strongly red/orange pixels (emblem, lights) are kept as they are.
Usage: python3 -I recolor_green.py in.png out.png"""
import sys, numpy as np
from PIL import Image
a = np.asarray(Image.open(sys.argv[1]).convert('RGB')).astype(np.float32)
lum = a.mean(2)
pts = np.array([0, 18, 38, 61, 85, 110, 255], np.float32)
ramp = np.array([[12, 16, 12], [30, 40, 24], [62, 76, 38], [92, 130, 66], [108, 148, 80], [128, 164, 98], [200, 222, 180]], np.float32)
out = np.stack([np.interp(lum, pts, ramp[:, c]) for c in range(3)], -1)
mx = a.max(2); mn = a.min(2); sat = (mx - mn) / np.maximum(mx, 1)
keep = (a[..., 0] > a[..., 1] + 35) & (a[..., 0] > a[..., 2] + 35) & (sat > 0.45) & (a[..., 0] > 90)
out[keep] = a[keep]
print('kept red/orange px', int(keep.sum()), 'of', keep.size)
Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).save(sys.argv[2])
