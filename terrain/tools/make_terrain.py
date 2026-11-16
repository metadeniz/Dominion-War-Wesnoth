#!/usr/bin/env python3
"""Builds the space terrain of The Dominion War: every image under terrain/images/terrain/dw/,
terrain/terrain.cfg (terrain types) and terrain/terrain-graphics.cfg (drawing rules).

    cd terrain/tools && python3 make_terrain.py            # everything
    python3 make_terrain.py --wml                          # only the two .cfg files

The mapping from Wesnoth terrain to space terrain is in terrain/lua/space_terrain.lua (used in game)
and convert_map.py (the same table, for converting .map files by hand). Design: design/space-tileset.md.
"""
import os, sys, math, random, json
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
ROOT = os.path.dirname(HERE)                     # terrain/
IMG = os.path.join(ROOT, 'images', 'terrain', 'dw')
import gaslib as G

# ---------------------------------------------------------------------------------------------
# Terrain types. Every space terrain plays exactly as the Wesnoth terrain it replaces: it copies
# that terrain's aliasof / mvt_alias and its village, castle and keep properties.
# ---------------------------------------------------------------------------------------------
T = []
def terrain(string, tid, name, help, aliasof, symbol, group, **kw):
    T.append(dict(string=string, id=tid, name=name, help=help, aliasof=aliasof, symbol=symbol, group=group, **kw))

