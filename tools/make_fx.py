#!/usr/bin/env python3
"""Draws the placeholder weapon effects and the crew-level badges.

    python3 tools/make_fx.py

Writes images/projectiles/dw/*.png (beam bolts, torpedoes, transporter shimmer) and
images/misc/dw-*.png (Veteran and Elite crew badges). Needs Pillow and numpy.
These are stand-ins until the final effects are picked (sprites/fx-prototypes in the library).
"""
import math
import os

import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FX = os.path.join(ROOT, "images", "projectiles", "dw")
MISC = os.path.join(ROOT, "images", "misc")

# Direction of the north-east hex neighbour (dx, dy in pixels) for a 72 px hex.
NE = (54.0, -36.0)
N = (0.0, -1.0)

BEAMS = {
    # name: (core colour, glow colour, length, width)
    "beam-phaser": ((255, 236, 200), (255, 120, 20), 56, 2.2),
    "beam-spiral": ((255, 250, 210), (255, 190, 40), 56, 2.6),
    "beam-polaron": ((235, 215, 255), (150, 60, 255), 56, 2.4),
    "beam-plasma": ((230, 255, 200), (90, 230, 40), 52, 2.6),
    "bolt-phaser": ((255, 240, 210), (255, 110, 10), 26, 3.2),
    "bolt-disruptor": ((225, 255, 215), (40, 220, 60), 30, 3.0),
    "bolt-breen": ((225, 250, 255), (60, 210, 230), 30, 3.2),
}

TORPEDOES = {
    # name: (core colour, glow colour, radius)
    "torpedo-photon": ((255, 245, 220), (255, 80, 30), 7.0),
    "torpedo-micro": ((255, 245, 220), (255, 110, 40), 4.5),
    "torpedo-quantum": ((235, 245, 255), (60, 140, 255), 7.5),
    "torpedo-klingon": ((255, 230, 220), (235, 30, 30), 7.0),
    "torpedo-cardassian": ((255, 250, 220), (255, 170, 20), 6.5),
    "torpedo-jemhadar": ((255, 255, 255), (200, 210, 235), 6.5),
    "torpedo-plasma": ((235, 255, 215), (80, 230, 40), 7.5),
    "torpedo-dampener": ((240, 250, 255), (120, 200, 255), 8.0),
}


def glow_image(size, dist, core, glow, width):
    """An RGBA image from a distance field: a hot core that fades into a coloured glow."""
    core_a = np.clip(1.0 - dist / width, 0, 1)
    glow_a = np.exp(-(dist / (width * 2.6)) ** 2)
    alpha = np.clip(core_a + glow_a * 0.85, 0, 1)
    mix = np.clip(core_a * 1.4, 0, 1)[..., None]
    rgb = np.array(core)[None, None, :] * mix + np.array(glow)[None, None, :] * (1 - mix)
    img = np.dstack([rgb, alpha[..., None] * 255]).astype(np.uint8)
    return Image.fromarray(img, "RGBA")


def segment_distance(size, direction, length):
    h = w = size
    y, x = np.mgrid[0:h, 0:w].astype(float)
    cx = cy = (size - 1) / 2.0
    dx, dy = direction
    n = math.hypot(dx, dy)
    dx, dy = dx / n, dy / n
    ax, ay = cx - dx * length / 2, cy - dy * length / 2
    px, py = x - ax, y - ay
    t = np.clip(px * dx + py * dy, 0, length)
    qx, qy = ax + t * dx, ay + t * dy
    d = np.hypot(x - qx, y - qy)
    # Taper the tail so the bolt reads as moving forward.
    taper = 0.55 + 0.45 * (t / length)
    return d / taper


def draw_beams():
    for name, (core, glow, length, width) in BEAMS.items():
        for suffix, direction in (("n", N), ("ne", NE)):
            dist = segment_distance(72, direction, length)
            glow_image(72, dist, core, glow, width).save(os.path.join(FX, f"{name}-{suffix}.png"))


