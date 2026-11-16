import numpy as np
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

