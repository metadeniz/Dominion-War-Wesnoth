# Sprite lighting preferences (D, 13 Nov 2026)

From the 15 Maquis raider light rigs (sprites/roster/raider-lighting-rigs.png, rigs in sprites/roster/src/rigs-raider.json).
Positions are scene coordinates: x = screen right, y = up, z = toward the camera. "fill" = soft sky light (hemisphere).

| Rig | D's verdict | Setup | Sprite brightness / contrast |
|---|---|---|---|
| 10 | Favourite | Key from the right (3.4) + weak light from front left (0.6), fill 0.1 | lum 79, contrast 25 |
| 08 | Favourite | Key from the right (3.4) + rim light from back left (1.2), no fill | lum 73, contrast 28 |
| 01 | Good | Key from the right (3.2), fill 0.5 | lum 74, contrast 26 |
| 14 | OK | Key from the right (3.0) + overhead (1.0) + rim back left (1.0), no fill | lum 91, contrast 25 |
| 15 | Neat, for some ships | Warm key from the right (3.6), cool fill 0.3 | lum 70, contrast 31 |
| 04 | For some dark ships | Low, grazing key from the right (4.0), fill 0.15 | lum 48, contrast 30 |

Not picked: 03 and 11 (black shadows, harsh), 05, 12 and 13 (bright and flat), 07 (front light, flat), 02, 06, 09.

## What the picks have in common
- One strong key light from the right does the shaping.
- The side away from the key stays dark but never black: a little fill (0.1 to 0.5) or one weak second light keeps the detail readable at 72px. This is the "darker middle" look.
- When there is a second light, it is weak and comes from the side opposite the key (front left or back left), so it outlines the far edge against dark space.
- Medium brightness (lum about 70 to 80) and moderate contrast (about 25 to 28). Too much fill or a front light flattens the ship. No fill and a strong rim crush the shadows.

