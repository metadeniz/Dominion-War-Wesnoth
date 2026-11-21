import sys, math, importlib.util
spec=importlib.util.spec_from_file_location("units",sys.argv[1]); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
U,RES,HIT=m.U,m.RES,m.HIT
TAX={"Sensors":1,"Repairs +4":3,"Cloak":3,"Nebula cloak":1.5,"Command":3,"Evasive":1,"Glory":1,"Plunder":1,
     "Ketracel supply":2,"Ketracel-dependent":-1,"Machine":0,"Badlands pilots":0.5}
def dmg(att,res,hit):
    n,d,s,t,r,sp=att
    if sp in ("kamikaze","detonate"): return 0.0  # one-off, scored separately
    if sp=="transporter": res={k:0 for k in res}
    if sp=="targeting lock": hit=max(hit,0.6)
    mult=1.25 if sp=="fleet tactics" else 1.0
    if sp=="charge": mult=1.4   # rough: doubled on attack, but retaliation doubles too
    if sp=="shield breaker": mult=1.25   # rough: allies then hit the weakened target harder
    if sp=="energy dampener": mult=1.4   # slow halves retaliation & next turn damage
    v=round(d*(100-res[t])/100*mult)*s*hit
    if sp=="ramming speed": v*=1.6  # fights to the end
    return v
def best(ua,ub,r):
    xs=[dmg(a,RES[ub[9]],HIT[ub[7]]) for a in ua[11] if a[4]==r]
    return max(xs) if xs else 0.0
def duel(ua,ub):
    ranges=["r","m"]
    def choose(att,de):
        return max(ranges,key=lambda r:(best(att,de,r)-0.8*best(de,att,r)) if best(att,de,r)>0 else -99)
    ra=choose(ua,ub); rb=choose(ub,ua)
    toB=best(ua,ub,ra)+best(ua,ub,rb); toA=best(ub,ua,ra)+best(ub,ua,rb)
    ca=ua[3]-sum(TAX.get(x,0) for x in ua[12]); cb=ub[3]-sum(TAX.get(x,0) for x in ub[12])
    sa=(ua[4]/max(toA,.1)); sb=(ub[4]/max(toB,.1))
    return math.log((sa/sb)*(cb/ca)**1.5)
facs=["Federation","Klingon","Dominion","Maquis"]
rec=lambda f:[u for u in U if u[0]==f and not u[13] and "Machine" not in u[12]]
print(" "*12+"".join(f"{f[:8]:>10}" for f in facs))
for a in facs:
    line=f"{a[:11]:12}"
    for b in facs:
        v=[duel(x,y) for x in rec(a) for y in rec(b)]
        line+=f"{math.exp(sum(v)/len(v)):>10.2f}"
    print(line)
print("\nper unit vs all enemy recruits (geo mean strength per gold, 1.0 = even)")
allr=[u for f in facs for u in rec(f)]
for u in U:
    if "Machine" in u[12]: continue
    v=[duel(u,y) for y in allr if y[0]!=u[0]]
    print(f"{u[1][:34]:35}{math.exp(sum(v)/len(v)):6.2f}")