SPACE_HELP = "<italic>text='Open space'</italic> is empty void. Ships move through it at full speed, but there is nothing to hide behind."
terrain('Zs', 'dw_space', 'Open Space', SPACE_HELP, 'Gt', 'space-01', 'flat')
terrain('Zsl', 'dw_space_lane', 'Space Lane', "<italic>text='Space lanes'</italic> are open space marked by navigation beacons: the roads of a map. They play as open space.", 'Gt', 'space-01', 'flat')
terrain('Zsf', 'dw_space_shoal', 'Open Space', "This open space was a ford on the original map: it plays as the better of open space and the Badlands.", 'Gt, Wst', 'space-01', 'water', editor_name='Open Space (ford)')
terrain('Zv', 'dw_dim_void', 'Dim Void', "<italic>text='Dim void'</italic> is a dark stretch of space, far from any star. It plays as cave floor.", 'Ut', 'dim-01', 'cave')
terrain('Zvh', 'dw_dim_void_rocks', 'Dim Asteroids', "Asteroids drifting in the dim void. They play as rocky cave: the better of cave floor and an asteroid field for defence, the worse for movement.", 'Ut, Ht', 'dim-01', 'cave', mvt_alias='-,Ut,Ht')
terrain('Zb', 'dw_badlands', 'Badlands', "<italic>text='The Badlands'</italic> are plasma storms that wreck navigation and shields. Ships are slow and easy to hit in them, as in shallow water. The Maquis know how to fly them.", 'Wst', 'gas-bad-0-0', 'water')
terrain('Zbd', 'dw_badlands_deep', 'Deep Badlands', "<italic>text='The deep Badlands'</italic> are the heart of the plasma storms: a barrier for most ships, as deep water is.", 'Wdt', 'gas-deep-0-0', 'water')
terrain('Zbr', 'dw_wreckage', 'Wreckage Field', "<italic>text='Wreckage fields'</italic> are Badlands strewn with the hulls of ships that did not make it. They play as a coastal reef.", 'Wrt', 'gas-bad-0-0', 'water')
terrain('Zbs', 'dw_badlands_swamp', 'Badlands Fringe', "<italic>text='The Badlands fringe'</italic> is thinner, patchier plasma. It plays as swamp.", 'St', 'gas-swamp-0-0', 'water')
terrain('Zd', 'dw_dust', 'Dust Cloud', "<italic>text='Dust clouds'</italic> clog engines and sensors. They play as sand.", 'Dt', 'gas-dust-0-0', 'desert')
terrain('Za', 'dw_ice', 'Comet Ice Field', "<italic>text='Comet ice fields'</italic> are drifts of frozen gas and ice shards. They play as frozen terrain.", 'At', 'gas-ice-0-0', 'frozen')
terrain('Zh', 'dw_asteroids', 'Asteroid Field', "<italic>text='Asteroid fields'</italic> give good cover but need careful piloting. They play as hills.", 'Ht', 'hills-01', 'rough')
terrain('Zhd', 'dw_asteroids_dust', 'Dusty Asteroids', "Asteroids in a dust cloud. They play as desert hills.", 'Dt, Ht', 'hills-01', 'rough, desert', mvt_alias='-,Dt,Ht')
terrain('Zha', 'dw_asteroids_ice', 'Icy Asteroids', "Asteroids in a comet ice field. They play as snowy hills.", 'At, Ht', 'hills-01', 'rough, frozen', mvt_alias='-,At,Ht')
terrain('Zm', 'dw_asteroids_dense', 'Dense Asteroids', "<italic>text='Dense asteroid fields'</italic> are packed with big rocks: the best cover, and slow going. They play as mountains.", 'Mt', 'mount-01', 'rough')
terrain('Zma', 'dw_asteroids_dense_ice', 'Dense Icy Asteroids', "Dense asteroids in a comet ice field. They play as snowy mountains.", 'At, Mt', 'mount-01', 'rough, frozen', mvt_alias='-,At,Mt')
terrain('Zt', 'dw_dark_matter_floor', 'Dark Matter', "<italic>text='Dark matter'</italic> swallows the light of the stars behind it. It plays as a mushroom grove's floor.", 'Tt', 'gas-dark-0-0', 'cave')
terrain('Zq', 'dw_rift', 'Subspace Rift', "<italic>text='Subspace rifts'</italic> are tears in space that no ship can enter, though some can fly over them. They play as a chasm.", 'Qt', 'rift-01', 'obstacle')
terrain('Zl', 'dw_corona', 'Stellar Corona', "<italic>text='Stellar coronas'</italic> are the burning outer layers of a star. They play as lava.", 'Qt', 'gas-corona-0-0', 'obstacle', light=25, max_light=35)
IMP = "Impassable: no ship can enter it."
terrain('Zxe', 'dw_eddy', 'Gravitational Eddy', "<italic>text='Gravitational eddies'</italic> are whirlpools in space-time that bend the starlight around them. " + IMP, 'Xt', 'eddy-01', 'obstacle')
terrain('Zxr', 'dw_radiation', 'Radiation Zone', "<italic>text='Radiation zones'</italic> are clouds of lethal radiation. " + IMP, 'Xt', 'gas-rad-0-0', 'obstacle')
terrain('Zxp', 'dw_plasma_storm', 'Plasma Storm', "<italic>text='Plasma storms'</italic> are vast, crackling storm fronts. " + IMP, 'Xt', 'gas-plasma-0-0', 'obstacle')
terrain('Zxq', 'dw_briar_patch', 'Briar Patch', "<italic>text='The Briar Patch'</italic> is a dense, metaphasic nebula that no ship can fly through. " + IMP, 'Xt', 'gas-briar-0-0', 'obstacle')
terrain('Zxn', 'dw_void', 'The Void', "<italic>text='The Void'</italic> is empty of stars and of everything else, at the edge of the known map. " + IMP, 'Xt', 'gas-void-0-0', 'obstacle')
terrain('Zxk', 'dw_black_hole', 'Black Hole', "<italic>text='Black holes'</italic> swallow anything that comes too close. " + IMP, 'Xt', 'black-hole-1', 'obstacle')
terrain('Zxj', 'dw_pulsar', 'Pulsar', "<italic>text='Pulsars'</italic> sweep space with beams of radiation. " + IMP, 'Xt', 'pulsar-1', 'obstacle')

# Castles: Zc + look + group. Looks: d = drydock (joined to a keep), b = broken drydock,
# o = defensive outpost (not joined to a keep), x = broken outpost. Groups copy the castle's alias.
CGROUPS = {'': ('Ct', None), 'a': ('Ct, At', 'ice'), 'w': ('Ct, Wst', 'bad'), 's': ('Ct, St', 'swamp'), 'r': ('Ct, Wrt', 'bad')}
CLOOKS = {'d': ('Drydock', 'dw_drydock', "<italic>text='Drydocks'</italic> are the berths of a starbase, inside its shield perimeter. Ships can be built here from the starbase's core."),
          'b': ('Ruined Drydock', 'dw_drydock_ruin', "<italic>text='Ruined drydocks'</italic> still hold together well enough for ships to be built here from a starbase's core."),
          'o': ('Defensive Outpost', 'dw_outpost', "<italic>text='Defensive outposts'</italic> are shielded platforms with no starbase core: good cover, but no ships are built here unless a core is next to them."),
          'x': ('Ruined Outpost', 'dw_outpost_ruin', "<italic>text='Ruined outposts'</italic> are abandoned defence platforms, their shields broken but still worth holding.")}
