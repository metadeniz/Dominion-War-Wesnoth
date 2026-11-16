# Space tileset for standard Wesnoth maps (proposal 1, 16 Nov 2026)

Goal (D): an alternate tileset for this mod, so that existing Wesnoth maps can be played with our own space terrain art.

Mockup of The Freelands in this style: `tileset/mockup-freelands.png` (whole map) and `tileset/mockup-freelands-detail.png` (close-up at game scale, 72px hexes). It's procedural placeholder art, put together the way Wesnoth would layer the tiles. It shows the mapping and the overall look, not finished art. The stars, black holes and protostar on the impassable hexes are the Star Control add-on's own images, which D said we can reuse for impassable terrain.

## Approach: swap the terrain when the game starts

**Recommended.** The era carries a `prestart` event (a few lines of WML plus a small Lua function) that turns every hex of whatever map was picked into the matching space terrain before the first turn. The `.map` files stay untouched, so any 2p–6p map works with the Star Trek era, including maps downloaded later and random maps.

- Each space terrain is a new terrain code (prefix `Z`, so it can't clash with core Wesnoth or with Star Control's `Y` codes) declared as an *alias* of the Wesnoth terrain it replaces. Movement and defence rules still see "forest", "hills" and so on, so the hull tables in `unit-stats.md` work unchanged, and mixed hexes (hills with forest, a village in a swamp) keep Wesnoth's "best of" and "worst of" rules.
- Base and overlay layers are converted separately: `Hh^Fp` (forested hills) becomes an asteroid field with a nebula over it.
- The game shows the new names (Nebula, Asteroid Field, Badlands…) in the terrain tooltip and help.
- The same table also goes into a small `convert_map.py`, as Star Control has, for writing hand-polished space versions of a map for the editor.

Limits: the lobby's map preview and the map editor still show the original green map (only the game converts). If a scenario's own events test for specific terrain codes, they won't match after the swap. That's rare in multiplayer maps and doesn't matter for plain `.map` files.

**Not recommended: overriding Wesnoth's own terrain images** (keeping the codes and swapping the pictures). It would mean redrawing hundreds of core transition and castle-corner images to fit Wesnoth's drawing rules, and tooltips would still say "Pine Forest".

## Why these translations

Rule: **every space terrain keeps the gameplay role of the Wesnoth terrain it replaces**, and the art uses the Star Trek phenomenon that plays that same role on screen. That keeps each map's balance (distances, choke points, defensive lines) exactly as its designer made it, and the hull tables stay valid.

| Wesnoth terrain: its role in a map | Star Trek equivalent: why it fits |
|---|---|
| Forest: cover, slows movement, places to hide and ambush | **Nebula**: in Trek, nebulae hide ships and blind sensors (the Mutara Nebula in *Wrath of Khan*; the Maquis hiding in nebulae). It also fits the roster's *nebula cloak*. |
| Hills: good defence, a bit slow | **Asteroid field**: rocks give cover but need careful piloting |
| Mountains: best defence, slow, hard for big units | **Dense asteroids**: the same, more so; capital ships struggle (4 moves, 30% in `unit-stats.md`) |
| Impassable: walls that shape the map | **Stellar bodies**: no ship flies through a star or a black hole |
| Village: income, repairs, owned by a side | **Planet**: a colony or supply world |
| Castle and keep: where you recruit | **Starbase**: a shipyard with docking modules |
| Swamp: slow, poor defence | **Badlands** (D, 16 Nov): the same plasma storms as water, so swamp and water read as one hazard |
| Sand: slowish, poor defence | **Dust cloud** |
| Frozen | **Comet ice field** |
| Mushroom grove | **Dark matter nebula** (D, 16 Nov): some cover, but no hiding |
| Cave floor | **Dim void** (only used in cave maps) |
| Chasm, lava | **Subspace rift** / **stellar corona** |

Each family gets its own colour so it reads at a glance at 72px: nebulae green, dark matter purple, Badlands red and orange, dust brown, asteroids as grey 3D rocks.

