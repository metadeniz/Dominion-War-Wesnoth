# Sprite scale notes

Sprite size follows each ship's canon length on a compressed scale: visible size grows with length to the power 0.3, anchored on the Galaxy-class (642 m), which already fills its hex. No ship may grow past the edge of its 72px hex (the Wesnoth wiki says only exceptionally large units should spill over), so the biggest ships all end up close to the same size.

Lengths come mostly from Ex Astris Scientia (ex-astris-scientia.org, size table and ship pages). That site gathers figures from the Star Trek Encyclopedia, the DS9 Technical Manual and the Fact Files, plus its own estimates. They aren't strictly canon.

| Ship | Length used | Notes |
|---|---|---|
| Danube runabout | 23 m | |
| Peregrine (Maquis fighter) | 25 m | rough estimate |
| Maquis raider | 60 m | estimate (about 50 m on screen) |
| Bajoran assault vessel | 93 m | |
| Jem'Hadar attack ship | 95 m | Encyclopedia says 68 m; the site estimates about 95 m |
| Hideki | 98 m | estimate |
| B'rel bird-of-prey | 110 m | design size |
| Defiant | 120–170 m | 150 m used |
| K't'inga | 214 m | |
| Miranda | 243 m | |
| Bajoran freighter | 250 m | Eaglemoss figure |
| Klingon freighter (Noggra's ship) | ~300 m | no published figure; a guess |
| Constellation | 310 m | |
| Breen warship | 330 m | uncertain, "at least 300 m" |
| Intrepid | 344 m | |
| K'Vort bird-of-prey | ~350 m | no canon figure |
| Galor | 371–481 m | 420 m used |
| Nebula | ~440 m | |
| Akira | ~464 m | |
| Excelsior | 467 m | |
| Vor'cha | 481 m | |
| Galaxy | 642 m | |
| Jem'Hadar battle cruiser | ~650 m | |
| Negh'Var | 682 m | |
| Jem'Hadar battleship | ~1,500 m | estimates range from 1.3 to 4.5 km |
| Mercenary raider (Baran's) | ~170 m | Ex Astris estimate; the same design as the Miradorn Theta-class. Its sprite is about 17% bigger than this scale gives (not resized) |

Resized: Excelsior, Nebula, Defiant, Klingon freighter, B'rel, Vor'cha, Negh'Var, Jem'Hadar attack ship, Galor, Jem'Hadar battleship. Then, after D's decision, the bigger unlisted ships also grew: Akira, Intrepid, K't'inga, K'Vort, Breen warship, Hideki and the Jem'Hadar battle cruiser. The small craft (Danube, Peregrine, Maquis raider, Bajoran assault vessel) keep their size so they stay readable. The Galaxy, Miranda, Constellation and Bajoran freighter already matched the scale.

**Jem'Hadar battleship:** D agreed it can spill slightly past its hex. Its image is 96x96 instead of 72x72 (`canvas: 96` in `src/roster2.json`), and Wesnoth centres it on the hex, so it overlaps its neighbours by about 12px on each side. That makes it about 30% longer on screen than the Galaxy.

The settings live in `src/roster2.json` (`size`, with `size_before_scale` kept for each resized ship).
