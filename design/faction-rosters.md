# Star Trek Wesnoth: Faction Rosters (draft 2)

Four factions for the Dominion War (2373–2375): **Federation**, **Klingon Empire**, **Dominion Alliance** and the **Maquis**. Romulans are on hold.

## Roster rules

- **On screen only.** Every ship appears on screen. Nothing is invented. Where a ship comes from outside DS9 or is rarely seen, the notes say so.
- **Right era.** No pre-warp or sublight ships (so no Bajoran lightships or sub-impulse raiders) and nothing from the future (so no Olympic class).
- **At most 11 ships per faction.** If canon doesn't have 11 good ships for a faction, the roster stays short.
- **One model per ship.** Every ship has a 3D model and a sprite (see `sprites/roster/`), rendered at the 45° camera angle chosen for all ship sprites.

## Costs

Ship prices follow one formula: **cost = HP ÷ 4 + melee ÷ 5 + ranged × 0.3 + ability gold − 1**. See `cost-formula.md` for the ability table and how each ship fits. The up-to-date stats and prices are in `unit-stats.md`.

## How levels work: crew experience, not new ships

A ship never turns into another ship. Every class is recruited as itself, and its level stands for how experienced its crew is.

| Level | Crew | Change from Green (first guess) |
|---|---|---|
| 0 | Auxiliary (shuttles, freighters) | Cheap support craft. Advances to a Green crew. |
| 1 | Green | Base stats. This is what you recruit. |
| 2 | Veteran | +20% HP, +1 damage on every attack, +5% defence |
| 3 | Elite | +40% HP, +2 damage on every attack, +10% defence, and one extra strike on the main weapon |
| AMLA | Legendary | +3 HP and a full repair each time, as in Wesnoth |

In WML, each class gets three unit types, for example `Galaxy (Green)`, `Galaxy (Veteran)` and `Galaxy (Elite)`, all using the same sprite. A rank badge could show the level. Bigger ships cost more and need more XP to level up.

Every ship is a **level 1 recruit**, except one small level 0 ship per faction.

---

## 1. Shared rules

### Damage types

| Type | Wesnoth analogue | Comes from |
|---|---|---|
| **Phaser** | blade | Federation phasers, Cardassian spiral-wave disruptors |
| **Disruptor** | pierce | Klingon disruptors and mercenary weapons |
| **Torpedo** | impact | Photon and quantum torpedoes |
| **Plasma** | fire | Maquis improvised weapons |
| **Polaron** | arcane | Jem'Hadar polaron beams (cut through shields) |
| **Kinetic** | cold | Ramming and boarding |

*Ranged* attacks are beams and torpedoes. *Melee* attacks are point-blank fire, ramming and boarding.

### Terrain

| Terrain | Plays like | Notes |
|---|---|---|
| Open space | flat | Default |
| Nebula | forest | Blocks sight, good cover |
| Asteroid field | hills or mountains | Defence bonus, slow to cross; small ships cross it better |
| Planet orbit | village | Income and repairs |
| Starbase or station | castle | Recruiting hex |
| Ion storm or gas giant | swamp | Slows ships and weakens shields |

### Abilities