def draw_torpedoes():
    size = 32
    y, x = np.mgrid[0:size, 0:size].astype(float)
    c = (size - 1) / 2.0
    for name, (core, glow, radius) in TORPEDOES.items():
        d = np.hypot(x - c, y - c)
        # Four short spikes, the classic torpedo twinkle.
        ang = np.arctan2(y - c, x - c)
        spikes = 1.0 + 0.35 * np.cos(4 * ang) ** 8
        glow_image(size, d / spikes, core, glow, radius * 0.45).save(os.path.join(FX, f"{name}.png"))


def draw_transporter():
    size = 72
    rng = np.random.default_rng(7)
    img = np.zeros((size, size, 4), float)
    y, x = np.mgrid[0:size, 0:size].astype(float)
    for _ in range(70):
        px = rng.normal(36, 9)
        py = rng.uniform(14, 58)
        r = rng.uniform(0.6, 1.6)
        d = np.hypot(x - px, y - py)
        a = np.exp(-(d / r) ** 2)
        img[..., 3] = np.maximum(img[..., 3], a)
    column = np.exp(-((x - 36) / 10) ** 2) * np.clip(1 - np.abs(y - 36) / 26, 0, 1) * 0.35
    img[..., 3] = np.clip(np.maximum(img[..., 3], column), 0, 1)
    img[..., 0] = 200
    img[..., 1] = 230
    img[..., 2] = 255
    img[..., 3] *= 255
    Image.fromarray(img.astype(np.uint8), "RGBA").save(os.path.join(FX, "transporter.png"))


def chevrons(count, size, scale, offset):
    """Gold rank chevrons, like a sleeve insignia."""
    img = np.zeros((size, size, 4), float)
    y, x = np.mgrid[0:size, 0:size].astype(float)
    ox, oy = offset
    for i in range(count):
        cy = oy + i * 4.0 * scale
        # A V shape: distance to two short segments.
        best = np.full(x.shape, 1e9)
        for sx in (-1, 1):
            ax, ay = ox, cy + 3.0 * scale
            bx, by = ox + sx * 5.0 * scale, cy
            vx, vy = bx - ax, by - ay
            t = np.clip(((x - ax) * vx + (y - ay) * vy) / (vx * vx + vy * vy), 0, 1)
            d = np.hypot(x - (ax + t * vx), y - (ay + t * vy))
            best = np.minimum(best, d)
        line = np.clip(1.3 * scale - best, 0, 1)
        edge = np.clip(2.2 * scale - best, 0, 1)
        img[..., 3] = np.maximum(img[..., 3], edge)
        for ch, (lc, ec) in enumerate(zip((255, 215, 90), (60, 40, 0))):
            img[..., ch] = np.where(line > 0, lc * line + ec * (1 - line), np.where(edge > 0, ec, img[..., ch]))
    img[..., 3] *= 255
    return Image.fromarray(img.astype(np.uint8), "RGBA")


def draw_badges():
    os.makedirs(MISC, exist_ok=True)
    # Overlays: 72 x 72, badge in the top-left corner of the hex.
    chevrons(1, 72, 1.0, (16, 14)).save(os.path.join(MISC, "dw-veteran.png"))
    chevrons(2, 72, 1.0, (16, 12)).save(os.path.join(MISC, "dw-elite.png"))
    # Icons for the advancement menu.
    chevrons(1, 60, 3.0, (30, 20)).save(os.path.join(MISC, "dw-veteran-icon.png"))
    chevrons(2, 60, 3.0, (30, 14)).save(os.path.join(MISC, "dw-elite-icon.png"))


def main():
    os.makedirs(FX, exist_ok=True)
    draw_beams()
    draw_torpedoes()
    draw_transporter()
    draw_badges()
    print("wrote", FX, "and", MISC)


if __name__ == "__main__":
    main()
