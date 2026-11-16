"""Minimal reader for old 3ds Max .max files (written here from the MS-CFB spec and the Max SDK mesh chunk layout).
- cfb_streams(path): {stream name: bytes} from the OLE compound file
- chunks(data): parse the Max chunk tree (uint16 id, int32 size incl. header, negative size = container, 0 = 64-bit size)
Usage: python3 -I maxread.py FILE.max [dump|meshes OUTDIR]
"""
import struct, sys, os, zlib

def cfb_streams(path):
    b = open(path, 'rb').read()
    assert b[:8] == bytes.fromhex('D0CF11E0A1B11AE1'), 'not an OLE file'
    ss = 1 << struct.unpack_from('<H', b, 0x1E)[0]; mss = 1 << struct.unpack_from('<H', b, 0x20)[0]
    nfat, dir0, _txn, cutoff, mfat0, nmfat, difat0, ndifat = struct.unpack_from('<IIIIIIII', b, 0x2C)
    sec = lambda n: b[(n + 1) * ss:(n + 2) * ss]
    difat = list(struct.unpack_from('<109I', b, 0x4C)); d = difat0
    for _ in range(ndifat):
        s = sec(d); difat += struct.unpack_from('<%dI' % (ss // 4 - 1), s); d = struct.unpack_from('<I', s, ss - 4)[0]
    fat = []
    for n in difat[:nfat]: fat += struct.unpack('<%dI' % (ss // 4), sec(n))
    def chain(n, table):
        out = []
        seen = set()
        while n < 0xFFFFFFFA and n < len(table) and n not in seen: seen.add(n); out.append(n); n = table[n]
        return out
    dirs = b''.join(sec(n) for n in chain(dir0, fat))
    ents = []
    for i in range(len(dirs) // 128):
        e = dirs[i * 128:(i + 1) * 128]; nl = struct.unpack_from('<H', e, 0x40)[0]
        name = e[:max(nl - 2, 0)].decode('utf-16-le', 'replace'); typ = e[0x42]
        start, size = struct.unpack_from('<IQ', e, 0x74)
        if ss == 512: size &= 0xFFFFFFFF
        ents.append((name, typ, start, size))
    root = ents[0]; ministream = b''.join(sec(n) for n in chain(root[2], fat))[:root[3]]
    mfat = []
    for n in chain(mfat0, fat): mfat += struct.unpack('<%dI' % (ss // 4), sec(n))
    out = {}
    for name, typ, start, size in ents:
        if typ != 2: continue
        if size < cutoff:
            data = b''.join(ministream[n * mss:(n + 1) * mss] for n in chain(start, mfat))
        else:
            data = b''.join(sec(n) for n in chain(start, fat))
        out[name] = data[:size]
    return out

class Chunk:
    __slots__ = ('id', 'kids', 'data', 'off')
    def __init__(s, id, kids=None, data=None, off=0): s.id, s.kids, s.data, s.off = id, kids, data, off
    def first(s, id):
        for k in s.kids or []:
            if k.id == id: return k

def chunks(data, base=0, depth=0):
    out = []; o = 0
    if depth == 0 and data[:2] == b'\x1f\x8b': data = zlib.decompress(data, zlib.MAX_WBITS | 32)
    while o + 6 <= len(data):
        cid, size = struct.unpack_from('<Hi', data, o); hdr = 6
        if size == 0:
            size = struct.unpack_from('<q', data, o + 6)[0]; hdr = 14
        cont = size < 0; size &= 0x7FFFFFFFFFFFFFFF if hdr == 14 else 0x7FFFFFFF
        if size < hdr or o + size > len(data): break
        body = data[o + hdr:o + size]
        if cont: out.append(Chunk(cid, chunks(body, base + o + hdr, depth + 1), None, base + o))
        else: out.append(Chunk(cid, None, body, base + o))
        o += size
    return out

def walk(cs, path=()):
    for i, c in enumerate(cs):
        yield path + (i,), c
        if c.kids: yield from walk(c.kids, path + (i,))

def mesh_of(c):
    """c: a container holding a 0x0914 vertex chunk and a 0x0912 face chunk."""
    v = c.first(0x0914); f = c.first(0x0912)
    if not v or not f: return None
    n = struct.unpack_from('<I', v.data)[0]
    if len(v.data) < 4 + 12 * n: return None
    verts = struct.unpack_from('<%df' % (3 * n), v.data, 4)
    m = struct.unpack_from('<I', f.data)[0]; faces = []; mats = []
    if len(f.data) >= 4 + 16 * m and (len(f.data) - 4) % m == 0 if m else False:
        step = (len(f.data) - 4) // m
        for i in range(m):
            a, b2, c2 = struct.unpack_from('<3I', f.data, 4 + i * step); faces.append((a, b2, c2))
            if step >= 20: mats.append(struct.unpack_from('<HH', f.data, 4 + i * step + 16)[1])
    tv = c.first(0x0916); tf = c.first(0x0918); uv = None; uvf = None
    if tv and tf:
        k = struct.unpack_from('<I', tv.data)[0]; uv = struct.unpack_from('<%df' % (3 * k), tv.data, 4)
        if len(tf.data) == 12 * len(faces): uvf = [struct.unpack_from('<3I', tf.data, 12 * i) for i in range(len(faces))]
        else:
            k2 = struct.unpack_from('<I', tf.data)[0]; uvf = [struct.unpack_from('<3I', tf.data, 4 + 12 * i) for i in range(k2)]
    return verts, faces, mats, uv, uvf

def write_obj(path, verts, faces, mats, uv, uvf):
    with open(path, 'w') as o:
        o.write('# converted from .max by tools/maxread.py\n')
        for i in range(0, len(verts), 3): o.write('v %.6f %.6f %.6f\n' % verts[i:i + 3])
        if uv:
            for i in range(0, len(uv), 3): o.write('vt %.6f %.6f\n' % (uv[i], uv[i + 1]))
        order = sorted(range(len(faces)), key=lambda i: mats[i] if mats else 0); cur = None
        for i in order:
            m = mats[i] if mats else 0
            if m != cur: o.write('usemtl m%d\n' % m); cur = m
            a, b, c = faces[i]
            if uvf: ta, tb, tc = uvf[i]; o.write('f %d/%d %d/%d %d/%d\n' % (a + 1, ta + 1, b + 1, tb + 1, c + 1, tc + 1))
            else: o.write('f %d %d %d\n' % (a + 1, b + 1, c + 1))

if __name__ == '__main__':
    st = cfb_streams(sys.argv[1]); mode = sys.argv[2] if len(sys.argv) > 2 else 'dump'
    if mode == 'dump':
        for k, v in st.items(): print('stream', repr(k), len(v))
        sc = chunks(st['Scene']); n = 0
        for p, c in walk(sc):
            if c.id in (0x0914, 0x0912) and n < 400: print('  ', p, hex(c.id), len(c.data) if c.data is not None else 'C'); n += 1
    if mode == 'meshes':
        out = sys.argv[3]; os.makedirs(out, exist_ok=True); k = 0
        for p, c in walk(chunks(st['Scene'])):
            if c.kids and c.first(0x0914) and c.first(0x0912):
                r = mesh_of(c)
                if r: write_obj(os.path.join(out, 'mesh%02d.obj' % k), *r); print('mesh', k, p, len(r[0]) // 3, 'verts', len(r[1]), 'faces', 'mats', sorted(set(r[2]))); k += 1