GNAME = {'': '', 'a': ' (ice)', 'w': ' (Badlands)', 's': ' (Badlands fringe)', 'r': ' (wreckage)'}
CASTLES = []
for L, (nm, tid, hp) in CLOOKS.items():
    for g, (al, gas) in CGROUPS.items():
        code = 'Zc' + L + g; CASTLES.append(code)
        terrain(code, tid + ('_' + g if g else ''), nm, hp, al, 'castle-' + L, 'castle', recruit_onto=True, editor_name=nm + GNAME[g])
KEEPS = []
for L, (nm, tid, hp) in {'': ('Starbase', 'dw_starbase', "<italic>text='Starbases'</italic> build ships: a ship at the core can build new ships onto the drydocks around it."),
                         'x': ('Ruined Starbase', 'dw_starbase_ruin', "<italic>text='Ruined starbases'</italic> can still build ships onto the drydocks around them.")}.items():
    for g, (al, gas) in CGROUPS.items():
        code = 'Zk' + L + g; KEEPS.append(code)
        terrain(code, tid + ('_' + g if g else ''), nm, hp, al, 'keep' + ('-x' if L else ''), 'castle', recruit_onto=True, recruit_from=True, editor_name=nm + GNAME[g])

# Overlays
terrain('^Zf', 'dw_nebula', 'Nebula', "<italic>text='Nebulae'</italic> hide ships and blind sensors. They play as forest.", '_bas, Ft', 'gas-neb-0-0', 'forest', mvt_alias='-,_bas,Ft')
terrain('^Zfa', 'dw_nebula_ice', 'Nebula', "A nebula over comet ice. It plays as snowy forest.", '_bas, At, Ft', 'gas-neb-0-0', 'forest, frozen', mvt_alias='-,_bas,At,Ft', editor_name='Nebula (ice)')
terrain('^Zt', 'dw_dark_matter', 'Dark Matter Nebula', "<italic>text='Dark matter nebulae'</italic> give some cover but no place to hide. They play as a mushroom grove.", '_bas, Tt', 'gas-dark-0-0', 'forest, cave', mvt_alias='-,_bas,Tt')
terrain('^Zto', 'dw_dark_matter_old', 'Dark Matter Nebula', "A dark matter nebula. It plays as an old-style mushroom grove.", 'Tt', 'gas-dark-0-0', 'forest, cave', editor_name='Dark Matter Nebula (old grove)')
terrain('^Zv', 'dw_planet', 'Planet', "<italic>text='Planets'</italic> are colonies and supply worlds: they give income and repair the ships in orbit, like villages.", '_bas, Vt', 'planet-M-1', 'village', heals=8, gives_income=True)
terrain('^Zvo', 'dw_planet_open', 'Planet', "A planet that plays as a village of the terrain under it (as merfolk villages do).", '_bas', 'planet-ocean-1', 'village', heals=8, gives_income=True, editor_name='Planet (base terrain)')
terrain('^Zr', 'dw_rubble', 'Loose Asteroids', "A few asteroids over another terrain. They play as sand rubble.", '_bas, Ht', 'hills-01', 'rough', mvt_alias='-,_bas,Ht')
terrain('^Zo', 'dw_depot', 'Supply Beacon', "A supply beacon in a dust cloud: it repairs ships, like an oasis.", 'Dt', 'beacon', 'desert', mvt_alias='_bas', def_alias='_bas', heals=8)
terrain('^Zco', 'dw_dock_overlay', 'Docking Ring', "A docking ring over another terrain: plays as a castle overlay.", '_bas', 'castle-o', 'castle', recruit_onto=True)
terrain('^Zko', 'dw_core_overlay', 'Starbase Core', "A starbase core over another terrain: plays as a keep overlay.", '_bas', 'keep', 'castle', recruit_onto=True, recruit_from=True)
BRIDGES = {'Zu': ('_bas, Gt', None, 'Navigation Buoys', "A line of navigation buoys through the Badlands: it plays as a bridge."),
           'Zw': ('Ut, _bas', None, 'Navigation Buoys', "A line of navigation buoys over a rift: it plays as a chasm bridge."),
           'Zy': ('_bas, Rt', 'Gt, Rt', 'Tractor Rail', "A tractor-beam rail: it plays as mine rails.")}
