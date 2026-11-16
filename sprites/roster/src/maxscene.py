"""Assemble the nodes of an old .max scene into one OBJ (my own code; chunk ids from the Max SDK layout).
Usage: python3 -I maxscene.py FILE.max OUT.obj [--quat=std|conj] [--list]
Each node: class (guid 1, super 1), 0x0962 name, 0x0960 parent, 0x2034/0x2035 references
(ref 0 = PRS controller, ref 1 = object), 0x096A/B/C object-offset position/rotation/scale.
"""
import sys, struct, math, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from maxread import cfb_streams, chunks, mesh_of, write_obj, walk

def classes(st):
    name = 'ClassDirectory3' if 'ClassDirectory3' in st else 'ClassDirectory2' if 'ClassDirectory2' in st else 'ClassDirectory'
    out = []
    for c in chunks(st[name]):
        e = {'name': None, 'guid': None, 'super': None}
        for k in c.kids or []:
            if k.id == 0x2042: e['name'] = k.data.decode('utf-16-le', 'replace')
            if k.id == 0x2060 and len(k.data) >= 16: dll, guid, sup = struct.unpack_from('<IQI', k.data); e.update(guid=guid, super=sup)
        out.append(e)
    return out

def refs_of(c):
    r = c.first(0x2034)
    if r: return {i: v for i, v in enumerate(struct.unpack('<%dI' % (len(r.data) // 4), r.data))}
    r = c.first(0x2035)
    if r:
        a = struct.unpack('<%dI' % (len(r.data) // 4), r.data); d = {}
        for i in range(1, len(a) - 1, 2): d[a[i]] = a[i + 1]
        return d
    return {}

def qmat(q, conj=False):
    x, y, z, w = q
    if conj: x, y, z = -x, -y, -z
    n = math.sqrt(x*x + y*y + z*z + w*w) or 1; x, y, z, w = x/n, y/n, z/n, w/n
    return [[1-2*(y*y+z*z), 2*(x*y-z*w), 2*(x*z+y*w)], [2*(x*y+z*w), 1-2*(x*x+z*z), 2*(y*z-x*w)], [2*(x*z-y*w), 2*(y*z+x*w), 1-2*(x*x+y*y)]]

def m4(pos=(0, 0, 0), q=(0, 0, 0, 1), s=(1, 1, 1), conj=False):
    R = qmat(q, conj); return [[R[i][0]*s[0], R[i][1]*s[1], R[i][2]*s[2], pos[i]] for i in range(3)] + [[0, 0, 0, 1]]

def mul(A, B): return [[sum(A[i][k]*B[k][j] for k in range(4)) for j in range(4)] for i in range(4)]

def floats(c, cid, n):
    k = c.first(cid) if c and c.kids else None
    if k and len(k.data) >= 4*n: return struct.unpack_from('<%df' % n, k.data)
    return None

import re
def _bitmaps(top, cls, i, seen=None, depth=0):
    """filenames of Bitmap texmaps reachable from scene index i"""
    seen = seen if seen is not None else set(); out = []
    if i >= len(top) or i in seen or depth > 6: return out
    seen.add(i); c = top[i]
    if c.id < len(cls) and cls[c.id]['name'] == 'Bitmap':
        for _p, k in walk([c]):
            if k.id == 0x1230 and k.data:
                for enc in ('utf-16-le', 'latin-1'):
                    m = re.findall(r'[^\\/:*?"<>|\x00]+\.(?:png|bmp|jpg|jpeg|tga|tif)', k.data.decode(enc, 'ignore'), re.I)
                    if m: out.append(m[-1].strip()); break
    for key, v in sorted(refs_of(c).items()): out += _bitmaps(top, cls, v, seen, depth + 1)
    return out

def resolve_mat(top, cls, i):
    """-> ('std', diffuse_file or None, name) | ('topbot', top, bottom) | ('multi', [subs])"""
    if i is None or i >= len(top): return ('std', None, None)
    c = top[i]; n = cls[c.id]['name'] if c.id < len(cls) else '?'; r = refs_of(c)
    subs = [v for k, v in sorted(r.items()) if v < len(top) and cls[top[v].id]['name'] not in ('ParamBlock', 'ParamBlock2')]
    if n == 'Top/Bottom' and len(subs) >= 2: return ('topbot', resolve_mat(top, cls, subs[0]), resolve_mat(top, cls, subs[1]))
    if n.startswith('Multi') : return ('multi', [resolve_mat(top, cls, v) for v in subs])
    files = _bitmaps(top, cls, i); dif = [f for f in files if 'bump' not in f.lower()]
    return ('std', dif[0] if dif else None, n)

def pick(m, matid, nz):
    if m[0] == 'topbot': return pick(m[1] if nz >= 0 else m[2], matid, nz)
    if m[0] == 'multi': return pick(m[1][matid % len(m[1])], matid, nz) if m[1] else None
    return m[1]

def _mname(key): return re.sub(r'[^A-Za-z0-9_]+', '_', os.path.splitext(key)[0] if not key.startswith('node:') else key)

def node_colour(name):
    n = name.lower()
    if 'glow' in n or 'red' in n: return (0.9, 0.25, 0.1), (0.9, 0.25, 0.1)
    if 'light' in n: return (1.0, 0.9, 0.6), (1.0, 0.9, 0.6)
    if 'black' in n: return (0.08, 0.08, 0.08), None
    return (0.55, 0.45, 0.35), None

def write_obj_mtl(out, V, T, F, M, TF):
    base = os.path.splitext(out)[0]; mtl = os.path.basename(base) + '.mtl'
    with open(out, 'w') as o:
        o.write('# assembled from .max by tools/maxscene.py\nmtllib %s\n' % mtl)
        for v in V: o.write('v %.5f %.5f %.5f\n' % v)
        for t in T: o.write('vt %.6f %.6f\n' % (t[0], t[1]))
        o.write('vt 0 0\n'); dummy = len(T) + 1
        cur = None
        for i in sorted(range(len(F)), key=lambda i: M[i]):
            if M[i] != cur: cur = M[i]; o.write('usemtl %s\n' % _mname(cur))
            f = F[i]; tf = TF[i]
            ts = [t + 1 for t in tf] if tf else [dummy] * 3
            o.write('f %d/%d %d/%d %d/%d\n' % (f[0] + 1, ts[0], f[1] + 1, ts[1], f[2] + 1, ts[2]))
    with open(base + '.mtl', 'w') as o:
        for key in sorted(set(M)):
            o.write('newmtl %s\n' % _mname(key))
            if key.startswith('node:'):
                kd, ke = node_colour(key[5:]); o.write('Kd %.3f %.3f %.3f\n' % kd)
                if ke: o.write('Ke %.3f %.3f %.3f\n' % ke)
            else:
                o.write('Kd 1 1 1\nmap_Kd %s\n' % (os.path.splitext(key)[0] + '.png'))
            o.write('\n')
    print('materials', sorted(set(M)))

def main():
    path, out = sys.argv[1], sys.argv[2]; conj = '--quat=conj' in sys.argv; listing = '--list' in sys.argv
    st = cfb_streams(path); cls = classes(st); top = chunks(st['Scene'])[0].kids
    info = lambda c: cls[c.id] if c.id < len(cls) else {'name': '?', 'guid': None, 'super': None}
    def prs(i, depth=0):
        """local TM of the PRS controller at scene index i"""
        if i is None or i >= len(top): return m4()
        c = top[i]; g = info(c)['guid']; r = refs_of(c)
        pos, q, s = (0, 0, 0), (0, 0, 0, 1), (1, 1, 1)
        if g == 0x2005:
            pc = top[r[0]] if 0 in r and r[0] < len(top) else None
            rc = top[r[1]] if 1 in r and r[1] < len(top) else None
            sc = top[r[2]] if 2 in r and r[2] < len(top) else None
            pos = floats(pc, 0x2503, 3) or pos
            q = floats(rc, 0x2504, 4) or q
            s = (floats(sc, 0x2501, 3) or floats(sc, 0x2505, 3) or s)[:3]
        return m4(pos, q, s, conj), (pos, q, s)
    def find_mesh(i, depth=0, seen=None):
        seen = seen if seen is not None else set()
        if i is None or i >= len(top) or i in seen or depth > 6: return None
        seen.add(i); c = top[i]
        for k in c.kids or []:
            if k.kids and k.first(0x0914) and k.first(0x0912): return k
        r = refs_of(c)
        for key in sorted(r, reverse=True):
            m = find_mesh(r[key], depth + 1, seen)
            if m: return m
        return None
    nodes = {}
    for i, c in enumerate(top):
        g = info(c)
        if g['guid'] == 1 and g['super'] == 1:
            nm = c.first(0x0962); name = nm.data.decode('utf-16-le', 'replace').rstrip('\x00') if nm else '?'
            par = c.first(0x0960); parent = struct.unpack_from('<I', par.data)[0] if par and len(par.data) >= 4 else None
            nodes[i] = dict(c=c, name=name, parent=parent, refs=refs_of(c))
    def world(i, depth=0):
        n = nodes.get(i)
        if not n or depth > 30: return m4()
        L, _ = prs(n['refs'].get(0))
        return mul(world(n['parent'], depth + 1), L) if n['parent'] in nodes else L
    allv, allf, allm, allt, alltf = [], [], [], [], []
    for i, n in nodes.items():
        mc = find_mesh(n['refs'].get(1))
        _, (pos, q, s) = prs(n['refs'].get(0))
        if listing: print(i, repr(n['name']), 'parent', n['parent'], 'pos', [round(v, 2) for v in pos], 'q', [round(v, 3) for v in q], 's', [round(v, 3) for v in s], 'mesh', bool(mc))
        if not mc: continue
        r = mesh_of(mc)
        if not r: continue
        verts, faces, mats, uv, uvf = r
        mres = resolve_mat(top, cls, n['refs'].get(3))
        c = n['c']; op = floats(c, 0x096A, 3) or (0, 0, 0); oq = floats(c, 0x096B, 4) or (0, 0, 0, 1); osc = (floats(c, 0x096C, 3) or (1, 1, 1))[:3]
        M = mul(world(i), m4(op, oq, osc, conj))
        base = len(allv)
        for k in range(0, len(verts), 3):
            x, y, z = verts[k:k + 3]
            allv.append(tuple(M[j][0]*x + M[j][1]*y + M[j][2]*z + M[j][3] for j in range(3)))
        tb = len(allt)
        if uv:
            for k in range(0, len(uv), 3): allt.append((uv[k], uv[k + 1], 0.0))
        for fi, f in enumerate(faces):
            a, b2, c2 = (allv[v + base] for v in f)
            nz = (b2[0]-a[0])*(c2[1]-a[1]) - (b2[1]-a[1])*(c2[0]-a[0])
            if (M[0][0]*(M[1][1]*M[2][2]-M[1][2]*M[2][1]) - M[0][1]*(M[1][0]*M[2][2]-M[1][2]*M[2][0]) + M[0][2]*(M[1][0]*M[2][1]-M[1][1]*M[2][0])) < 0: nz = -nz
            tex = pick(mres, mats[fi] if mats else 0, nz)
            key = tex if tex else ('node:' + n['name'])
            allf.append(tuple(v + base for v in f)); allm.append(key)
            alltf.append(tuple(t + tb for t in uvf[fi]) if uvf and uv else None)
    write_obj_mtl(out, allv, allt, allf, allm, alltf)
    print('nodes', len(nodes), 'verts', len(allv), 'faces', len(allf))

if __name__ == '__main__': main()
