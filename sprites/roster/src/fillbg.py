"""Replace the white background around a projected texture (e.g. a top-view schematic) with the hull colour,
so faces whose UVs fall just outside the drawn ship are not white. Flood fill from the borders over near-white pixels.
Usage: python3 -I fillbg.py IN OUT [threshold]"""
import sys
import numpy as np
from PIL import Image
from collections import deque
src, out = sys.argv[1], sys.argv[2]; th = int(sys.argv[3]) if len(sys.argv) > 3 else 225
a = np.asarray(Image.open(src).convert('RGB')).copy(); h, w, _ = a.shape
white = (a.min(-1) >= th)
seen = np.zeros((h, w), bool); q = deque()
for x in range(w):
    for y in (0, h - 1):
        if white[y, x] and not seen[y, x]: seen[y, x] = True; q.append((y, x))
for y in range(h):
    for x in (0, w - 1):
        if white[y, x] and not seen[y, x]: seen[y, x] = True; q.append((y, x))
while q:
    y, x = q.popleft()
    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        yy, xx = y + dy, x + dx
        if 0 <= yy < h and 0 <= xx < w and white[yy, xx] and not seen[yy, xx]: seen[yy, xx] = True; q.append((yy, xx))
hull = np.median(a[~seen & ~white], 0).astype(np.uint8)
a[seen] = hull
# also grow the hull colour one ring into the anti-aliased edge
Image.fromarray(a).save(out, quality=95); print(src.split('/')[-1], 'filled', round(seen.mean() * 100, 1), '% with', hull)