| Ability | Wesnoth equivalent | Effect |
|---|---|---|
| **Cloak** | ambush (everywhere) | Invisible unless next to an enemy or within 3 hexes of a *Sensors* ship |
| **Sensors** | none (new) | Reveals cloaked ships within 3 hexes |
| **Repairs +4** | heals +4 | Adjacent friendly ships recover HP |
| **Command** | leadership | Lower-level adjacent allies deal more damage |
| **Evasive** | skirmisher | Ignores enemy zones of control |
| **Fleet tactics** | backstab | Double damage when an ally is on the far side of the target |
| **Targeting lock** | marksman | At least 60% to hit when attacking |
| **Energy dampener** | slows | Halves the target's damage and movement for a turn |
| **Ramming speed** | berserk | Melee only: fights until one ship is destroyed |
| **Plunder** | none (new) | +3 gold when this ship destroys an enemy |
| **Glory** (Klingon trait) | none (new) | Regains 8 HP after destroying an enemy |
| **Ketracel supply** | heals (Jem'Hadar only) | Jem'Hadar ships next to it recover 8 HP. Jem'Hadar ships can't be repaired any other way except at planets and stations. |

---

## 2. Federation (lawful), 7 ships + 1 leader-only ship

The most ships, the best repairs and good sensors. Strong all-rounders, but pricey at the top.

| Ship | Lvl | Role | Cost | HP | MP | Attacks (damage-strikes) | Abilities | On screen |
|---|---|---|---|---|---|---|---|---|
| Danube-class runabout | 0 | Scout, light ship | 10 | 24 | 7 | phaser 4-2, micro-torpedo 6-1 | Sensors | DS9 throughout |
| Miranda-class | 1 | Cheap line ship | 14 | 36 | 5 | phaser 5-3, torpedo 8-2 | — | DS9 fleet battles ("Sacrifice of Angels", "What You Leave Behind") |
| Excelsior-class | 1 | Battleship of the line | 20 | 50 | 5 | phaser 7-3, torpedo 11-2 | — | DS9 throughout |
| Intrepid-class | 1 | Fast science cruiser | 22 | 44 | 7 | phaser 7-3, torpedo 10-2 | Sensors, repairs +4 | DS9 "Inter Arma Enim Silent Leges" (one appearance) |
| Akira-class | 1 | Torpedo carrier | 24 | 52 | 5 | phaser 6-3, torpedo 12-3 | Targeting lock | DS9 fleet battles |
| Nebula-class | 1 | Heavy cruiser | 26 | 58 | 5 | phaser 8-3, torpedo 12-2 | Sensors | DS9 throughout (sprite uses the triangular-pod version) |
| Galaxy-class | 1 | Flagship | 34 | 72 | 5 | phaser array 9-4, torpedo 14-2 | Command, repairs +4 | DS9 throughout |

**Leaders:** Excelsior, Nebula, Galaxy, and the Defiant as a leader-only ship (not recruitable).

**Leader-only:** Defiant-class: Glass-cannon escort, 25, 44, 6, pulse phaser 9-3, quantum torpedo 14-1, Evasive, DS9 seasons 3–7.

Left out: Centaur, Saber and Steamrunner (dropped from the roster), Norway (only in *First Contact*), Ambassador and Oberth (in DS9 only in the 2367 Wolf 359 flashback), Sovereign (never in DS9), Nova and Prometheus (Voyager only), Olympic (only in a future timeline).

---

## 3. Klingon Empire (chaotic), 7 ships + 1 leader-only ship

All attack, no healers. Klingons recover by winning (*Glory*), and their Birds-of-Prey cloak. Canon only has six ship types in this era. Two older 22nd-century ships from *Enterprise*, the Raptor and the D5, were added at D's request. Their prices are drafts (the Raptor is an older scout with no cloak, so it costs less than the B'rel; the D5 is an older, smaller battle cruiser, so it costs less than the K't'inga), and their other stats are still to be written.