for b, (al, mvt, nm, hp) in BRIDGES.items():
    for dc, dn in (('|', 'n'), ('/', 'ne'), ('\\', 'se')):
        terrain('^' + b + dc, 'dw_' + {'Zu': 'buoys', 'Zw': 'buoys_rift', 'Zy': 'rail'}[b] + '_' + dn, nm, hp, al, 'buoys-' + dn, 'bridge', **({'mvt_alias': mvt} if mvt else {}))

# Which codes show which gas, for drawing (a hex may be in one base gas and one overlay gas).
FAM = {f: [] for f in ('bad', 'deep', 'swamp', 'dust', 'ice', 'corona', 'rad', 'plasma', 'briar', 'void', 'neb', 'dark')}
FAM['bad'] += ['Zb', 'Zbr']; FAM['deep'] += ['Zbd']; FAM['swamp'] += ['Zbs']; FAM['dust'] += ['Zd', 'Zhd']
FAM['ice'] += ['Za', 'Zha', 'Zma']; FAM['corona'] += ['Zl']; FAM['rad'] += ['Zxr']; FAM['plasma'] += ['Zxp']
FAM['briar'] += ['Zxq']; FAM['void'] += ['Zxn']; FAM['dark'] += ['Zt']
for code in CASTLES + KEEPS:
    gas = CGROUPS[code[3:] if code.startswith('Zc') else code[2:].lstrip('x')][1]
    if gas: FAM[gas].append(code)
OVERLAY_FAM = {'neb': ['^Zf', '^Zfa'], 'dark': ['^Zt', '^Zto']}
BASE_LAYER = {'bad': -900, 'deep': -900, 'swamp': -899, 'dust': -898, 'ice': -897, 'corona': -896, 'rad': -895, 'plasma': -895, 'briar': -895, 'void': -894, 'dark': -890}
OVER_LAYER = {'neb': -600, 'dark': -601}

def fam_types(f):
    """Terrain match string for every hex that shows gas family f."""
    s = [c + '^*' for c in FAM[f]] + ['*' + o for o in OVERLAY_FAM.get(f, [])]
    return ','.join(s)

# ---------------------------------------------------------------------------------------------
# Images
# ---------------------------------------------------------------------------------------------
def save(im, name):
    p = os.path.join(IMG, name + '.png'); os.makedirs(os.path.dirname(p), exist_ok=True); im.save(p, optimize=True)

