# Cost formula check: compares each ship's price in units.py with
#   cost = HP/4 + melee/5 + ranged*0.3 + ability gold - 1
# melee and ranged are the best attack's damage x strikes (fleet tactics x1.25, energy dampener x1.4;
# kamikaze and detonate left out). Ability gold is the same table duel.py uses.
# Reads units.py as data (no code from it is run).  Usage: python3 costformula.py units.py
import sys, re, ast

TAX = {"Sensors": 1, "Repairs +4": 3, "Cloak": 3, "Nebula cloak": 1.5, "Command": 3, "Evasive": 1,
       "Glory": 1, "Plunder": 1, "Ketracel supply": 2, "Ketracel-dependent": -1, "Badlands pilots": 0.5}
MULT = {"fleet tactics": 1.25, "energy dampener": 1.4}

def load(path):
    s = open(path).read()
    body = re.sub(r"\bA\(", "(", s[s.index("U = [") + 4:])
    U = ast.literal_eval(body.strip())
    return [u[:11] + ([a + ("",) * (6 - len(a)) for a in u[11]],) + u[12:] for u in U]

def best(u, rng):
    xs = [a[1] * a[2] * MULT.get(a[5], 1) for a in u[11]
          if a[4] == rng and a[5] not in ("kamikaze", "detonate")]
    return max(xs) if xs else 0

def formula(u):
    ab = sum(TAX.get(x, 0) for x in u[12])
    return u[4] / 4 + best(u, "m") / 5 + best(u, "r") * 0.3 + ab - 1, ab

if __name__ == "__main__":
    print(f"{'Ship':36}{'cost':>5}{'formula':>8}{'diff':>6}   HP melee ranged abil")
    for u in load(sys.argv[1]):
        if "Machine" in u[12]:
            print(f"{u[1][:35]:36}{u[3]:5}{'':>8}{'':>6}   one-shot warhead, priced by hand")
            continue
        f, ab = formula(u)
        flag = "  <-- off by 2+" if abs(u[3] - f) >= 2 else ""
        print(f"{u[1][:35]:36}{u[3]:5}{f:8.1f}{u[3] - f:+6.1f}   {u[4]:3} {best(u, 'm'):5.1f} {best(u, 'r'):5.0f} {ab:4}{flag}")
