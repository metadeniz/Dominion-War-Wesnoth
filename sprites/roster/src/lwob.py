"""Parse a LightWave 5 (LWOB) object: points, polygons, surfaces with their texture settings."""
import struct
import numpy as np

def chunks(b, off, end, hdr=4):
    while off + 4 + hdr <= end:
        cid = b[off:off+4].decode('latin1')
        sz = struct.unpack('>I' if hdr == 4 else '>H', b[off+4:off+4+hdr])[0]
        yield cid, off + 4 + hdr, sz
        off += 4 + hdr + sz + (sz & 1)

def s0(b, o):
    e = b.index(b'\0', o); return b[o:e].decode('latin1'), e + 1 + ((e + 1 - o) & 1)

def parse(path):
    b = open(path, 'rb').read(); assert b[:4] == b'FORM' and b[8:12] == b'LWOB'
    pts = None; srfs = []; polys = []; surfs = {}
    for cid, o, sz in chunks(b, 12, len(b)):
        if cid == 'PNTS': pts = np.frombuffer(b[o:o+sz], '>f4').reshape(-1, 3).astype(np.float64)
        elif cid == 'SRFS':
            p = o
            while p < o + sz: n, p = s0(b, p); srfs.append(n)
        elif cid == 'POLS':
            p = o; end = o + sz
            while p < end:
                nv = struct.unpack('>H', b[p:p+2])[0]; p += 2
                vs = struct.unpack('>%dH' % nv, b[p:p+2*nv]); p += 2*nv
                s = struct.unpack('>h', b[p:p+2])[0]; p += 2
                if s < 0: s = -s; p += 2   # detail polygon count follows; details are listed inline next
                polys.append((vs, s - 1))
        elif cid == 'SURF':
            name, p = s0(b, o); d = {'tex': []}; cur = None
            for sc, so, ss in chunks(b, p, o + sz, hdr=2):
                v = b[so:so+ss]
                if sc == 'COLR': d['colr'] = tuple(v[:3])
                elif sc in ('LUMI', 'DIFF', 'SPEC', 'TRAN', 'REFL', 'GLOS'): d[sc.lower()] = struct.unpack('>H', v[:2])[0] / 256
                elif sc in ('VLUM', 'VDIF', 'VSPC', 'VTRN'): d[sc.lower()] = struct.unpack('>f', v[:4])[0]
                elif sc == 'FLAG': d['flag'] = struct.unpack('>H', v[:2])[0]
                elif sc in ('CTEX', 'DTEX', 'STEX', 'RTEX', 'TTEX', 'LTEX', 'BTEX'):
                    cur = {'slot': sc, 'type': v.split(b'\0')[0].decode('latin1')}; d['tex'].append(cur)
                elif cur is not None:
                    if sc == 'TFLG': cur['flg'] = struct.unpack('>H', v[:2])[0]
                    elif sc in ('TSIZ', 'TCTR', 'TFAL', 'TVEL'): cur[sc.lower()] = struct.unpack('>3f', v[:12])
                    elif sc == 'TIMG': cur['img'] = v.split(b'\0')[0].decode('latin1')
                    elif sc == 'TALP': cur['alp'] = v.split(b'\0')[0].decode('latin1')
                    elif sc == 'TWRP': cur['wrp'] = struct.unpack('>HH', v[:4])
                    elif sc == 'TVAL': cur['val'] = struct.unpack('>H', v[:2])[0] / 256
                    elif sc == 'TAMP': cur['amp'] = struct.unpack('>f', v[:4])[0]
                    elif sc == 'TCLR': cur['clr'] = tuple(v[:3])
                    elif sc == 'TOPC': cur['opc'] = struct.unpack('>f', v[:4])[0]
                    elif sc == 'TFP0': cur['fp0'] = struct.unpack('>f', v[:4])[0]
            surfs[name] = d
    return pts, srfs, polys, surfs
