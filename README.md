# Star_Trek_Wesnoth

Working folder for the Star Trek Wesnoth mod. It mirrors the project library
path for path, so any file a project thread adds or updates in the library
lands at the same relative path here.

    design/    design docs (rosters, unit stats, lighting, space tileset) and the balance scripts
    sounds/    weapon, cloak, transporter and explosion sounds, with SOURCES/CREDITS
    sprites/   ship sprites: roster/ (sheets, finals, render sources), ships/, ships-3d/
    tileset/   space tileset studies and mockups, with src/ generators

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

There is no _main.cfg yet, so Wesnoth skips this folder until the add-on
itself (units, terrain, eras) is written here.
