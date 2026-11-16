# Optimal sprite lighting: overnight study (13-14 Nov 2026)

Pictures:
- `sprites/roster/roster-lighting-optimal-candidates.png`: the whole roster in four columns. 1 is the sprites now (sheet v40), 2 is setup 2 as you saw it, 3 is candidate A and 4 is candidate C.
- `sprites/roster/lighting-changes-step-by-step.png`: six ships, adding one change at a time.

Nothing in the roster or the sheet has changed yet. Both candidates are ready to apply once you pick one.

## The short answer

The best lighting is setup 2's layout, with three bugs fixed and two numbers worked out for each ship.

**One layout for every ship, so all units on the map share the same light:**
- **Main light:** from the right and low, about 20 degrees above the table, casting shadows on the ship itself.
- **Fill:** from front left, the side opposite the main light.
- **Rim:** from back left.
- **Overhead:** little or none.
- **No sky light.**
- **Ground shadow:** straight below.

**Two numbers per ship, worked out by measuring its 72px sprite:**
1. **Fill strength.** The fill grows until the ship reaches a target light-to-shadow ratio, or until the sprite's overall contrast falls to a floor, whichever comes first.
2. **Exposure.** All lights are scaled together, so the ship's brightness lands where the brightness rule puts it. Self-lit windows and engines are not scaled.

**Candidates A and C differ in one thing only:**
- **A** keeps the 0.5 overhead light and the 1.0 rim, like setup 2.
- **C** drops the overhead light, halves the rim, and makes up for it with more fill. On paper C is better, with a little more contrast and detail at the same brightness. On screen the difference is small. This one is your call.

## The rule in numbers

- **Light-to-shadow ratio:** about 2.4 : 1 for most ships, measured on the light alone with the paint divided out. This is what setup 2 gave the ships you liked. Klingon ships get about 3.6 : 1, which is what setup 1 gave them and what you preferred for them.
- **Contrast floor:** the brightest tenth of the sprite must stay at least 3.5 times brighter than the darkest tenth, measured on the light and paint together. This keeps plain-painted ships from going flat.
- **Fill cap:** the fill never exceeds 0.4 times the main light, so the light always reads as coming from the right.
- **Brightness rule:**
  - **Target:** 88, close to mainline Wesnoth's median unit brightness of 90.
  - **Darker ships** keep half of their gap below 88.
  - **Brighter ships** keep a quarter of their gap above 88.
  - **Limits:** the result is kept between 55 and 100.

  Ships keep their character, so Klingons stay the darkest, but the extremes come in. Brightness now ranges from 69 to 101, against 47 to 127 now. The spread between ships drops from 20 to 8.
- **Your own picks stay as they are,** with only the shadow fix and the brightness rule added:
  - Danube runabout: option 5
  - Jem'Hadar battleship: rig 8
  - Maquis raider: rig 10

| | Sprites now | Setup 2 | A | C |
|---|---|---|---|---|
| Average brightness (range) | 81 (47-127) | 91 (52-137) | 86 (69-101) | 86 (69-102) |
| Contrast, average (lowest ship) | 26.9 (14.3) | 22.9 (11.8) | 25.3 (17.9) | 26.1 (17.5) |
| Shadow side (darkest tenth) | 47 | 62 | 55 | 55 |
| Hull below 25 (crushed) | 2.6% | 0.2% | 0.8% | 0.6% |

In short, A and C lift the shadows most of the way to setup 2, keep almost all the contrast of the sprites now, and even out the brightness.

## Bugs found and fixed

These bugs mattered more than any light setting.

1. **The main light missed most of the Nebula and the Keldon.**
   - A shadow setting (normal bias 0.03) pushed the shadow test inside the hull wherever a model's surfaces face inward.
   - The Nebula's saucer received 5% of the main light it should, and the Keldon 30%. The Akira was also partly affected.
   - They were lit almost only by the overhead and fill lights. That is why both needed big brightness boosts (`br=1.63` and `br=1.9`) and still looked flat.
   - **Fix:** normal bias 0. I checked the change on every other ship and saw no shadow stripes ("acne").
2. **Ten ships cast no shadows onto themselves:** Miranda, Galaxy, both Defiants, K'Vort, Vor'cha, Negh'Var, Jem'Hadar attack ship and battle cruiser, and Baran's raider.
   - Their loading path never switched shadow receiving on.
   - **Fix:** switched on for all ships.
3. **The D5 and the Bajoran freighter carried their own light.**
   - Each model file holds the artist's own directional light, which lit the ship in every render regardless of our setup. With every light of ours switched off, the freighter still had brightness 112 and the D5 90.
   - That is why the freighter was the brightest ship, and why the D5 needed `br=0.1` ("wing plates render pale").
   - **Fix:** lights and cameras inside model files are now removed, and the D5 goes back to `br=1.0`.
   - The freighter now shows its own rust-brown paint, lit like every other ship. Have a look at whether you like it.

## What the tests showed

