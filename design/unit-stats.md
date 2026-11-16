# Star Trek Wesnoth: Unit Stats (proposal 2)

A proposal for D to review. It gives Wesnoth-style stats to every ship in `faction-rosters.md` (draft 2), fills in the four ships that had no stats yet (Raptor, D5, Dreadnought, Ferengi Marauder), and adds what the roster left open: XP, alignment, resistances, terrain, traits and how each ability works. No game files were changed.

**Proposal 2** follows D's rule that only torpedoes are ranged: every beam, ram and boarding party is now melee. That changed the balance a lot, so most attack numbers were redone. Section 2 also explains how cloaked ships are found.

Where this proposal changes a number from the roster draft, the change is listed under each faction, with the reason.

## Key choices at a glance

1. **Only torpedoes are ranged** (D's rule). Photon, quantum and micro-torpedoes are ranged. Phasers, disruptors, polaron beams, plasma weapons, rams and boarding parties are melee. That splits the factions in a Wesnoth way: every Federation ship carries torpedoes, Klingon ships carry light torpedoes (usually one strike), and the Cardassian Hideki and Galor, the Breen warship, the freighters, the mercenary raider and the Dreadnought have no ranged attack at all. A ship with no ranged attack can't shoot back at torpedoes, so those ships get more HP and harder-hitting beams for their price.
2. **Each faction has a shield profile** (resistances), so the damage types matter. The Federation is weak to polaron (as in canon, early in the war), Klingons shrug off rams, Cardassians resist phaser-type beams, Jem'Hadar resist polaron, the Breen resist phasers but hate plasma, and Maquis ships have thin shields everywhere except against plasma.
3. **Three hull classes** set terrain defence and movement: light ships (escorts, raiders, fighters) hide well in nebulae and asteroids, cruisers are the middle, and capital ships are easy to hit and slow through asteroids.
4. **Big ships cost 2 upkeep.** Every ship is level 1, so without this a Galaxy would cost the same upkeep as a Miranda. Wesnoth lets a unit set its own upkeep, so the capital ships (Nebula, Galaxy, Vor'cha, Jem'Hadar battle cruiser) pay 2.
5. **Command has to be reworked.** Wesnoth leadership only helps allies of a *lower* level, and nearly every ship is level 1, so a Galaxy's Command would only help runabouts. Proposal: Command helps adjacent allies of the same or lower crew level.
6. **Cloaked ships are found only on contact.** No ship has a detection ability for now. A cloaked ship is revealed when an enemy moves next to it, and the enemy has to stop, as with Wesnoth's ambush. Jem'Hadar (partial) and Federation (tachyon detection grid) decloaking abilities may come later.
7. **The Dreadnought is a guided missile.** Its warhead always hits for 32 and destroys the Dreadnought. Until then it fights with a plasma cannon.
8. **Multiplayer leaders start as Veterans** and come from a pool of mid-sized ships (20 to 30 gold), so a Maquis raider leader never faces a Jem'Hadar battleship. The flagships become an optional "Flagships" game setting.

---

## 1. How the numbers work

### Damage notation

`7-3` means 7 damage, 3 strikes, as in Wesnoth.

**Ranged and melee:** ranged attacks are torpedoes: photon, quantum and micro-torpedoes, and the Jem'Hadar torpedo. Everything else is melee: phasers, disruptors, polaron beams, plasma weapons, the Breen energy dampener, rams, boarding parties and the Dreadnought's warhead. A ship attacked at range can only answer with its own torpedoes, so a beam-only ship takes torpedo fire without being able to fire back.

Each attack has one damage type. Damage types map to Wesnoth types so the engine's resistance code works unchanged:

| Type | Wesnoth type | Used by |
|---|---|---|
| Phaser | blade | Federation, Bajoran and Maquis phasers, Cardassian spiral-wave disruptors |
| Disruptor | pierce | Klingon, Breen and mercenary disruptors, the Ferengi EM pulse |
| Torpedo | impact | Photon, quantum and Jem'Hadar torpedoes, the Dreadnought warhead |
| Plasma | fire | Maquis plasma charges, the Dreadnought's plasma cannon |
| Polaron | arcane | Jem'Hadar polaron beams |
| Kinetic | cold | Ramming, boarding, the Jem'Hadar kamikaze and the Breen energy dampener |

All three **Jem'Hadar ships** carry a plain torpedo (ranged, Torpedo damage), drawn white in its animation. Polarons are beams only. The Breen **energy dampener** does Kinetic damage, which is Wesnoth's cold and suits the cold-world Breen.

### Shield profiles (resistances)

Positive numbers mean less damage taken, negative numbers mean more, as in Wesnoth.

| Shields | Phaser | Disruptor | Torpedo | Plasma | Polaron | Kinetic | Ships |
|---|---|---|---|---|---|---|---|
| Federation | +10% | +10% | 0% | +10% | −20% | 0% | Federation ships, captured Constellation, stolen Defiant |
| Klingon | 0% | +10% | +10% | 0% | −10% | +20% | Klingon ships except Raptor and D5 |
| Klingon (old) | −10% | 0% | 0% | 0% | −10% | +20% | Raptor, D5 |
| Cardassian | +20% | 0% | −10% | 0% | +10% | 0% | Hideki, Galor, Keldon |
| Jem'Hadar | 0% | 0% | −10% | 0% | +30% | +10% | Jem'Hadar ships |
| Breen | +30% | 0% | 0% | −20% | +10% | +10% | Breen warship |
| Maquis | −10% | −10% | −10% | +20% | −10% | 0% | Maquis fighter, Maquis raider |
| Bajoran | 0% | 0% | 0% | +10% | −10% | 0% | Bajoran freighter, Bajoran assault vessel |
| Mercenary | −10% | +10% | 0% | 0% | −10% | 0% | Mercenary raider |
| Dreadnought | +20% | 0% | −10% | +20% | 0% | +10% | Dreadnought |
| Ferengi | 0% | +10% | 0% | +10% | −10% | +10% | Ferengi Marauder |

Reasons in one line each:

- **Federation:** balanced shields, but polaron beams cut straight through them (canon, early in the Dominion War). This is the Federation's one big weakness.
- **Klingon:** heavy armour. Built to ram and be rammed, and good against disruptors and torpedoes. **Klingon (old)** is for the two 22nd-century ships: same armour against rams, but weaker shields against phasers, disruptors and torpedoes.
- **Cardassian:** strong against beam weapons like their own, weak against torpedoes.
- **Jem'Hadar:** almost immune to polaron fire, a little weak to torpedoes (the Defiant's quantum torpedoes did well against them on screen).
- **Breen:** very strong against phasers, which made them deadly to the Federation in season 7. They are a cold-world species, so they take extra damage from plasma, which is the Maquis' weapon.
- **Maquis:** thin shields on small ships, offset by speed and high defence. They know plasma well (the Badlands are full of plasma storms) and resist it.
- **Bajoran, Mercenary, Dreadnought, Ferengi:** one-off profiles for the Maquis' mixed fleet.

