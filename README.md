# Dominion_War_Wesnoth

Working folder for The Dominion War, a Star Trek mod for Wesnoth. It mirrors the project library
path for path, so any file a project thread adds or updates in the library
lands at the same relative path here.

    design/    design docs (rosters, unit stats, lighting, space tileset) and the balance scripts
    sounds/    weapon, cloak, transporter and explosion sounds, with SOURCES/CREDITS
    sprites/   ship sprites: roster/ (sheets, finals, render sources), ships/, ships-3d/
    tileset/   space tileset studies and mockups, with src/ generators

The add-on itself (first playable build, multiplayer):

    _main.cfg  entry point; loads utils/, terrain/, ui/, units/, era/
    era/       The Dominion War era, one file per faction, and events.cfg (Glory, Plunder,
               kamikaze and warhead self-destruct, Ketracel dependency, Veteran leaders)
    units/     the 32 ship types per faction (generated, see below), hull movetypes and races
    utils/     shared macros: shields (resistances), abilities, weapon specials, crew levels
               and traits, placeholder attack animations
    images/    unit sprites, placeholder weapon effects (projectiles/dw/), crew badges (misc/)
    terrain/   the space tileset (any map is turned into space when a game starts)
    tools/     make_units.py writes units/*.cfg from the stats tables; make_fx.py draws the
               placeholder effects; test_addon/ is an automated rules test

To play: start a multiplayer game, pick the era **The Dominion War** and any 2p map.

Ship stats come from design/unit-stats.md (proposal 2). To change a ship, edit the tables in
`tools/make_units.py` and run `python3 tools/make_units.py`; don't edit units/*.cfg by hand.
Attack sounds use the GPL set in sounds/free-sci-fi/ so the build can be published. Weapon
visuals are simple placeholders (beam bolts and glowing torpedoes) until the final effects
are picked.

Not in this build yet: the optional "Flagships" leader setting, Jem'Hadar and Federation
cloak detection, cloak/decloak sounds, and a Sovereign-class unit (the sprite is here, but it
has no stats in design/unit-stats.md).

Rules test: copy tools/test_addon/DW_Test into the add-ons folder next to this add-on and run
`wesnoth --nogui -u dw_test`. It checks every ship's images and sounds, the kamikaze, warhead,
transporter, targeting lock, Command, Glory, crew levels, cloaks and traits.

## Syncing new work from the project

This folder is a git repo pushed to
https://github.com/metadeniz/Dominion-War-Wesnoth. Project threads work on a
branch and open a pull request; after merging, run `git pull` here.

Older route, for library files that aren't in the repo yet:

1. A cloud thread packs design/, sounds/, sprites/ and tileset/ (no model .zips,
   no __pycache__) into standalone zips of 9 MB or less at
   exports/stw/stw-NN.zip in the project library. Pieces must stay well under
   16 MB, because the laptop link refuses anything bigger.
2. A thread on this laptop downloads each piece and unpacks it here,
   overwriting files with the same path. Files deleted in the library are not
   deleted here.

First sync: 2026-11-16, 655 files.