Every light was rendered separately for every ship, so any mix can be put together exactly, in linear light. Checked against real renders, the mixes are off by about 1 level in 255.

Each alternative below was matched to the same brightness and the same shadow side as the reference, then measured for how much contrast and detail it keeps:

- **Fill position:** front left is the best of those tried. A fill from straight left or from high front left loses about 0.5 contrast, and sky light needs about 3 times the strength and tints the shadows blue.
- **Main light position:** low from the right is best. A higher main light, or one from front right, flattens the ships; one from back right is about equal.
- **Overhead light:** less is better. Going from 1.0 to 0.5 to 0.25 to 0 adds contrast and detail at each step, provided the fill makes up the shadow side. This matches your verdict that 14soft beats 14, and your raider favourites 10 and 8, which have no overhead light. It is the case for C.
- **Rim light:** it hardly matters at 72px. Less rim plus a little more fill gives slightly more contrast.

**The same positions win for every shape group I tried:** flat-topped (saucers, Defiant), angled (wings, freighters) and in between. What differs between ships is how much fill they need, not where it comes from.

## Shapes and paint: why the fill must differ per ship

**Shape decides how much shadow a ship has to start with.**
- Flat-topped ships (Galaxy, Nebula, Defiant) face up into the light and have little shadow even with no fill, only about 2 : 1. Under candidate A they get no fill at all.
- Winged and angled ships have deep shadows (up to 8 : 1 for the runabout) and need fill to open them.

**Paint decides how much shadow a ship can afford to lose.**
- Ships with busy paint, panels and windows still read when the shadows are filled.
- Ships with plain paint read only through light and shadow. That covers the Klingon greens, the untextured Jem'Hadar battleship and the Breen.
- Setup 2's flat 0.6 fill cut the contrast of the six Klingon ships you flagged by 24%, against 14% for the rest. The contrast floor in the rule stops that.

So the rule needs no per-ship tuning: it reads both things off each ship's own sprite. Klingons also get the deeper-shadow style on purpose. Cinema lights villains low-key, and that's what you preferred for them.

## Checked against your earlier verdicts

Without being tuned to them, the rule lands close to your earlier per-ship verdicts:
- **Flat ships** (Defiant, Negh'Var, Constellation): you preferred 14soft, with no fill. The rule gives them 0, 0.19 and 0.34.
- **Klingons:** you preferred setup 1, with no fill. The rule gives them 0 to 0.36, average 0.11.
- **Jem'Hadar battleship:** you picked rig 8, which has no fill. The rule gives it less fill than standard ships. I kept rig 8 anyway.
- **Maquis raider:** you picked rig 10, with fill 0.6. The rule gives 0.54.
- **"Some ships are too bright":** the brightest now come down to 100 or less (Keldon 137 to 100, Galor 129 to 97, freighter 134 to 74).

## How strong each light really is

Settings and what the hull actually receives differ, because a low light grazes the surfaces while an overhead light hits the tops square on. Here is the share of all light reaching the hull, as a roster average:

| | Main (right) | Overhead | Rim (back left) | Fill (front left) |
|---|---|---|---|---|
| Setup 2, by setting | 3.4 | 0.5 | 1.0 | 0.6 |
| Setup 2, received | 44% | 25% | 15% | 16% |
| A, received | 48% | 27% | 16% | 9% |
| C, received | 61% | 0% | 10% | 29% |

## Reference: mainline Wesnoth 1.18

I measured 247 mainline base unit sprites:
- **Brightness:** median 90, with the middle half between 77 and 100.
- **Light direction:** 89% are brighter at the top and 66% brighter on the right.
- **Shadows:** a shadow straight below the unit, RGB 22,0,52 at 60% opacity.
- **Outlines:** they carry dark outlines (about 20% of their pixels are below 25), which our renders don't need on dark space.
- **Terrain:** mountains are about 20% brighter on their right faces, and buildings cast shadows to the lower left. So terrain is lit from the upper right too.

## What I need from you

1. **Pick A or C.** If you can't tell them apart, A is the safer step.
2. **Say if any ship looks wrong** in the candidates sheet. The freighter is the one most changed, because it lost its built-in light.

Then I'll apply the pick as sheet v41, move the current sprites to `old/`, and update the credits.

## Files

- **Tools** (`sprites/roster/src/`):
  - `passes.js` renders one light at a time.
  - `comp.py` and `lightlab.py` mix and measure.
  - `strategies3.py` solves fill and exposure per ship.
  - `buildopt.py` writes the roster files.
  - `shapestats.py` measures which way the hull faces.
  - `exp_abcd.py` runs the position tests.
  - `wesunitstats.py` and `terrainlight.py` measure mainline Wesnoth.
- **Renderer** (`page3.html`):
  - shadow fix (per-light `nb`/`bias`)
  - `recvAll`
  - built-in lights stripped from model files
  - `ambient` and `normals` passes for measuring
- **Candidate rosters:** `roster-optA.json` and `roster-optC.json`.
