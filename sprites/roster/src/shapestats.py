# python3 -I shapestats.py  -> per ship: which way the visible hull faces (from the normals pass), in the light rig's frame
# x = screen right, y = up, z = toward the camera (the camera looks down at 45 degrees)
import sys, os, json, numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lightlab import U, PD
e = np.radians(45)
LIGHTS = {'K1': [7, 2.5, -0.5], 'K2': [7, 5, -0.5], 'K3': [5, 2.5, 4], 'K4': [6, 2.5, -4], 'O': [0, 8, 0.3], 'R': [-6, 2, -4], 'F1': [-4, 2, 5], 'F2': [-7, 2.5, 0], 'F3': [-3, 6, 3]}
def normals(uid):
    a = np.asarray(Image.open(os.path.join(PD, uid, 'N.png')).convert('RGBA')).astype(np.float32) / 255
    m = a[..., 3] > 0.9; nv = a[..., :3][m] * 2 - 1; nv /= np.maximum(np.linalg.norm(nv, axis=1, keepdims=True), 1e-6)
    X = np.array([1, 0, 0]); Y = np.array([0, np.cos(e), -np.sin(e)]); Z = np.array([0, np.sin(e), np.cos(e)])
    return nv[:, :1] * X + nv[:, 1:2] * Y + nv[:, 2:3] * Z
def stats(uid):
    n = normals(uid)
    d = {'up': (n[:, 1] > 0.85).mean(), 'left': (n[:, 0] < -0.5).mean(), 'right': (n[:, 0] > 0.5).mean(), 'front': (n[:, 2] > 0.5).mean(), 'down': (n[:, 1] < -0.2).mean()}
    for k, v in LIGHTS.items():
        v = np.array(v, float); v /= np.linalg.norm(v); c = np.clip(n @ v, 0, None); d['c' + k] = c.mean()
    return d
if __name__ == '__main__':
    rows = {u: stats(u) for u in U}
    ks = list(next(iter(rows.values())).keys())
    print('%-18s' % 'ship' + ''.join('%6s' % k for k in ks))
    for u, d in rows.items(): print('%-18s' % u + ''.join('%6.2f' % d[k] for k in ks))
    json.dump({u: {k: float(v) for k, v in d.items()} for u, d in rows.items()}, open(os.path.join(os.path.dirname(PD), 'shapestats.json'), 'w'), indent=1)
