"""Decode Amiga IFF ILBM images (palette or 24-bit, ByteRun1 or raw) to PIL images."""
import struct
import numpy as np
from PIL import Image

def chunks(b, off, end):
    while off + 8 <= end:
        cid = b[off:off+4].decode('latin1'); sz = struct.unpack('>I', b[off+4:off+8])[0]
        yield cid, off + 8, sz
        off += 8 + sz + (sz & 1)

def byterun1(src, pos, n):
    out = bytearray()
    while len(out) < n:
        c = src[pos]; pos += 1
        if c < 128: out += src[pos:pos+c+1]; pos += c + 1
        elif c > 128: out += bytes([src[pos]]) * (257 - c); pos += 1
    return bytes(out[:n]), pos

def load(path):
    b = open(path, 'rb').read()
    assert b[:4] == b'FORM' and b[8:12] == b'ILBM', path
    cmap = None; body = None
    for cid, o, sz in chunks(b, 12, len(b)):
        if cid == 'BMHD': w, h, _, _, npl, mask, comp, _, tcol = struct.unpack('>HHhhBBBBH', b[o:o+14])
        elif cid == 'CMAP': cmap = np.frombuffer(b[o:o+sz], np.uint8)[:sz//3*3].reshape(-1, 3)
        elif cid == 'BODY': body = (o, sz)
    rb = ((w + 15) // 16) * 2; nplanes = npl + (1 if mask == 1 else 0)
    pos = body[0]; planes = np.zeros((h, nplanes, rb * 8), np.uint8)
    for y in range(h):
        for p in range(nplanes):
            if comp == 1: row, pos = byterun1(b, pos, rb)
            else: row = b[pos:pos+rb]; pos += rb
            planes[y, p] = np.unpackbits(np.frombuffer(row, np.uint8))
    planes = planes[:, :, :w].astype(np.uint32)
    if npl == 24:
        rgb = np.zeros((h, w, 3), np.uint8)
        for c in range(3):
            v = np.zeros((h, w), np.uint32)
            for i in range(8): v |= planes[:, c*8+i] << i
            rgb[..., c] = v
        return Image.fromarray(rgb)
    idx = np.zeros((h, w), np.uint32)
    for i in range(npl): idx |= planes[:, i] << i
    if cmap is None: cmap = np.stack([np.linspace(0, 255, 1 << npl)] * 3, 1).astype(np.uint8)
    pal = np.zeros((256, 3), np.uint8); pal[:len(cmap)] = cmap[:256]
    return Image.fromarray(pal[np.clip(idx, 0, 255)])

if __name__ == '__main__':
    import sys
    load(sys.argv[1]).save(sys.argv[2])