| Ship | Lvl | Role | Cost | HP | MP | Attacks | Abilities | On screen |
|---|---|---|---|---|---|---|---|---|
| Klingon freighter (Noggra's ship) | 0 | Transport, boarding craft | 10 | 30 | 5 | disruptor 4-2, boarding party 6-2 (melee) | — | DS9 "Sons of Mogh" (see note) |
| Raptor-class scout | 1 | Scout | 13 | ? | ? | stats still to be written | — | ENT "Sleeping Dogs" (22nd century, 145 m) |
| B'rel-class Bird-of-Prey | 1 | Raider, scout | 15 | 30 | 7 | disruptor 5-3, torpedo 8-1 | Cloak | DS9 throughout, the most common Klingon ship |
| D5-class battle cruiser | 1 | Older battlecruiser | 16 | ? | ? | stats still to be written | — | ENT "Marauders", "Judgment", "The Augments", "Divergence" (22nd century, 155 m) |
| K't'inga-class | 1 | Line battlecruiser | 18 | 46 | 5 | disruptor 6-3, torpedo 10-2, ram 8-2 (melee) | — | DS9, up to the finale |
| K'Vort-class Bird-of-Prey | 1 | Heavy raider | 21 | 44 | 6 | disruptor 7-3, torpedo 12-1 | Cloak | TNG/DS9 (the B'rel design, scaled up) |
| Vor'cha-class | 1 | Attack cruiser | 25 | 58 | 5 | disruptor 8-3, torpedo 12-2, ram 10-2 | — | DS9 fleet battles |

**Leaders:** K'Vort, Vor'cha, and the Negh'Var as a leader-only ship (not recruitable).

**Leader-only:** Negh'Var-class: Flagship, 34, 80, 4, disruptor 10-4, torpedo 15-2, ram 14-2, Command, DS9 "The Way of the Warrior" and later.