### Hull classes (terrain)

Defence is the chance to dodge a hit, as in Wesnoth. Moves is the movement cost.

| Terrain | Light: moves / defence | Cruiser: moves / defence | Capital: moves / defence |
|---|---|---|---|
| Open space | 1 / 40% | 1 / 40% | 1 / 30% |
| Nebula | 2 / 60% | 2 / 50% | 2 / 40% |
| Asteroid field | 2 / 60% | 3 / 50% | 4 / 30% |
| Planet orbit | 1 / 60% | 1 / 60% | 1 / 50% |
| Starbase or station | 1 / 60% | 1 / 60% | 1 / 60% |
| Badlands, ion storm or gas giant (Wesnoth swamp) | 2 / 30% | 3 / 20% | 3 / 20% |
| Dark matter nebula (Wesnoth mushroom grove) | 2 / 50% | 2 / 40% | 2 / 30% |

**Badlands pilots** (Maquis fighter and raider only): +10% defence in nebulae and the Badlands, and the Badlands cost 1 less to enter.

**Dark matter nebulae** give some cover but no hiding: no cloak works there, the Maquis raider's nebula cloak included. **Dark matter adept** (every Maquis ship and the Breen warship, D's call): +10% defence in dark matter nebulae, and they cost 1 move instead of 2. The size of the bonus is a first guess, as are the base numbers in the row above.

### Levels and XP

The crew-level rules stay as the roster has them (Veteran: +20% HP, +1 damage on every attack, +5% defence; Elite: +40% HP, +2 damage, +10% defence and one extra strike on the main weapon). This proposal adds the XP:

- **Auxiliary (level 0) to Green:** 20 XP.
- **Green to Veteran:** between 28 and 56 XP, rising with the ship's size and cost (listed per ship below). A cheap ship levels quickly, a flagship slowly.
- **Veteran to Elite:** twice the Green-to-Veteran figure.
- **Elite to Legendary (AMLA):** 150 XP, as in Wesnoth.

Since almost every ship is level 1, every kill gives 8 XP and every fight 1 XP, whatever the target's size. That is fair to small ships: a B'rel that finishes off a Galaxy earns as much as one that finishes off a Miranda. If D wants big kills to be worth more, the WML can give bonus XP by the target's cost.

### Crew traits

Each ship gets two random crew traits, like Wesnoth's traits:

| Trait | Effect | Wesnoth equivalent |
|---|---|---|
| Quick | +1 MP, −5% HP | quick |
| Resilient | +4 HP, +1 HP per crew level | resilient |
| Sharpshooters | +1 damage on ranged attacks | dextrous |
| Hard chargers | +1 damage on melee attacks, +1 HP | strong |
| Seasoned officers | 20% less XP needed | intelligent |

Faction rules: Jem'Hadar ships always get **Bred for war** (fearless: no penalty at the wrong time of day) plus one random trait. The Dreadnought gets no traits.

### Time of day

Keep the Wesnoth day/night cycle, renamed as a star cycle (open question 3 in the roster). Lawful ships deal +25% at "day" and −25% at "night", chaotic ships the reverse. That gives the factions a rhythm:

- **Federation:** lawful.
- **Klingon:** chaotic.
- **Dominion:** mixed. Cardassians are lawful, Jem'Hadar chaotic, the Breen neutral, so some of the fleet is always at its best.
- **Maquis:** neutral. Never at their best, never at their worst.

