# Dominion_War_Wesnoth

Working folder for The Dominion War, a Star Trek mod for Wesnoth. It mirrors the project library
path for path, so any file a project thread adds or updates in the library
lands at the same relative path here.

    design/    design docs (rosters, unit stats, lighting, space tileset) and the balance scripts
    sounds/    weapon, cloak, transporter and explosion sounds, with SOURCES/CREDITS
    sprites/   ship sprites: roster/ (sheets, finals, render sources), ships/, ships-3d/
    tileset/   space tileset studies and mockups, with src/ generators

The add-on itself (skeleton, not playable yet):

    _main.cfg  entry point; loads utils/, terrain/ (when it exists), units/, era/
    era/       The Dominion War era and one file per faction (leaders, recruits)
    units/     stub ship types per faction, hull movetypes and races
    utils/     shared macros (shield profiles as resistances)
    images/    unit sprites the game loads (copies of sprites/roster/*.png)
    terrain/   reserved for the space tileset: add terrain/_main.cfg and
               _main.cfg picks it up automatically

Not copied: the large 3D model archives (*.zip at the top of the library)
and Python __pycache__ folders.

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

The ship types are stubs: stats come from design/unit-stats.md, but attacks,
abilities, crew levels, animations and sounds are not written yet.
