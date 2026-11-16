# 3D model sources

Sprites in this folder were rendered from these third-party models. Check each license before you publish the add-on.

| Sprite | Source model | License |
|---|---|---|
| federation-galaxy, federation-defiant, klingon-bird-of-prey (B'rel), dominion-attack-ship (fighter), dominion-battle-cruiser | github.com/bwoneill/tts_star_trek_into_the_unknown (`assets/factions/*/ships/*_mesh.obj` + `_skin.png`) | No license stated in the repository |
| federation-excelsior | Thingiverse #1427032 "Star Trek - USS Excelsior NCC-2000" (mirrored at archive.org/details/thingiverse-1427032) | CC BY 4.0 (attribution required) |

Files are named `<ship>-<facing>.png` for the six Wesnoth hex facings (se, ne, n, nw, sw, s), 72x72 with transparent backgrounds.
Render setup: three.js, orthographic camera at 45° elevation (the chosen angle; other angles are in the tilt-*/ and top-down-90/ folders), headings adjusted so each facing points at the neighbouring hex centre on screen.