**Note on the freighter:** the Klingon ship in "Sons of Mogh" (Noggra's ship) is the Promellian battlecruiser studio model from TNG "Booby Trap", painted green. The sprite uses the Star Trek Online "Promellian Command Battlecruiser" model D supplied, tinted Klingon green.

---

## 4. Dominion Alliance, 6 ships + 1 leader-only ship

Three races, each with a clear job:

- **Jem'Hadar (chaotic):** the hardest hitters. They fight to the death when ramming, but they only repair next to a Vorta-led ship (*Ketracel supply*) or at planets and stations.
- **Cardassians (lawful):** the cheap, disciplined main line, strong in numbers (*Fleet tactics*). With the freighter gone, Cardassian and Breen ships only repair at planets and stations, so the Dominion has no field repairs.
- **Breen (neutral):** one specialist ship with an energy dampener. Only one Breen design appears on screen, so there is only one Breen ship.

| Ship | Lvl | Race | Role | Cost | HP | MP | Attacks | Abilities | On screen |
|---|---|---|---|---|---|---|---|---|---|
| Hideki-class | 0 | Cardassian | Cheap patrol | 10 | 26 | 7 | disruptor 4-3 | — | DS9 |
| Galor-class | 1 | Cardassian | Line cruiser | 15 | 42 | 5 | spiral disruptor 6-3 | Fleet tactics | DS9 throughout |
| Jem'Hadar attack ship | 1 | Jem'Hadar | Assault | 17 | 38 | 6 | polaron beam 6-3, ramming 12-1 (melee) | Ramming speed | DS9, the most common Dominion ship |
| Keldon-class | 1 | Cardassian | Heavy cruiser | 21 | 54 | 5 | spiral disruptor 8-3, torpedo 10-2 | Fleet tactics | DS9 |
| Breen warship | 1 | Breen | Disabler | 22 | 50 | 6 | disruptor 7-3, energy dampener 6-2 | Energy dampener, resists phaser 30% | DS9 "Penumbra" onward |
| Jem'Hadar battle cruiser | 1 | Jem'Hadar | Vorta command ship | 28 | 64 | 5 | polaron beam 8-4, polaron torpedo 13-2 | Command, Ketracel supply | DS9 seasons 5–7 |

**Leaders:** Galor (a Gul), Breen warship (a Thot), Jem'Hadar battle cruiser (a Vorta), and the Jem'Hadar battleship as a leader-only ship (not recruitable).

**Leader-only:** Jem'Hadar battleship: Siege flagship, 40, 92, 4, polaron beam 10-4, polaron torpedo 16-2, Command, Ketracel supply, DS9 "Valiant", "What You Leave Behind".

---

## 5. Maquis (neutral), 6 ships + 3 leader-only ships

Rebel cells flying whatever they can get: their own raiders and fighters, Bajoran ships, hired mercenaries, a stolen Starfleet cruiser, the stolen Defiant and a reprogrammed Cardassian missile. This is the smallest roster.

| Ship | Lvl | Group | Role | Cost | HP | MP | Attacks | Abilities | On screen |
|---|---|---|---|---|---|---|---|---|---|
| Bajoran freighter | 0 | Bajoran | Supply, transport | 14 | 40 | 4 | phaser 3-2 | Repairs +4 | DS9 season 4 to 7 opening credits, "Past Prologue", "The Circle", "The Siege" |
| Maquis fighter (Peregrine-class) | 1 | Maquis | Fast fighter | 11 | 24 | 8 | phaser 4-3, micro-torpedo 7-1 | Evasive | TNG "Preemptive Strike", DS9 "The Maquis"; Starfleet flies the same design as an attack fighter in "Sacrifice of Angels" |
| Maquis raider | 1 | Maquis | Ambusher | 15 | 30 | 7 | phaser 5-3, torpedo 9-1 | Evasive, cloak in nebulae | DS9 and Voyager, the most common Maquis ship |
| Mercenary raider (Baran's) | 1 | Mercenary | Raider | 16 | 36 | 7 | disruptor 6-3 | Plunder, fleet tactics | TNG "Gambit" (2368, not DS9) |
| Bajoran assault vessel | 1 | Bajoran | Heavy fighter | 17 | 40 | 7 | phaser 6-3, torpedo 10-2 | Evasive | TNG "Preemptive Strike"; DS9 "Shadows and Symbols", "Image in the Sand". The most heavily armed Bajoran ship |
| Dreadnought (ATR-4107) | 1 | Maquis | Self-guided missile | 20 | ? | ? | stats still to be written | — | VOY "Dreadnought": a Cardassian missile that B'Elanna Torres reprogrammed for the Maquis |

**Leaders:** Maquis raider, plus three leader-only ships (not recruitable): the captured Constellation, the stolen Defiant and a Ferengi Marauder (D'Kora-class, 366 m; model: Raul Mamoru on TrekMeshes).

**Leader-only:** Captured Constellation-class: Stolen cruiser, 22, 56, 5, phaser 7-3, torpedo 11-2, —, The class is on screen in TNG ("The Battle", "Peak Performance"). A captured one is our own idea, added by request.

**Leader-only:** Stolen Defiant-class: Glass-cannon escort, 25, 44, 6, pulse phaser 9-3, quantum torpedo 14-1, Evasive, DS9 "Defiant": Thomas Riker steals the Defiant from DS9 for the Maquis and uses its Romulan cloak to slip into Cardassian space. Same stats and sprite as the Federation's Defiant for now.

**Leader-only:** Ferengi Marauder: Mercenary flagship, 30 (draft: between the Defiant and the Jem'Hadar battleship, the other leader-only ships), other stats still to be written.

**Gaps:** the Bajoran raider from "The Siege" is sub-impulse, so it stays out. The Ferengi shuttle, Antares-class freighter, Orion interceptor, Talarian observation craft were dropped by request (the D'Kora Marauder later came back as a leader-only ship), when this faction was narrowed from Non-Aligned Worlds to the Maquis. I found no Nausicaan ship model, and the only Gorn ship model is a Star Trek Online design, so both stay out.

---

## 6. Open questions

1. **Model licences:** `sprites/roster/CREDITS.md` lists every source. Before upload to the official Wesnoth add-on server, which only accepts freely licensed art, every sprite whose model has no stated licence or a non-commercial licence (CC BY-NC) needs replacing, and the Bajoran assault vessel needs repainting.
2. **Maquis:** keep Baran's raider (a mercenary ship from TNG "Gambit", never flown by the Maquis on screen), or drop it for a 5-ship roster?
3. **Day/night:** keep a star cycle for lawful and chaotic factions, or drop alignment?