---

## 2. Abilities and weapon specials

| Name | Kind | Effect | WML basis |
|---|---|---|---|
| **Cloak** | ability | Invisible on every terrain unless next to an enemy. Attacking reveals the ship until its next turn, as with ambush. | `[hides]` with no terrain filter |
| **Nebula cloak** | ability | As Cloak, but only in nebulae and the Badlands (not dark matter nebulae) | ambush |
| **Dark matter adept** | ability (Maquis ships, Breen warship) | +10% defence and 1 move in dark matter nebulae | movetype override |
| **Repairs +4** | ability | Adjacent allies recover 4 HP each turn | heals +4 |
| **Command** | ability | Adjacent allies of the **same or lower** crew level deal +25% damage (+25% more per level below the commander) | `[leadership]` with a custom level filter |
| **Evasive** | ability | Ignores enemy zones of control | skirmisher |
| **Glory** | ability (all Klingon ships) | Regains 8 HP after destroying an enemy | `die` event |
| **Plunder** | ability | +3 gold when this ship destroys an enemy | `die` event |
| **Ketracel supply** | ability | Adjacent Jem'Hadar ships recover 8 HP each turn | heals +8, filtered to Jem'Hadar |
| **Ketracel-dependent** | ability (all Jem'Hadar ships) | No rest repair. Jem'Hadar ships repair only from Ketracel supply, planets and stations. | `[effect] apply_to=` rest healing off |
| **Machine** | ability (Dreadnought) | No crew: gains no XP, has no traits, can't be helped by Command | custom |
| *charge* | weapon special (Defiant pulse phasers) | When attacking, both sides deal double damage, as with Wesnoth's charge. Not used on defence. | charge |
| *fleet tactics* | weapon special | ×1.5 damage when an ally is on the far side of the target | backstab, softened |
| *targeting lock* | weapon special | At least 60% chance to hit when attacking | marksman |
| *energy dampener* | weapon special | The target is slowed: half damage and half movement until the end of its next turn | slows |
| *shield breaker* | weapon special (Ferengi EM pulse) | If it hits at least once, all the target's resistances drop by 20 points until the end of the turn (Breen phaser +30% becomes +10%, Federation polaron −20% becomes −40%). It doesn't stack. Allies who attack the same ship afterwards gain the most from it. | `attacker_hits` event giving the target an `[object]` with a resistance effect and `duration=turn` |
| *transporter* | weapon special (Jem'Hadar boarding parties) | The boarding party beams through shields: the target's resistances count as 0% against it, good or bad. It can't be used on the Dreadnought, which has no crew. | `[resistance]` weapon special with `apply_to=opponent` (Wesnoth 1.16 or later) |
| *kamikaze* | weapon special (Jem'Hadar attack ship) | Always hits, one strike, for damage equal to the attack ship's current HP. The target can't retaliate, and the attack ship is destroyed. Nobody gains XP, Glory or Plunder from it. | custom: chance_to_hit 100, damage set in an `attack` event, `[disable]` on the opponent, attacker killed in `attack end` |
| *detonate* | weapon special | Always hits, one strike, and the Dreadnought is destroyed after the attack. No retaliation. | custom: chance_to_hit 100 plus an `attack end` event |

### Cloaking and detection

Cloaked ships are found the Wesnoth way, on contact only:

1. **Adjacent ships see them.** As with Wesnoth's ambush, any enemy ship next to a cloaked ship can see it. If an enemy ship moves into a hex next to a hidden cloaked ship, the cloaked ship is revealed and the moving ship stops at once and loses its remaining movement.
2. **Firing decloaks.** A cloaked ship can attack straight out of cloak, but it is then visible through the enemy's next turn, so the enemy can hit back. It cloaks again at the start of its own next turn. In canon, ships can't fire while cloaked, and Wesnoth's ambush already works this way.
3. **Hidden ships can't be targeted.** Until one of the above reveals it, a cloaked ship can't be attacked.

Ships that cloak: B'rel, K'Vort and both Defiants everywhere, and the Maquis raider only in nebulae and the Badlands. No ship can cloak in a dark matter nebula.

**Later:** the Jem'Hadar may get a decloaking ability that only works part of the time, and the Federation a tachyon detection grid. Neither is in this proposal. Until then the only counter to a cloak is to bump into it, which makes Birds-of-Prey and the Defiants strong. Watch that in playtesting.

### Maquis disguise and ambush (proposal 3, waiting for D's approval)

This section is a proposal only. The tables in section 3 don't include it yet.

**Which ships:** the **Maquis raider** and the **Maquis fighter (Peregrine)**, the two small Maquis-built ships. Left out:

- **Dreadnought:** a disguised missile with a warhead that always hits would give the enemy no counterplay. If D wants it anyway, the fair version is that it can't detonate on the turn it drops its disguise.
- **Bajoran freighter and assault vessel:** Bajoran militia ships, not Maquis-built. The freighter is also the ship the disguise imitates (see below).
- **Mercenary raider:** Baran's crew are hired guns, not Maquis.
- **Leaders:** a 366 m Marauder or a Constellation can't pass as a freighter, and the stolen Defiant already cloaks.

**Signature mask** (ability). The ship changes its warp signature to look like another ship. It's switched on from the ship's right-click menu at the start of its own turn, if no enemy is next to it, and it costs nothing.

- **What the enemy sees: a Bajoran freighter.** The ship's name, sprite and listed attack become the freighter's. It can't pose as an enemy or neutral ship, because Wesnoth draws every unit in its side's colour for all players, with no way to show one player a different picture. So it poses as the one Maquis ship the enemy has reason to leave alone. That also turns the real freighters into part of the bluff: every freighter might be a raider.
- **While masked, it really flies like a freighter:** 4 MP, only the freighter's phaser 4-2 (weapons powered down to civilian levels), no Evasive and no zone of control (the freighter is level 0, and level 0 ships have no zone of control in Wesnoth). That keeps the sidebar consistent with the disguise. The one tell is HP: the sidebar shows the ship's real maximum (raider 30, fighter 26, against a freighter's 40), which Wesnoth can't fake. A careful player can catch it.
- **Dropping the mask:** free, from the right-click menu, at any point in its own turn, before or after moving. Movement already spent stays spent.
- **What gives it away:** it attacks, or it is attacked. Either way the mask drops before the fight, so it always fights with its real weapons.
- **With Nebula cloak:** the raider can be masked and in a nebula at the same time. Inside the nebula it is hidden, outside it looks like a freighter. That gives it a disguise where the cloak doesn't work: open space and dark matter nebulae.
- **WML:** the mask is a `[variation]` of each ship with the freighter's name, image, attack and movement, switched by a right-click `[set_menu_item]`, and switched back in an `attack` event.

**Surprise attack** (weapon special on all the raider's and fighter's attacks): +50% damage when it attacks straight out of a nebula cloak, or on the turn it drops its mask. In WML this is a `[damage]` special filtered on a unit variable that is set when the cloak or mask drops and cleared after the attack.

**Balance:** the model can't price the bluff itself. Counting Surprise attack at +25% on average (it applies to about half the attacks), the Maquis go from 0.80–0.85 to 0.90–0.92 against the other factions, about where they were before the 16 Nov price rises. The raider at its new 15 gold scores 1.01, so that price fits a raider that can do this. The fighter scores 1.18 at 11 gold, which is strong, so 12 gold would suit it. The Bajoran freighter (0.52 at 14 gold) stays the weak spot. The bluff helps it a little, because the enemy can no longer safely ignore freighters, but it still needs a lower price or better stats.

**Changed from the roster:** *fleet tactics* is ×1.5 instead of the ×2 of Wesnoth's backstab, because it sits on durable line cruisers (Galor, Keldon) rather than a fragile thief. At ×2, three flanking Galors would delete a Galaxy in one turn.

---

## 3. Ship stats

Hull and Shields refer to the tables in section 1. Ships marked (leader) are leader-only and never recruited, so their upkeep is "loyal" and their cost only matters in campaigns.

### Federation (lawful)

**Identity:** the torpedo fleet. Every Federation ship carries torpedoes, so it can always shoot back at range, and it can hit the Galor, Hideki and Breen warship without taking any return fire. In return its beams are the weakest, so it loses close fights against Klingons and Jem'Hadar, and polaron beams cut through its shields. It has two field repair ships. Pricey, with the most capital ships.

| Ship | Lvl | Cost | HP | MP | XP | Align | Hull | Shields | Ranged | Melee | Abilities |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Danube-class runabout | 0 | 10 | 26 | 7 | 20 | lawful | light | Federation | micro-torpedo 6-1 | phaser 4-3 | — |
| Miranda-class | 1 | 14 | 38 | 5 | 32 | lawful | cruiser | Federation | torpedo 6-2 | phaser 4-3 | — |
| Excelsior-class | 1 | 20 | 52 | 5 | 40 | lawful | cruiser | Federation | torpedo 8-2 | phaser 5-3 | — |
| Intrepid-class | 1 | 23 | 44 | 7 | 40 | lawful | cruiser | Federation | quantum torpedo 10-2 | phaser 5-3 | Repairs +4 |
| Akira-class | 1 | 24 | 52 | 5 | 44 | lawful | cruiser | Federation | torpedo 8-3, *targeting lock* | phaser 5-3 | — |
| Nebula-class | 1 | 26 | 62 | 5 | 48 | lawful | capital (upkeep 2) | Federation | torpedo 10-2 | phaser 7-3 | — |
| Galaxy-class | 1 | 34 | 68 | 5 | 56 | lawful | capital (upkeep 2) | Federation | torpedo 11-2 | phaser array 7-4 | Command, Repairs +4 |
| Defiant-class (leader) | 1 | 25 | 44 | 6 | 44 | lawful | light | Federation | quantum torpedo 12-1 | pulse phaser 9-2, *charge*<br>phaser 6-3 | Evasive, Cloak |

**Changes from the roster:** with beams now melee, Federation phasers are about 2 damage lower than in the roster (Excelsior 7-3 to 5-3) and torpedoes about a quarter lower (Excelsior 11-2 to 8-2). A ship with both good beams and good torpedoes beats a beam-only ship at both ranges, so one of the two has to be modest, and for the Federation that's the beams. The **Akira** keeps the strongest Federation torpedo attack (three strikes with targeting lock). The **Danube** gets 26 HP and phaser 4-3 (was 24 and 4-2): at 4-2 it couldn't hurt anything. The **Miranda** gets 38 HP (was 36), the **Excelsior** 52 (was 50), the **Nebula** 62 (was 58) and the **Galaxy** 68 (was 72). The **Defiant** gets Cloak, since the real Defiant carries a Romulan cloaking device. It also gets two beam weapons (D, 16 Nov): **pulse phasers** 9-2 with *charge*, for its all-out attack runs (18-2 when attacking, but return fire is doubled too), and a normal **phaser** 6-3, which it defends with. The stolen Defiant gets the same. The **Intrepid** carries **quantum torpedoes** 10-2 (was photon 8-2, D, 16 Nov), and its price goes from 22 to 23 gold to pay for them, which the cost formula allows (22.0).

### Klingon Empire (chaotic)

**Identity:** brawlers. Strong disruptors, rams and boarding parties up close, heavy armour and Glory instead of repair ships. Their torpedoes are light (most ships fire just one), so at range they lose to the Federation, and they want to close in. Two cloaked Birds-of-Prey for ambushes. Cheap on average, so they field more ships.

| Ship | Lvl | Cost | HP | MP | XP | Align | Hull | Shields | Ranged | Melee | Abilities |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Klingon freighter | 0 | 10 | 32 | 5 | 20 | chaotic | cruiser | Klingon | none | disruptor 5-3<br>boarding party 6-2 (kinetic) | Glory |
| Raptor-class scout | 1 | 13 | 32 | 8 | 32 | chaotic | light | Klingon (old) | torpedo 6-1 | disruptor 5-3 | Glory |
| B'rel-class Bird-of-Prey | 1 | 15 | 30 | 7 | 32 | chaotic | light | Klingon | torpedo 7-1 | disruptor 5-3<br>ram 12-1 (kinetic) | Cloak, Glory |
| D5-class battle cruiser | 1 | 16 | 40 | 6 | 36 | chaotic | cruiser | Klingon (old) | torpedo 8-1 | disruptor 7-3<br>boarding party 7-2 (kinetic) | Glory |
| K't'inga-class | 1 | 18 | 42 | 5 | 40 | chaotic | cruiser | Klingon | torpedo 8-2 | disruptor 6-3<br>ram 7-2 (kinetic) | Glory |
| K'Vort-class Bird-of-Prey | 1 | 21 | 44 | 6 | 44 | chaotic | cruiser | Klingon | torpedo 10-1 | disruptor 7-3<br>boarding party 6-3 (kinetic) | Cloak, Glory |
| Vor'cha-class | 1 | 25 | 58 | 5 | 48 | chaotic | capital (upkeep 2) | Klingon | torpedo 10-2 | disruptor 8-3<br>boarding party 7-3 (kinetic) | Glory |
| Negh'Var-class (leader) | 1 | 34 | 72 | 4 | 56 | chaotic | capital | Klingon | torpedo 13-2 | disruptor 9-4<br>boarding party 8-3 (kinetic) | Command, Glory |

**New ships:**

- **Raptor-class scout** (13 gold): the fastest Klingon ship (8 MP), for scouting and grabbing planets early. It has no cloak (22nd-century) and older, weaker shields.
- **D5-class battle cruiser** (16 gold): a cheaper, faster (6 MP), more fragile K't'inga that boards instead of ramming. It has older shields too.

**Changes from the roster:** every ship has Glory. All torpedoes are about 15% lower, as for every faction. The **freighter** gets 32 HP and disruptor 5-3 (was 30 and 4-2): it carries no torpedoes, so it now has no ranged attack. The **K't'inga** gets 42 HP and ram 7-2 (was 46, 8-2): it was the most gold-efficient line ship in the game. The **Negh'Var** gets 72 HP and disruptor 9-4 (was 80, 10-4), to bring it closer to the Galaxy at the same price.

**Who rams and who boards (D, 16 Nov).** Every Klingon ship fights up close with its disruptors. Some also get a second melee attack, chosen by what each ship would risk:

| Ship | Second melee | Why |
|---|---|---|
| Freighter | boarding party 6-2 | A troop transport: boarding is its job. |
| Raptor | none | A fast scout with old, weak shields. Ramming would throw away the ship, and it has no room for a boarding party. Its job is scouting, not brawling. |
| B'rel | **ram 12-1** (new) | Small, cheap and tough for its size, so it's the ship a captain risks on a ram. One big hit, which suits a hit-and-run raider. |
| D5 | boarding party 7-2 | An old cruiser with a large crew. It leaves ramming to the K't'inga and sends warriors across instead. This is the smaller ship with boarding that D asked for, alongside the freighter. |
| K't'inga | ram 7-2 | An old, heavily armoured hull, built to take a collision. The only cruiser that rams. |
| K'Vort | **boarding party 6-3** (new) | The B'rel's design scaled up, with room for a boarding party, and too valuable to ram with. |
| Vor'cha | **boarding party 7-3** (was ram 10-2) | A modern attack cruiser with a large crew. Too valuable to ram with. |
| Negh'Var | **boarding party 8-3** (was ram 12-2) | The flagship: the largest crew, and it never rams (D). |

Rams are few, hard strikes, and boarding parties are more, lighter strikes. Both do Kinetic damage, and Klingon boarding parties don't beam through shields the way the Jem'Hadar ones do. The balance check doesn't move: the disruptors stay each ship's main weapon, and the second attack mostly matters against targets with high disruptor resistance.

### Dominion Alliance

**Identity:** three fleets in one, and mostly a beam fleet. Only the Keldon and the Jem'Hadar ships carry torpedoes. The Hideki, Galor and Breen warship have to close in, so they are tougher and hit harder for their price than ships with torpedoes. Cardassians are cheap, disciplined lines with fleet tactics. Jem'Hadar are the hardest hitters: polaron beams, boarding parties that beam through shields, and attack ships that will ram an enemy as a kamikaze. They get no rest repair. One Breen disabler slows the enemy's best ship. No field repairs for the Cardassians and Breen.

| Ship | Lvl | Cost | HP | MP | XP | Align | Hull | Shields | Ranged | Melee | Abilities |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Hideki-class | 0 | 10 | 30 | 7 | 20 | lawful | light | Cardassian | none | spiral disruptor 5-3 (phaser) | — |
| Galor-class | 1 | 15 | 44 | 5 | 36 | lawful | cruiser | Cardassian | none | spiral disruptor 7-3 (phaser), *fleet tactics* | — |
| Jem'Hadar attack ship | 1 | 17 | 42 | 6 | 40 | chaotic | light | Jem'Hadar | torpedo 7-1 | polaron beam 8-3<br>boarding party 6-3 (kinetic), *transporter*<br>kamikaze current HP ×1 (kinetic), *kamikaze* | Ketracel-dependent |
| Keldon-class | 1 | 21 | 50 | 5 | 44 | lawful | cruiser | Cardassian | torpedo 8-2 | spiral disruptor 7-3 (phaser), *fleet tactics* | — |
| Breen warship | 1 | 22 | 58 | 6 | 44 | neutral | cruiser | Breen | none | disruptor 9-3<br>energy dampener 8-2 (kinetic), *energy dampener* | Dark matter adept |
| Jem'Hadar battle cruiser | 1 | 28 | 60 | 5 | 52 | chaotic | capital (upkeep 2) | Jem'Hadar | torpedo 10-2 | polaron beam 7-4<br>boarding party 7-3 (kinetic), *transporter* | Command, Ketracel supply, Ketracel-dependent |
| Jem'Hadar battleship (leader) | 1 | 40 | 88 | 4 | 64 | chaotic | capital | Jem'Hadar | torpedo 14-2 | polaron beam 10-4<br>boarding party 8-3 (kinetic), *transporter* | Command, Ketracel supply, Ketracel-dependent |

**Changes from the roster:** the beam-only ships got stronger to make up for having no ranged attack. The **Hideki** gets 30 HP and 5-3 (was 26 and 4-3). The **Galor** gets 44 HP and 7-3 (was 42 and 6-3). The **Jem'Hadar attack ship** gets 42 HP, polaron beam 8-3 (was 38 and 6-3) and a white torpedo 7-1, the same size as the B'rel's. The **Breen warship** gets 58 HP, disruptor 9-3 and dampener 8-2 (was 50, 7-3, 6-2). The ships with torpedoes came down instead: the **Keldon** gets 50 HP, spiral disruptor 7-3 and torpedo 8-2 (was 54, 8-3, 10-2), and the **Jem'Hadar battle cruiser** gets 60 HP, polaron beam 7-4 and torpedo 10-2 (was 64, 8-4, 13-2). The **Jem'Hadar battleship** gets 88 HP and torpedo 14-2 (was 92, 16-2). All Jem'Hadar ships lose rest repair (Ketracel-dependent), which is what makes the Vorta battle cruiser matter.

**Kamikaze and boarding (D's idea, on trial):** the roster's ramming speed is gone. In its place:

- **Boarding party** on all three Jem'Hadar ships (6-3 on the attack ship, 7-3 on the battle cruiser, 8-3 on the battleship). Because it beams through shields, it ignores resistances. That makes it the right pick against targets that shrug off polaron beams or rams, such as Klingons (+20% kinetic), the Breen and other Jem'Hadar. Against the Federation (−20% polaron), the polaron beam is still better.
- **Kamikaze** on the attack ship only. It hits for the ship's current HP: 42 at full strength, about 50 for a Veteran crew, less once the ship is damaged. Target resistances still apply (a Klingon ship takes 34 from a fresh attack ship). One fresh attack ship takes most of a Galaxy's 68 HP, and two destroy it. It costs 17 gold and gives the enemy no XP, so it's best used on leaders, healers and wounded capital ships. The big ships don't get it, because throwing away a 28-gold Vorta command ship is never worth it.

The balance check can't score a one-shot attack, so the attack ship's score below doesn't include the kamikaze. Watch for it in playtesting: a fresh attack ship is a cheap way to take out a leader.

### Maquis (neutral)

**Identity:** a swarm of cheap, fast, evasive ships with thin shields. The small ships carry a single torpedo, and the fighter and raider have a plasma charge as a second melee attack, which is what to use against the Breen. The freighter, the mercenary raider and the Dreadnought have no ranged attack. They win by picking fights in nebulae, the Badlands and dark matter nebulae (Badlands pilots, Nebula cloak, Dark matter adept) and by Plunder. One healer, no Command except on the Marauder leader.

| Ship | Lvl | Cost | HP | MP | XP | Align | Hull | Shields | Ranged | Melee | Abilities |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Bajoran freighter | 0 | 14 | 40 | 4 | 20 | neutral | cruiser | Bajoran | none | phaser 4-2 | Repairs +4, Dark matter adept |
| Maquis fighter (Peregrine) | 1 | 11 | 26 | 8 | 28 | neutral | light | Maquis | micro-torpedo 7-1 | phaser 5-3<br>plasma charge 6-2 | Evasive, Badlands pilots, Dark matter adept |
| Maquis raider | 1 | 15 | 30 | 7 | 32 | neutral | light | Maquis | torpedo 8-1 | phaser 5-3<br>plasma charge 7-2 | Evasive, Nebula cloak, Badlands pilots, Dark matter adept |
| Mercenary raider (Baran's) | 1 | 16 | 38 | 7 | 36 | neutral | light | Mercenary | none | disruptor 7-3, *fleet tactics* | Plunder, Dark matter adept |
| Bajoran assault vessel | 1 | 17 | 40 | 7 | 36 | neutral | light | Bajoran | torpedo 8-2 | phaser 6-3 | Evasive, Dark matter adept |
| Dreadnought (ATR-4107) | 1 | 20 | 48 | 5 | none | neutral | cruiser | Dreadnought | none | plasma cannon 7-3<br>warhead 32-1 (torpedo), *detonate* | Machine, Dark matter adept |
| Captured Constellation (leader) | 1 | 22 | 56 | 5 | 44 | neutral | cruiser | Federation | torpedo 8-2 | phaser 5-3 | Repairs +4, Dark matter adept |
| Stolen Defiant (leader) | 1 | 25 | 44 | 6 | 44 | neutral | light | Federation | quantum torpedo 12-1 | pulse phaser 9-2, *charge*<br>phaser 6-3 | Evasive, Cloak, Dark matter adept |
| Ferengi Marauder (leader) | 1 | 30 | 66 | 5 | 52 | neutral | capital | Ferengi | torpedo 10-2 | EM pulse 7-3 (disruptor), *shield breaker* | Plunder, Command, Dark matter adept |

**New ships:**

- **Dreadnought (ATR-4107)** (20 gold): a reprogrammed Cardassian missile. It fights with a plasma cannon until the moment it detonates: the warhead always hits for 32 torpedo damage, gets no retaliation, and destroys the Dreadnought. 32 finishes a damaged ship, kills most scouts outright and takes most of a cruiser, but leaves a Galaxy standing. It is Cardassian-built, so its shields shrug off phasers and plasma, and it gains no XP.
- **Ferengi Marauder** (leader, 30 gold): a mercenary flagship with a photon torpedo, an electromagnetic pulse weapon that weakens the target's shields (*shield breaker*) for the rest of the turn, Plunder and Command. It is the only Maquis ship with Command. Its job is to open a target up for the Maquis swarm, so the EM pulse itself is modest (7-3).

**Changes from the roster:** the **Bajoran freighter** gets phaser 4-2 (was 3-2) and costs 14 (was 11), and the **Maquis raider** costs 15 (was 13), both moved to the cost formula in `cost-formula.md` (D, 16 Nov). The **Maquis fighter** gets 26 HP and phaser 5-3 (was 24 and 4-3). The **fighter and raider** get plasma-charge melee and Badlands pilots. The **mercenary raider** gets 38 HP and disruptor 7-3 (was 36 and 6-3), because it has no torpedoes. The **Bajoran assault vessel's** torpedo is 8-2 (was 10-2). The **captured Constellation** gets Repairs +4, so the three Maquis leaders play differently (healer, cloaked striker, commander). The **stolen Defiant** gets Cloak, as on screen.

---

## 4. Balance check

I scored every recruitable ship against every enemy recruit with a simple duel model: each ship picks the range that suits it best, damage is adjusted for resistances, open-space defence and weapon specials, and the score is strength per gold. Abilities like Cloak, Repairs and Command are priced in as a few gold each. It ignores terrain, time of day, zones of control and healing over time, so it's a sanity check and not a substitute for playtesting. The ship data and the model are in `design/unit-stats-balance/` (`python3 duel.py units.py` reruns it after any change).

Faction against faction (1.00 = even, above 1 favours the row):

| Row vs column | Federation | Klingon | Dominion | Maquis |
|---|---|---|---|---|
| Federation | 1.00 | 1.02 | 0.97 | 1.25 |
| Klingon | 0.98 | 1.00 | 1.06 | 1.17 |
| Dominion | 1.03 | 0.94 | 1.00 | 1.22 |
| Maquis | 0.80 | 0.85 | 0.82 | 1.00 |

The Federation, Klingons and Dominion are within about 6% of each other. **The Maquis now score 0.80 to 0.85 against everyone.** That comes from the 16 Nov price rises (Bajoran freighter 11 to 14, Maquis raider 13 to 15), not from the Marauder change. Before them the Maquis were at 0.93 to 0.99, which the model's missing terrain (Maquis light ships get 60 to 70% defence in nebulae and asteroids) roughly explains. At the new prices, the Bajoran freighter (0.52) and Maquis raider (0.78) are the weakest recruits in the game. Either the prices go back, or those two ships need more for their gold. If playtesting shows the Federation struggling against the Dominion's polaron beams, the first lever is Federation polaron resistance (−20% to −10%).

The only-torpedoes-are-ranged rule had the biggest effect: in a first pass with the old numbers, the Federation came out about 30 to 45% stronger than everyone, because every Federation ship had torpedoes and full-strength beams. Lower Federation beams, about 15% lower torpedoes for everyone and tougher beam-only ships brought it back to even.

Ships that score low on purpose, because their value is in what they do rather than in duels:

- **Danube, Hideki, Raptor, Maquis fighter:** scouts and cheap pickets.
- **Breen warship:** the model undervalues the energy dampener's slow.

The Jem'Hadar attack ship scores even without its kamikaze, so the kamikaze is pure extra. If it proves too strong in play, cut the attack ship's HP, which also lowers the kamikaze damage.

---

## 5. Leaders

**Proposal:** in multiplayer, the leader starts with a Veteran crew (level 2), as in Wesnoth, where leaders are level 2. Leaders come from a pool of ships worth 20 to 30 gold, so leaders across factions are about the same size:

| Faction | Leader pool |
|---|---|
| Federation | Excelsior, Nebula, Defiant |
| Klingon | K'Vort, Vor'cha |
| Dominion | Keldon (a Gul), Breen warship (a Thot), Jem'Hadar battle cruiser (a Vorta) |
| Maquis | Captured Constellation, stolen Defiant, Ferengi Marauder |

The roster's other leaders stay available in campaigns and as an optional **Flagships** game setting: Galaxy, Negh'Var and Jem'Hadar battleship (34 to 40 gold), and on the small side the Galor and Maquis raider. That moves the Galor out of the Dominion's default pool and puts the Keldon in.

---

## 6. Sounds

Which sound each attack uses, from `sounds/trek/` (for private play) with the free stand-in from `sounds/free-sci-fi/` for a public release:

| Attack | Trek sound | Free stand-in |
|---|---|---|
| Federation phaser | `phasers/tng_phaser*.ogg`; long beams (`tng_phaser4_top`, 6, 8, 9) for the Galaxy's array | `phasers/phaser-sweep-1/2.ogg` |
| Defiant pulse phaser | `phasers/tng_phaser_rifle.ogg` | `phasers/phaser-short-burst.ogg` |
| Photon / quantum torpedo | `torpedoes/tng_torpedo*.ogg` / `quantumtorpedoes*.ogg` | `torpedoes/torpedo-launch-1/2.ogg` |
| Klingon disruptor / torpedo | `disruptors/klingon_disruptor*.ogg` / `torpedoes/klingon_torpedo.ogg` | `phasers/phaser-maser-1/2.ogg` / `torpedoes/torpedo-charged-1.ogg` |
| Cardassian spiral disruptor | `disruptors/cardassian_disruptor.ogg` | `phasers/phaser-energy-beam.ogg` |
| Jem'Hadar polaron beam | `phasers/borg_phaser.ogg` (closest match, no polaron sound exists) | `phasers/phaser-retro-beam.ogg` |
| Breen disruptor and dampener | `disruptors/tng_weapons2.ogg` | `torpedoes/torpedo-antimatter.ogg` |
| Maquis plasma, Dreadnought, Ferengi EM pulse | `disruptors/tng_disruptor.ogg` | `torpedoes/torpedo-heavy-plasma-1/2.ogg`, `impacts/impact-plasma.ogg` |
| Ram, boarding, warhead | `explosions/largeexplosion*.ogg` | `impacts/impact-low-boom.ogg`, `impacts/explosion-ship.ogg` |
| Klingon cloak / decloak | `cloaking/cloak_klingon.ogg` / `decloak_birdofprey.ogg` | none yet |
| Defiant cloak (Romulan device) | `cloaking/cloak_romulan.ogg` / `decloak_romulan.ogg` | none yet |

---

## 7. Open questions for D

1. **Dreadnought:** a one-shot missile (as proposed), or a reusable heavy ship with a plain warhead attack?
2. **Leaders:** start multiplayer leaders as Veterans from the 20 to 30 gold pool, with flagships as an option?
3. **Upkeep 2 for capital ships:** keep it, or keep all ships at upkeep 1 and raise capital-ship prices instead?
4. **Defiant cloak:** both Defiants now cloak. Keep that, or leave the Federation one without it, as the roster had?
5. **Jem'Hadar kamikaze:** damage equal to the ship's current HP (as proposed), or a fixed amount? Should the big Jem'Hadar ships get it too?
6. **Maquis disguise and ambush:** approve the proposal above (raider and fighter only, posing as a Bajoran freighter)? Also, should the fighter go to 12 gold, and should the freighter come back down from 14?
