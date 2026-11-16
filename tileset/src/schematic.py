# flat-colour schematic of the original Wesnoth map, same hex layout as mock.py
import sys
from PIL import Image, ImageDraw
rows=[[c.strip().split(' ')[-1] for c in l.split(',')] for l in open(sys.argv[1]).read().strip().splitlines() if l.strip()]
H,W=len(rows),len(rows[0]); im=Image.new('RGB',(W*54+18,H*72+36),(0,0,0)); d=ImageDraw.Draw(im)
def col(c):
    b,_,o=c.partition('^')
    if c.startswith('_off'): return None
    if o.startswith('V'): return (240,200,60)
    if b[:1] in 'CK': return (150,150,160) if b[0]=='C' else (230,230,240)
    if o.startswith('X') or b[:1]=='X' or b[:1]=='Q': return (40,30,30)
    if o.startswith('F'): return (30,100,40)
    if o.startswith('T') or b[:1]=='T': return (120,60,140)
    if b.startswith('Wwf'): return (110,160,190)
    if b.startswith('Wo'): return (20,50,120)
    if b[:1]=='W': return (50,100,180)
    if b[:1]=='S': return (70,100,80)
    if b[:1]=='H': return (150,130,80)
    if b[:1]=='M': return (110,90,70)
    if b[:1]=='D': return (220,200,140)
    if b[:1]=='A': return (230,240,250)
    if b[:1]=='U': return (60,50,50)
    return (110,160,70)
for y in range(H):
    for x in range(W):
        c=col(rows[y][x])
        if not c: continue
        px,py=x*54,y*72+(36 if x%2==0 else 0)
        d.polygon([(px+18,py),(px+54,py),(px+72,py+36),(px+54,py+72),(px+18,py+72),(px,py+36)],fill=c,outline=(0,0,0))
im.save(sys.argv[2])