def make_images():
    import art_lib as A, asteroids as AS, impassable as IM, lonecastle as LC, gases
    os.makedirs(IMG, exist_ok=True)
    HEXA = G.HEXA
    def hexcut(im):
        a = np.asarray(im.convert('RGBA'), np.float32).copy(); a[..., 3] *= HEXA; return Image.fromarray(a.astype(np.uint8))
    # starfields
    for i in range(12): save(A.starfield(i), 'space-%02d' % (i + 1))
    for i in range(6):
        s = np.asarray(A.starfield(40 + i), np.float32).copy(); s[..., :3] = s[..., :3] * 0.45 + np.array([2, 2, 4]); save(Image.fromarray(s.astype(np.uint8)), 'dim-%02d' % (i + 1))
    # gas pieces and spill masks
    for d in range(6): save(G.spill_mask(d, 30, 1.0), 'spill-' + G.DIRS[d])
    for f, (fn, _) in gases.FAMILIES.items():
        tex = fn()
        for mx in range(G.PX):
            for my in range(G.PY): save(G.cut(tex, mx, my), 'gas-%s-%d-%d' % (f, mx, my))
    # asteroids: a few rocks per hex with black space between them (D's readability rule)
    def field(seed, kind, tint=None):
        r = random.Random(seed); im = Image.new('RGBA', (72, 72)); placed = []
        fk = AS.pick_kind(r)
        for (cnt, rmin, rmax, spread) in AS.SPEC[kind]:
            for _ in range(cnt):
                R = r.uniform(rmin, rmax)
                for attempt in range(60):
                    ang = r.uniform(0, 6.283); rr = min(spread, 30 - R * 1.25) * math.sqrt(r.random())
                    cx = 36 + math.cos(ang) * rr; cy = 36 + math.sin(ang) * rr * 0.92
                    if all(math.hypot(cx - ox, cy - oy) >= AS.GAP[kind] * (R + oR) + 1.5 for ox, oy, oR in placed): break
                else: continue
                placed.append((cx, cy, R))
        placed.sort(key=lambda p: p[1])
        for cx, cy, R in placed:
            k = fk if r.random() < 0.55 else AS.pick_kind(r)
            rock = AS.CACHE.get_rock(r.randrange(10 ** 6), R, k, R > 3.5, tint)
            im.alpha_composite(rock, (int(round(cx - rock.width / 2)), int(round(cy - rock.height / 2))))
        return hexcut(im)
    for i in range(10):
        save(field(100 + i, 'hills'), 'hills-%02d' % (i + 1)); save(field(200 + i, 'mount'), 'mount-%02d' % (i + 1))
        save(field(100 + i, 'hills', (10, 45, 22)), 'hills-neb-%02d' % (i + 1)); save(field(200 + i, 'mount', (10, 45, 22)), 'mount-neb-%02d' % (i + 1))
        save(field(100 + i, 'hills', (28, 8, 42)), 'hills-dark-%02d' % (i + 1)); save(field(200 + i, 'mount', (28, 8, 42)), 'mount-dark-%02d' % (i + 1))
    # planets: class M by default, ocean worlds in the Badlands, rocky moons in asteroids, desert in dust, ice on ice
    for kind in ('M', 'ocean', 'rock', 'desert', 'ice'):
        for i in range(4):
            p = A.planet(900 + i * 7 + len(kind), 23, kind); im = Image.new('RGBA', (72, 72)); im.alpha_composite(p, (36 - p.width // 2, 36 - p.height // 2)); save(hexcut(im), 'planet-%s-%d' % (kind, i + 1))
    # small things
    save(A.beacon(), 'beacon')
    for i in range(3): save(A.debris(i), 'wreckage-%d' % (i + 1))
    for dc, dn in (('|', 'n'), ('/', 'ne'), ('\\', 'se')): save(A.buoys(dc), 'buoys-' + dn)
    # gravitational eddies: the starlight bent round a whirlpool, alternating spin
    for i in range(6):
        base = A.starfield(60 + i).convert('RGBA'); big = Image.new('RGBA', (72, 72), (5, 6, 12, 255)); big.alpha_composite(base)
        im = IM.eddies(big, [(36, 36)] if i % 2 == 0 else [(36, 36), (-500, -500)][::-1], seed=i)
        save(hexcut(im), 'eddy-%02d' % (i + 1))
    # subspace rift: a glowing crack
    for i in range(4):
        r = random.Random(70 + i); pts = []; a0 = r.uniform(0, math.pi); x, y = 36 - math.cos(a0) * 30, 36 - math.sin(a0) * 30
        for k in range(9):
            pts.append((x, y)); x += math.cos(a0) * 7.5 + r.uniform(-4, 4); y += math.sin(a0) * 7.5 + r.uniform(-4, 4)
        segs = list(zip(pts, pts[1:]))
        im = IM.glow_lines((72, 72), segs, (235, 240, 255, 255), (120, 80, 255, 200), 1.6, 7, 4)
        save(hexcut(im), 'rift-%02d' % (i + 1))
    # lone impassable hexes: Star Control's black holes and pulsars (D: reuse for impassable)
    SC = os.path.join(HERE, 'sc') + '/'   # from the Star Control add-on's own terrain art (D's)
    for i, n in enumerate(['black-hole', 'black-hole2', 'black-hole3', 'black-hole4']): save(Image.open(SC + n + '.png').convert('RGBA'), 'black-hole-%d' % (i + 1))
    save(Image.open(SC + 'pulsar.png').convert('RGBA'), 'pulsar-1')
    # castles and keeps
    tint = Image.new('RGBA', (72, 72)); ImageDraw.Draw(tint).polygon(G.HEXV, fill=(90, 180, 255, 26))
    def tinted(im):
        o = tint.copy(); o.alpha_composite(im); return o
    for i in range(3):
        save(tinted(A.arch(i, False)), 'castle-d-%d' % (i + 1)); save(A.arch(i, True), 'castle-b-%d' % (i + 1))
        save(tinted(LC.battlements(i, False)), 'castle-o-%d' % (i + 1)); save(tinted(LC.corner_turrets(i, False)), 'castle-oa-%d' % (i + 1))
    for i in range(4):
        save((LC.corner_turrets if i % 2 else LC.bunkers)(i, True), 'castle-x-%d' % (i + 1))
    save(A.station('keep', False, 0), 'keep'); save(A.station('keep', True, 0), 'keep-x')
    for d in range(6):
        save(A.shield_layer((72, 72), [(0, 0, d, False)], []), 'shield-%s' % G.DIRS[d])
        save(A.shield_layer((72, 72), [(0, 0, d, True)], []), 'shield-broken-%s' % G.DIRS[d])
        for v in range(2): save(A.wall_layer((72, 72), [(0, 0, d)], seed=d * 3 + v), 'wall-%s-%d' % (G.DIRS[d], v + 1))
    # broken outposts: each side mostly a broken shield, now and then whole or gone (D: at most one down)
    for d in range(6):
        dn = G.DIRS[d]
        for v, src in enumerate(['shield-broken-' + dn] * 3 + ['shield-' + dn, None]):
            save(Image.open(os.path.join(IMG, src + '.png')) if src else Image.new('RGBA', (72, 72)), 'shield-x-%s-%d' % (dn, v + 1))
    # editor symbols for castle looks
    for L in 'dbox':
        bg = A.starfield(0).convert('RGBA'); bg.alpha_composite(Image.open(os.path.join(IMG, 'castle-%s-1.png' % L)))
        for d in range(6): bg.alpha_composite(Image.open(os.path.join(IMG, ('shield-%s.png' if L in 'do' else 'shield-broken-%s.png') % G.DIRS[d])))
        save(bg, 'castle-' + L)

# ---------------------------------------------------------------------------------------------
# WML
# ---------------------------------------------------------------------------------------------
HEADER = "#textdomain wesnoth-Dominion_War_Wesnoth\n# Generated by terrain/tools/make_terrain.py. Edit that script, not this file.\n"

def wml_terrain():
    out = [HEADER, "# Space terrain types. Every code starts with Z, which neither core Wesnoth nor the Star Control\n# add-on (Y) uses. Each type is an alias of the Wesnoth terrain it replaces, so it plays the same.\n"]
    for t in T:
        out.append('[terrain_type]')
        out.append('    symbol_image=dw/%s' % t['symbol'])
        out.append('    id=%s' % t['id'])
        out.append('    name= _ "%s"' % t['name'])
        out.append('    editor_name= _ "%s"' % t.get('editor_name', t['name']))
        out.append('    string=%s' % t['string'])
        out.append('    aliasof=%s' % t['aliasof'])
        for k in ('mvt_alias', 'def_alias'):
            if k in t: out.append('    %s=%s' % (k, t[k]))
        for k in ('heals', 'light', 'max_light'):
            if k in t: out.append('    %s=%s' % (k, t[k]))
        for k in ('gives_income', 'recruit_onto', 'recruit_from'):
            if t.get(k): out.append('    %s=yes' % k)
        out.append('    submerge=0')
        out.append('    unit_height_adjust=0')
        out.append('    editor_group=%s' % t['group'])
        out.append('    help_topic_text= _ "%s"' % t['help'])
        out.append('[/terrain_type]\n')
    return '\n'.join(out)

def tile(x, y, typ=None, flag=None, images=(), extra=''):
    s = ['    [tile]', '        x,y=%d,%d' % (x, y)]
    if typ: s.append('        type=%s' % typ)
    if flag: s.append('        set_no_flag=%s' % flag)
    for im in images:
        s.append('        [image]')
        for k, v in im.items(): s.append('            %s=%s' % (k, v))
        s.append('        [/image]')
    s.append('    [/tile]')
    return '\n'.join(s)

def rule(*tiles, mod=False, prob=None):
    s = ['[terrain_graphics]']
    if mod: s += ['    mod_x=%d' % G.PX, '    mod_y=%d' % G.PY]
    if prob: s.append('    probability=%d' % prob)
    s += list(tiles); s.append('[/terrain_graphics]')
    return '\n'.join(s)

def var(n, width=2):
    return ';'.join(('%0' + str(width) + 'd') % i for i in range(1, n + 1)) if width else ';'.join(str(i) for i in range(1, n + 1))

# neighbour offsets for a single-hex rule anchored at (2, 2): an even column, all offsets positive
def nb(d):
    return G.neighbour(2, 2, d)

def wml_graphics():
    R = [HEADER, "# Drawing rules for the space terrain. Images live in images/terrain/dw/.\n"
         "# Layers, back to front: starfield -1000, base gas -900, overlay gas (nebulae) -600, asteroids -500,\n"
         "# planets and buoys -300, stations -250, shield edges -200. All behind ships.\n"]
    ALL_CASTLE = ','.join(c + '^*' for c in CASTLES + KEEPS)
    # 1. base: starfield (dim void and eddies have their own)
    R.append('# 1. Base layer')
    R.append(rule(tile(0, 0, 'Zv^*,Zvh^*', 'base', [dict(name='dw/dim-@V.png', variations=var(6), layer=-1000)])))
    R.append(rule(tile(0, 0, 'Zxe^*', 'base', [dict(name='dw/eddy-@V.png', variations=var(6), layer=-1000)])))
    R.append(rule(tile(0, 0, 'Z*^*', 'base', [dict(name='dw/space-@V.png', variations=var(12), layer=-1000)])))
    # 2. gas: each hex shows its piece of the family's repeating texture
    R.append('\n# 2. Gas. Each hex shows the piece of its gas at its place in a pattern that repeats every %dx%d hexes,\n#    so neighbouring hexes of one gas join up. Gas also spills softly into every neighbour without it.' % (G.PX, G.PY))
    for f in FAM:
        typ = fam_types(f); layer = OVER_LAYER.get(f, BASE_LAYER.get(f)) if f in OVERLAY_FAM else BASE_LAYER[f]
        if f == 'neb': layer = OVER_LAYER['neb']
        if not typ: continue
        R.append('# %s' % f)
        for mx in range(G.PX):
            for my in range(G.PY):
                R.append(rule(tile(mx, my, typ, 'gas_' + f, [dict(name='dw/gas-%s-%d-%d.png' % (f, mx, my), layer=layer)]), mod=True))
        for mx in range(G.PX):
            for my in range(G.PY):
                for d in range(6):
                    nx, ny = G.neighbour(mx, my, d)
                    sx = G.PX if nx < 0 else 0; sy = G.PY if ny < 0 else 0   # keep every tile position >= 0
                    R.append(rule(tile(mx + sx, my + sy, '!,' + typ + ',_off^_usr', 'spill_%s_%s' % (f, G.DIRS[d]),
                                       [dict(name='"dw/gas-%s-%d-%d.png~MASK(terrain/dw/spill-%s.png)"' % (f, mx, my, G.DIRS[d]), layer=layer - 1)]),
                                  tile(nx + sx, ny + sy, typ), mod=True))
    # 3. things in hexes
    R.append('\n# 3. Asteroids, planets, beacons, buoys, eddies, stellar bodies')
    rocks = [('Zm^Zf*,Zma^Zf*', 'mount-neb'), ('Zm^Zt*,Zma^Zt*', 'mount-dark'), ('Zm^*,Zma^*', 'mount'),
             ('Zh*^Zf*,Zvh^Zf*,*^Zr', 'hills-neb'), ('Zh*^Zt*,Zvh^Zt*', 'hills-dark'), ('Zh*^*,Zvh^*', 'hills')]
    for typ, stem in rocks:
        R.append(rule(tile(0, 0, typ, 'rocks', [dict(name='dw/%s-@V.png' % stem, variations=var(10), layer=-500)])))
    planets = [('Zb*^Zv*', 'ocean'), ('Zh^Zv*,Zm*^Zv*,Zha^Zv*,Zvh^Zv*', 'rock'), ('Zd^Zv*,Zhd^Zv*', 'desert'), ('Za^Zv*', 'ice'), ('*^Zv*', 'M')]
    for typ, kind in planets:
        R.append(rule(tile(0, 0, typ, 'planet', [dict(name='dw/planet-%s-@V.png' % kind, variations=var(4, 0), layer=-300)])))
    R.append(rule(tile(0, 0, 'Zsl^*', 'beacon', [dict(name='dw/beacon.png', layer=-800)])))
    R.append(rule(tile(0, 0, '*^Zo', 'beacon', [dict(name='dw/beacon.png', layer=-300)])))
    R.append(rule(tile(0, 0, 'Zbr^*', 'wreckage', [dict(name='dw/wreckage-@V.png', variations=var(3, 0), layer=-800)])))
    for dc, dn in (('|', 'n'), ('/', 'ne'), ('\\', 'se')):
        R.append(rule(tile(0, 0, '*^Zu%s,*^Zw%s,*^Zy%s' % (dc, dc, dc), 'buoys', [dict(name='dw/buoys-%s.png' % dn, layer=-300)])))
    R.append(rule(tile(0, 0, 'Zq^*', 'rift', [dict(name='dw/rift-@V.png', variations=var(4), layer=-900)])))
    R.append(rule(tile(0, 0, 'Zxk^*', 'body', [dict(name='dw/black-hole-@V.png', variations=var(4, 0), layer=-500)])))
    R.append(rule(tile(0, 0, 'Zxj^*', 'body', [dict(name='dw/pulsar-1.png', layer=-500)])))
    # 4. castles and keeps
    R.append('\n# 4. Starbases. Drydocks and outposts sit inside a shield perimeter, drawn on each side that faces\n#    something other than a castle or keep. Ruined drydocks get a broken wall of girders instead, and ruined\n#    outposts a broken shield.')
    R.append(rule(tile(0, 0, ','.join(k + '^*' for k in KEEPS if 'x' not in k[2:]), 'station', [dict(name='dw/keep.png', layer=-250)])))
    R.append(rule(tile(0, 0, ','.join(k + '^*' for k in KEEPS if 'x' in k[2:]), 'station', [dict(name='dw/keep-x.png', layer=-250)])))
    by = lambda L, gs=None: ','.join('Zc' + L + g + '^*' for g in CGROUPS if gs is None or g in gs)
    R.append(rule(tile(0, 0, by('d'), 'station', [dict(name='dw/castle-d-@V.png', variations=var(3, 0), layer=-250)])))
    R.append(rule(tile(0, 0, by('b'), 'station', [dict(name='dw/castle-b-@V.png', variations=var(3, 0), layer=-250)])))
    # D: battlements (B) for an empty outpost, corner turrets (A) when something shows inside it
    R.append(rule(tile(0, 0, by('o', ['']), 'station', [dict(name='dw/castle-o-@V.png', variations=var(3, 0), layer=-250)])))
    R.append(rule(tile(0, 0, by('o', ['a', 'w', 's', 'r']), 'station', [dict(name='dw/castle-oa-@V.png', variations=var(3, 0), layer=-250)])))
    R.append(rule(tile(0, 0, by('x'), 'station', [dict(name='dw/castle-x-@V.png', variations=var(4, 0), layer=-250)])))
    shielded = ','.join([by('d'), by('o')] + [k + '^*' for k in KEEPS if 'x' not in k[2:]])
    walled = ','.join([by('b')] + [k + '^*' for k in KEEPS if 'x' in k[2:]])
    for d in range(6):
        x, y = nb(d); dn = G.DIRS[d]
        R.append(rule(tile(2, 2, shielded, 'edge_' + dn, [dict(name='dw/shield-%s.png' % dn, layer=-200)]), tile(x, y, '!,' + ALL_CASTLE)))
        R.append(rule(tile(2, 2, walled, 'edge_' + dn, [dict(name='dw/wall-%s-@V.png' % dn, variations='1;2', layer=-200)]), tile(x, y, '!,' + ALL_CASTLE)))
        # broken outposts: mostly broken shield, now and then a whole side or none (D)
        R.append(rule(tile(2, 2, by('x'), 'edge_' + dn, [dict(name='dw/shield-x-%s-@V.png' % dn, variations=var(5, 0), layer=-200)]), tile(x, y, '!,' + ALL_CASTLE)))
    return '\n\n'.join(R) + '\n'

if __name__ == '__main__':
    if '--wml' not in sys.argv: make_images()
    open(os.path.join(ROOT, 'terrain.cfg'), 'w').write(wml_terrain())
    open(os.path.join(ROOT, 'terrain-graphics.cfg'), 'w').write(wml_graphics())
    print('terrain types:', len(T), ' images:', len(os.listdir(IMG)))
