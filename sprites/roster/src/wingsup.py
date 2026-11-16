"""Raise the wings of the TTS B'rel bird-of-prey (wings-down attack pose -> wings-up cruise pose).
Each wing is rotated about a fore-aft hinge line at |z|=Z0, y=Y0; the angle ramps in over RAMP so the root bends smoothly.
Normals are rotated with their vertices (one new vn per face corner). UVs are untouched, so brel.png still fits.
Usage: python3 -I wingsup.py in.obj out.obj ANGLE_DEG [Z0 Y0 RAMP]"""
import sys, numpy as np
src, dst, ang = sys.argv[1], sys.argv[2], np.radians(float(sys.argv[3]))
Z0 = float(sys.argv[4]) if len(sys.argv) > 4 else 0.30; Y0 = float(sys.argv[5]) if len(sys.argv) > 5 else 0.06
RAMP = float(sys.argv[6]) if len(sys.argv) > 6 else 0.08
L = open(src).read().split('\n')
V = []; VN = []; other = []; faces = []
for l in L:
    if l.startswith('v '): V.append([float(t) for t in l.split()[1:4]])
    elif l.startswith('vn '): VN.append([float(t) for t in l.split()[1:4]])
V = np.array(V); VN = np.array(VN)
az = np.abs(V[:, 2]); sg = np.where(V[:, 2] < 0, -1.0, 1.0)
a = ang * np.clip((az - (Z0 - RAMP)) / RAMP, 0, 1)           # per-vertex angle
c, s = np.cos(a), np.sin(a)
dz, dy = az - Z0, V[:, 1] - Y0
nz_ = Z0 + dz * c - dy * s; ny_ = Y0 + dz * s + dy * c
V2 = V.copy(); V2[:, 2] = sg * nz_; V2[:, 1] = ny_
out = []; nv = 0; newvn = []
for l in L:
    if l.startswith('v '):
        nv += 1; x, y, z = V2[nv - 1]; out.append('v %.6f %.6f %.6f' % (x, y, z))
    elif l.startswith('vn '): continue
    elif l.startswith('f '):
        parts = []
        for tok in l.split()[1:]:
            f = tok.split('/'); vi = int(f[0]) - 1
            if len(f) > 2 and f[2]:
                n = VN[int(f[2]) - 1].copy(); nzz = n[2] * sg[vi]; nyy = n[1]
                n[2] = sg[vi] * (nzz * c[vi] - nyy * s[vi]); n[1] = nzz * s[vi] + nyy * c[vi]
                newvn.append(n); f[2] = str(len(newvn))
            parts.append('/'.join(f))
        out.append('f ' + ' '.join(parts))
    else: out.append(l)
# put normals right after the vertices
i = max(k for k, l in enumerate(out) if l.startswith('v '))
out = out[:i + 1] + ['vn %.5f %.5f %.5f' % tuple(n) for n in newvn] + out[i + 1:]
open(dst, 'w').write('\n'.join(out))
print('rotated', int((a > 0).sum()), 'of', len(V), 'verts; wing tip y', V[az > 0.8, 1].mean().round(3), '->', V2[az > 0.8, 1].mean().round(3))
