import json, random, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tools')); from sprite72 import make72
from PIL import Image, ImageDraw, ImageFont
R=json.load(open('roster2.json')); OUT=sys.argv[1]
F=lambda s,b=False: ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf'%('-Bold' if b else ''), s)
CW,CH,PAD,PER=176,200,28,6
rows=sum((len(f['units'])+PER-1)//PER for f in R)
W=PAD*2+PER*CW; H=PAD+132+len(R)*50+rows*CH+20
im=Image.new('RGBA',(W,H),(11,14,24,255)); d=ImageDraw.Draw(im); random.seed(3)
for _ in range(W*H//900):
    v=random.randint(70,200); d.point((random.randrange(W),random.randrange(H)),(v,v,v+20,255))
d.text((PAD,PAD),"Star Trek Wesnoth: canon roster sprites (draft 42)",font=F(28,True),fill=(235,238,245))
d.text((PAD,PAD+40),"Recruits are level 1 and level up through crew experience; gold cards are leader-only ships. 72x72 game size shown at 2x, 45° camera, facing south-east.",font=F(14),fill=(160,170,190))
d.text((PAD,PAD+84),"Coin, top left = price in gold (drafts for the Raptor, D5, Dreadnought and Marauder). ASK = the model's author asks for permission first.",font=F(14),fill=(160,170,190))
d.text((PAD,PAD+62),"Tag = model licence: CC BY/CC0 free; NC = non-commercial; NC-ND = no changes; STD = Sketchfab Standard; ? = none stated; OURS* = built here.",font=F(14),fill=(160,170,190))
y=PAD+122
late=[]
for f in R:
    nl=sum(1 for u in f['units'] if u.get('leader')); nr=len(f['units'])-nl
    d.text((PAD,y),f"{f['faction']}  ({nr} ships" + (f" + {nl} leader" + ("s" if nl>1 else "") if nl else "") + ")",font=F(22,True),fill=(255,214,120)); y+=40
    for i,u in enumerate(f['units']):
        x=PAD+(i%PER)*CW
        if i and i%PER==0: y+=CH
        d.rounded_rectangle((x,y,x+CW-12,y+CH-14),10,fill=(34,30,30,255) if u.get('leader') else (22,28,46,255),outline=(200,160,70) if u.get('leader') else (45,55,85),width=2 if u.get('leader') else 1)
        lx=x+8
        if 'cost' in u:   # price: gold coin + number, top left
            d.ellipse((x+8,y+8,x+20,y+20),fill=(222,178,72),outline=(150,110,40)); d.ellipse((x+11,y+11,x+17,y+17),outline=(170,128,48))
            d.text((x+24,y+6),str(u['cost']),font=F(13,True),fill=(240,210,120)); lx=x+30+d.textlength(str(u['cost']),font=F(13,True))
        if u.get('leader'): d.text((lx,y+9),'LEADER',font=F(10,True),fill=(230,190,90))
        sp=make72(Image.open(f"out2/{u['id']}.png"),u.get('pop',False),6); n2=sp.size[0]*2; sp=sp.resize((n2,n2),Image.NEAREST)
        if n2>144: late.append((sp,(x+(CW-12-n2)//2,y+6-(n2-144)//2)))   # oversize: drawn last, spilling past its card
        else: im.alpha_composite(sp,(x+(CW-12-144)//2,y+6))
        lic={'CC BY 4.0':'CC BY','CC BY-NC 4.0':'CC BY-NC','CC BY-NC-ND 4.0':'NC-ND','CC0':'CC0','no licence stated':'?','Sketchfab Standard':'STD'}.get(u['lic'],u.get('tag','?'))
        col=(110,200,140) if lic in('CC BY','CC0') else (220,170,90) if lic in('CC BY-NC','OURS*','STD') else (220,110,110)
        d.text((x+CW-20,y+8),lic,font=F(10,True),fill=col,anchor='ra')
        words=u['name'].split(); lines=['']
        for w_ in words:
            t=(lines[-1]+' '+w_).strip()
            if d.textlength(t,font=F(13))>CW-24: lines.append(w_)
            else: lines[-1]=t
        for j,l in enumerate(lines[:2]): d.text((x+8,y+152+j*15),l,font=F(13),fill=(225,230,240))
    y+=CH+10
for sp_,pos_ in late: im.alpha_composite(sp_,pos_)
im=im.crop((0,0,W,y+10)); im.convert('RGB').save(OUT); print(im.size)
