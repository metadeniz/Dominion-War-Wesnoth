# python3 -I objgroups.py MODEL.obj -> bounding box and face count per o/g group
import sys, numpy as np
V = []; groups = {}; cur = 'default'
for line in open(sys.argv[1], errors='replace'):
    if line.startswith('v '): V.append([float(x) for x in line.split()[1:4]])
    elif line.startswith(('o ', 'g ')): cur = line.split(None, 1)[1].strip() if len(line.split()) > 1 else 'unnamed'
    elif line.startswith('usemtl'): cur2 = line.split(None, 1)[1].strip(); cur = cur.split('|')[0] + '|' + cur2
    elif line.startswith('f '):
        idx = [int(t.split('/')[0]) for t in line.split()[1:]]; groups.setdefault(cur, []).extend(idx)
V = np.array(V)
print('vertices', len(V), 'bbox', V.min(0).round(2), V.max(0).round(2))
for g, idx in groups.items():
    i = np.array(idx); i = np.where(i < 0, len(V) + i, i - 1); P = V[i]
    print('%-50s faces~%6d  min %s max %s' % (g[:50], len(idx) // 3, P.min(0).round(2), P.max(0).round(2)))