## Decided (D, 16 Nov)

- Water option C: fords become open space; shallow water, reefs and deep water become the Badlands.
- Castles: not all starbases (D). Keeps stay starbases; castle hexes sit inside a glowing **shield perimeter** with emitter pylons along the outer edge, like castle walls and towers (D: "A is better"). Ruined castles get a **physical perimeter** (armour plates and girders, breached and scorched) instead. What goes inside the perimeter: four ideas in `tileset/castle-interiors.png` (hangar deck, docking clamps, defence grid, repair gantries); recommended: hangar deck. D then asked for Utopia Planitia-style drydocks: four proposals in `tileset/castle-utopia-planitia.png` (U1 arched-rib drydocks, U2 lattice cages, U3 over Mars, U4 working yard); **Picked: U1, arched-rib drydocks (D: "u1 is good").**
- Fords are plain open space, with no lanes (D, 16 Nov: "nix the fords for now"). Reefs as Badlands with hull wreckage; bridges as lines of navigation buoys. Tropical forest nebulae are teal, not orange, so they don't read as Badlands. Four water maps compared: `tileset/water-*.png`.
- Badlands art (D, 16 Nov): "use the star control's theme of wispy currents, but use your existing reddish colors", plus DS9-style prototypes from thin to full. Four prototypes: `tileset/badlands-*.png` (currents, DS9 thin, DS9 thick, DS9 full). **Picked: 1, wispy currents (D: "lets go with 1 for now").** Deep water is drawn denser and darker, with fewer glints (`tileset/badlands-currents-deep.png`). Renderer: `tileset/src/badlands.py`.
- Mushroom groves become **dark matter nebulae** (D): no hiding bonus (left out of the nebula cloak's terrains), but some defence, which may vary by ship type or faction. Proposal for `unit-stats.md`: light 2 moves / 50%, cruiser 2 / 40%, capital 2 / 30%; **D: Maquis ships and the Breen warship get a bonus there** The exact numbers (base and bonus) belong to the unit stats work in `unit-stats.md`; the values here are only a starting suggestion.
- Colours (D, 16 Nov): **every forest is a green nebula**, whatever the forest type; **purple is reserved for dark matter nebulae**; other colours stay free for other terrain. Hills or mountains with forest (or with mushrooms) are the nebula with rocks and debris drawn inside it. Rendered: `tileset/freelands-v2.png`.
- Asteroids reworked after Star Control (D, 16 Nov: "improve the rocky areas"): lumpy, pitted, cratered rocks in mixed grey, brown and dark colours, lit like the ships (key from the right, rim from back left). **Readability rule: if you can see black space through it, ships can fly through it.** Passable fields are spaced out like Star Control's hill tile (D: "it makes the map look less noisy" and "clearer that they are passable"): hills are a few separate rocks with black gaps, mountains a few bigger rocks with smaller gaps, no grit spill and no haze. Impassable rubble is the opposite, a solid pile of boulders in thick brown dust. Sheet: `tileset/asteroids-passable-vs-impassable.png`. Renders: `tileset/asteroids-*.png`; renderer `tileset/src/asteroids.py`.
- Impassable objects (D, 16 Nov): **3-hex objects, not 4-hex**, as Star Control's small objects: one image centred on the corner three mutually adjacent impassable hexes share. Where the impassable terrain sits among rocks (impassable mountains always do), the object has a **debris disk** (Star Control's rocky supergiants and protostars) or a **band of rocks drawn in front** of it (black holes, dark stars). **Never planets** for impassable terrain (the brown dwarf is dropped as it reads as a planet). Objects keep at least one hex between them; impassable hexes not covered by a triangle (lone hexes, pairs, thin lines) are rubble walls.
- Impassable terrain (D, 16 Nov): the rubble wall is dropped (D: "I really hate the rubble wall look"). Impassable hexes (impassable mountains ^Xm and cave/stone walls X*) are drawn by the **shape of each cluster**, decided when the map is converted: clusters touching the map border are **the Void** (VOY "Night"; never inside a map, D); thick blobs are zones: **plasma storm** for big ones (deep blue, lightning), otherwise **radiation zone** (after Star Control's, in yellow) or **Briar Patch** (toned down); thin lines are chains of **gravitational eddies** (colourless lensing whirlpools); lone hexes are Star Control's 1-hex **black holes and pulsars**, with an eddy now and then. Zone centrepieces (3-hex): globular cluster in radiation zones, none in the Briar Patch (D: the debris disk does not go with it), supergiant in plasma storms (with a debris disk on impassable mountains). D's notes for later: a ship graveyard would have to be passable; minefields would be single-hex. Renders: `tileset/impassable-*.png`; code `tileset/src/impassable.py`. Open: most mainline walls are thin, so eddies dominate on maze maps (Arcanclave Citadel).
- Swamp also becomes the Badlands (in place of ion storms). It still plays as swamp. In `unit-stats.md` the "Ion storm or gas giant" row already sets swamp's costs, so that row now stands for the Badlands, and *Badlands pilots* apply there as written.

## Water: options

Water matters more than it looks. Across 25 mainline 1.18 multiplayer maps, water is a median **20% of the playable hexes**, and up to 48% (Hornshark Island) and 60% (Ruphus Isle). About half of it is **fords**, which already play as flat ground for land units; the rest (shallow and deep water) is what makes rivers, lakes and coasts into barriers and choke points. Comparison image on Hornshark Island: `tileset/water-options-hornshark.png`.

**A. Ignore water: all of it becomes open space.**
- Pros: least art and rules work; the cleanest, emptiest look, which feels most like space; ships fly freely.
- Cons: the map's barriers disappear. Rivers and lakes stop being choke points, coasts stop protecting flanks, and island maps lose their shape entirely (see the image). Distances to villages and starts change, so the designer's balance no longer holds; on watery maps every side can reach everything quickly. Water villages and castles float in empty space (harmless).

**B. All water becomes Badlands, fords included.**
- Pros: every map plays as designed.
- Cons: fords are meant to be cheap crossings, and making them storms changes that. It's also a lot of red: a fifth of The Freelands (first mockup).

**C. Hybrid (recommended):** fords become open space; shallow water and reefs become **Badlands**; deep water becomes **deep Badlands**.
- Pros: the barriers stay where the map maker put them, and fords stay free crossings with no gameplay change at all (they keep their flat-or-water rule). Much less red than B. Badlands are canon (the Maquis' home ground) and already have a rule: the Maquis *Badlands pilots* ability.
- Cons: needs Badlands rows in the hull tables. Island maps still have broad storm borders (Ruphus Isle).

## Terrain mapping

Every terrain class in Wesnoth 1.18 is covered. "Plays as" is the Wesnoth class the space terrain stays an alias of, so its cost and defence come from the ship's movetype.

| Wesnoth terrain | Space terrain | Plays as | Look |
|---|---|---|---|
| Grass, dirt, roads, floors | **Open space** | flat | Starfield. Roads get small amber nav beacons, so the map's lanes still read. |
| Forest (overlay) | **Nebula** | forest | Green clouds spilling past the hex edge (D: all forests green). With hills or mountains under it: rocks and debris inside the nebula. |
| Hills | **Asteroid field** | hills | A few separate cratered rocks with black space between them |
| Mountains | **Dense asteroid field** | mountains | Bigger rocks, smaller gaps, still see-through |
| Impassable mountains, cave and stone walls | **Stellar body** (star, black hole, giant, protostar, cluster) | impassable | 3-hex stars, protostars and black holes from Star Control's art, each with a debris disk or rocks in front; never planets. The rest of the cluster, and lone impassable hexes, are rubble walls: a solid pile of boulders in thick brown dust. |
| Village (overlay) | **Planet** | village | Class M by default. Ocean world for water and swamp villages, ice for snowy ones, desert for desert ones, rocky moon for hill and mountain ones. |
| Castle | **Arched-rib drydocks** (Utopia Planitia, U1) around the starbase | castle | Shield perimeter with emitter pylons on the outer edge; arched ribs on two rails in each berth. Ruins: broken physical perimeter and broken ribs |
| Castle not connected to a keep | **Defensive outpost** (D) | castle | Same hexagonal shield perimeter as other castles, centre left empty for the unit, dressing only near the walls. Intact: **B battlements** (armour plates with running lights along each wall); **A corner turrets** when something shows inside the hex (badlands under a water castle, swamp, nebula). Ruined: walls mostly broken up with at most one down, dressing from A or D (bunkers) wrecked and scorched. Water castles (Chw, Cm) get a patch of badlands. See `tileset/lone-castle-prototypes.png`, `tileset/lone-castles-outposts.png` |
| Keep | **Starbase core** | castle (keep) | Central hub with running lights |
| Swamp | **Badlands** (D, 16 Nov) | swamp | A lighter, patchier plasma than water, so swamp is still told apart in play |
| Shallow water | **Badlands** (plasma storm) | shallow water | Red and orange plasma filaments, as in the DS9 and Voyager Badlands. Rivers become plasma streams. |
| Ford | **Open space** (water option C) | best of flat and shallow water (as now) | Plain starfield (D: no ford lanes for now) |
| Deep water | **Deep Badlands** | deep water | Dense, darker plasma |
| Coastal reef | **Wreckage field** | reef | Badlands with hull debris |
| Sand, beach, dunes | **Dust cloud** | sand | Brown haze |
| Snow, ice | **Comet ice field** | frozen | Pale blue ice shards |
| Cave floor | **Dim void** | cave | Darker starfield |
| Mushroom grove, mycelium | **Dark matter nebula** (D, 16 Nov) | fungus | A cloud darker than space that swallows the stars behind it, with a faint violet lensing rim |
| Chasm, lava | **Subspace rift** / **stellar corona** | unwalkable | Glowing crack / orange plasma |
| Bridges | **Navigation buoys** over the Badlands | as now (best of flat and water) | A line of beacons |
| Flowers, stones and other decorations | (dropped) | as now | Open space |

## Open points for D

1. **The rest of the mapping above** (water and swamp are decided). The roster's terrain list (`faction-rosters.md`) has only six space terrains. The extra ones (Badlands on water, dust, ice, dark nebula, anomaly, rift) need costs and defences in the hull tables (`unit-stats.md`, section 1). I'd base them on Wesnoth's own costs for those classes, which keeps each map's balance (for example, deep water stays a barrier for big ships).
2. **Nebulae reduce visibility** (from Star Control). Wesnoth supports this directly: a movetype can give terrain a *vision cost*. Nebulae at vision cost 3 and the Badlands at 2 would let ships hide behind nebula walls. This changes the rules, so it's for D to decide.
3. **Asteroids raise defence:** this already follows from hills and mountains (light hulls 60% in asteroid fields).

## Art plan, after D's go-ahead

- **3D objects** (asteroids, planets, starbase modules and cores): rendered with the ship pipeline (`sprites/roster/src`) and the default lighting C from `lighting-preferences.md`, with the key light from the right as Wesnoth requires. No ground shadows, since nothing sits on a ground in space.
- **Gas** (nebulae, Badlands, dust, anomalies): procedural 2D, drawn larger than a hex and centred on it, so neighbouring hexes merge into one cloud and no hex edges show. Because every space hex sits on the same starfield, no Wesnoth-style transition tiles are needed.
- **Stellar bodies:** Star Control's black holes, giants, stars, protostars, pulsar and globular cluster.
- Roughly 20 terrain types and 100–130 images, plus the WML (terrain types, drawing rules, prestart conversion) and editor icons.
- Possible later: a faction beacon in place of Wesnoth's village flag on planets, and animated Badlands plasma.