## Shadows
- The ground shadow is drawn in its own pass and must look normal; no light may be added just to make a shadow.
- A shadow from straight above looked much better than the default angle on winged ships (K'Vort, Raptor). Decided 13 Nov: D says a shadow "looks necessary", so every sprite keeps a ground shadow, cast from straight above (also over the team ring, sprites/roster/team-ring-shadows.png). Rig 14 is the default lighting since sheet v37; exceptions: Maquis raider rig 10, Jem'Hadar battleship rig 8.

## Update after the 8-ship sample (13 Nov, sprites/roster/lighting-rigs-sample.png)
- D thinks rig 14 is the best lighting in general: key from the right + overhead + rim from back left, no sky fill. It keeps dark hulls readable (K'Vort lum 53, K't'inga 76) where 1, 10 and 8 crush them.
- Rig 1 "looks too bright": its sky fill (0.5) lifts and blue-tints the shadows, so the ship reads washed out even though its average brightness is lower than 14's.
- D finds 14 more "realistic": all of its light is directional and white, with no sky light, which is how light behaves in space and how studio miniatures are shot.
- The Maquis fighter (Peregrine) looks good under every rig: a light hull, high-contrast paint, faceted shape and self-lit lights.

## Default switched to 14soft (13 Nov, sheet v39)
D: "14soft looks better in almost every case". 14soft = rig 14 with the overhead light at 0.5 and the key at 3.4:
key 3.4 from the right (pos 7, 2.5, -0.5, casts self-shadows) + overhead 0.5 (0, 8, 0.3) + rim 1.0 from back left (-6, 2, -4), no sky fill, shadow from straight above.
Exceptions: Maquis raider rig 10, Jem'Hadar battleship rig 8. D liked the runabout better under the old default (its blue nacelle strip is paint on its left side, which 14soft leaves in shadow); exception offered, not decided.

## Properties of the ideal default (measured on the 72px sprites, tools/lightmetrics.py)
Brightness = mean luminance of the hull pixels (0-255). p10/p90 = the darkest/brightest tenth of the hull. Crushed = hull pixels below 25.
- Light from the right (upper right on screen). This is also Wesnoth's rule: "Light comes from the artist's upper right" (wiki.wesnoth.org/Creating_Unit_Art). The first default (upper left) broke it.
- The main light is low, about 20 degrees above the table, so it rakes across the hull and panel edges catch it.
- A weak overhead light, about 1/7 of the main light, keeps the tops of dark ships readable. 1/3 (rig 14) flattens; none (rigs 8, 1) lets dark ships sink.
- A rim light from back left at about 1/3 of the main light outlines the far edge.
- No sky fill: picks had 0 to 0.1. Rig 1's 0.5 read as washed out.
- Ground shadow from straight above.
- Targets: average brightness 75-85; p10 at least ~40; p90 ~105-115 (lit side about 2.5x the shadow side); under 5% crushed; no blown highlights.
  Rejected rigs miss one of these: 03, 06 and 04 crush 19-31% of the hull; 05, 12 and 13 have p10 56-68 with the lit side only ~2x brighter (flat).
  Measured: raider favourites 10 (79, p10 47, 0.5% crushed) and 8 (73, 36, 5.3%); 14soft on the whole roster 82, p10 48, 2.6% crushed; rig 14 91, p10 57.
- Not met yet: even brightness across ships. Under 14soft they range from 47 (K'Vort, Vor'cha) to 127 (Bajoran freighter). Scaling each ship's light partway toward ~80 would fix it while keeping Klingons the darkest.
- Ships whose identifying paint or markings face away from the light (runabout) need an exception or self-lit markings.
- Wesnoth's own shadow rule: colour RGB 22,0,52 at 60% opacity (wiki.wesnoth.org/Creating_Shadows_Under_Units). Ours is black at 35%.

## 13 Nov evening: D's verdicts on the three setups, and the overnight study
- D: setup 2 (14soft + front-left light 0.6) "is best in most cases, but not all cases. some ships are too bright."
- D: some ships "dont look better or look worse" under setup 2: B'rel, K't'inga, Raptor, Noggra's freighter, K'Vort, Negh'Var. All are Klingon, with plain dark green paint, and the fill cut their contrast by 24% against 14% for the rest.
- D asked for the optimal lighting, including how to manage overall brightness, possibly per shape or ship. Study: `design/lighting-study.md`; candidates: `sprites/roster/roster-lighting-optimal-candidates.png`.
- Result (awaiting D's pick, A or C):
  - Setup 2's layout for every ship, with fill and exposure solved per ship.
  - Fill: target light-to-shadow ratio of 2.4:1 (3.6:1 for Klingons), with a contrast floor so plain-painted ships don't go flat.
  - Brightness rule: toward 88, keeping half of the gap below and a quarter above, kept between 55 and 100.
  - Bugs fixed: the main light missed most of the Nebula and Keldon (normal bias); ten ships cast no shadows onto themselves; the D5 and Bajoran freighter model files carried their own light.
- D's per-ship picks stay as they are (runabout option 5, Jem'Hadar battleship rig 8, raider rig 10), with only the shadow fix and the brightness rule added.

## 15 Nov: candidate C is the default (sheet v41)
- D: "4 looks best, so it should be default." Column 4 = candidate C (no overhead light, half rim, fill and exposure per ship). Applied in `src/roster2.json` and sheet v41.
- D: keep option 1 (sheet v40, rig 14soft): it "seems to look better on some ships": Noggra's freighter, B'rel, K't'inga, Negh'Var, Hideki, Galor, Keldon, Breen, Jem'Hadar battle cruiser, Defiant.
- D: option 3 (candidate A, with overhead light) "looks good on K'Vort", keep it for the future.
- Every ship's option 1 and option 3 lights are stored under `light_alt` in `src/roster2.json`, so any ship can be switched to them.
- Decided 15 Nov (sheet v42): the ten ships above use option 1 and the K'Vort uses option 3; every other ship uses C. D, 16 Nov: "both defiants should look the same", so the Stolen Defiant also uses option 1 (sheet v43).

## Standing rule (D, 15 Nov): when redoing a sprite, sample options 1 and 3
- D: "you dont need to keep the old sprites around, just recall option 1 and option 3. So in the future if I say I want to re-do a sprite, you should remember to have option 1 and option 3 ready as possiblities you can show me in a sample."
- So: whenever D asks to redo a ship's sprite, render a sample of that ship under C (the default), option 1 and option 3, side by side. Don't keep option sprites as files; keep the light setups instead.
- The setups are stored per ship under `light_alt` in `sprites/roster/src/roster2.json`. For a new ship, build them like this:
  - **Option 1 (rig 14soft, sheet v40):** hemi 0; key 3.4 at (7, 2.5, -0.5), casting shadows; overhead 0.5 at (0, 8, 0.3); rim 1.0 at (-6, 2, -4); shadowPos (0, 10, 0.001). It uses the old shadow settings (no `nb`, no `recvAll`), so it reproduces v40 exactly.
  - **Option 3 (candidate A):** key at (7, 2.5, -0.5) with `nb` 0; overhead 0.5 and rim 1.0; fill at (-4, 2, 5) solved per ship; exposure from the brightness rule; `recvAll`.
  - **C (default):** the same as option 3, but with no overhead light and rim 0.5.
  - For options 3 and C, the fill and exposure come from `src/strategies3.py` (candidates A and C), turned into roster lights by `src/buildopt.py`. These need the ship's light passes from `src/passes.js` (`src/passes-all.json`).
- Old option sprites (v40 copies, A sprites, v41 C sprites) were deleted on D's word; they can be re-rendered exactly from the setups.

## Retired sprites are not kept (D, 15 Nov)
- D had the whole `sprites/roster/old/` folder deleted. Don't keep copies of replaced sprites from now on; keep the light setups and model settings in `src/roster2.json`, so earlier versions can be re-rendered.

## Working images (D, 16 Nov)
- Comparison and contact sheets in the project files are not part of the mod, so keep them and do not ask D about deleting them.
