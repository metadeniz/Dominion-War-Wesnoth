# Weapon sound effects: credits and licences

Every file here is under a licence that the Wesnoth add-on server accepts: any version of the GNU GPL, or any Creative Commons licence ([Wesnoth:Copyrights](https://wiki.wesnoth.org/Wesnoth:Copyrights)). Sounds that are not GPL have to be listed in the add-on's `ART_LICENSE` file (or in a `<file>.ogg.license` file next to each sound). A ready-to-paste block is at the bottom of this file.

None of these are recordings from Star Trek. The show's own sound effects are Paramount's copyright and can't go on the add-on server. These are original sci-fi sounds that fill the same roles.

## What was done to the files

Every file was converted to Ogg Vorbis (44.1 kHz, quality 5), had leading silence trimmed, and was loudness-normalised to about −16 LUFS so the set plays at a similar volume. Files marked **trimmed** were also cut short with a 0.5 s fade-out so they fit a Wesnoth attack animation. `phaser-energy-beam.ogg` is two JC Sounds clips (build-up start and power-down finish) crossfaded together. The CC BY licences require these changes to be noted, so keep this section when you credit them.

## Phasers (sustained beams)

| File | Length | Source sound | Author | Licence |
|---|---|---|---|---|
| `phasers/phaser-maser-1.ogg` | 2.4 s | `weaponfire11.wav`, used as the "Maser" weapon in AstroMenace | Michael Kurinnoy (Viewizard) | GPL-3.0 |
| `phasers/phaser-maser-2.ogg` | 2.4 s | `weaponfire12.wav`, AstroMenace "Maser 2" | Michael Kurinnoy (Viewizard) | GPL-3.0 |
| `phasers/phaser-laser-beam.ogg` | 1.9 s | `weaponfire14.wav`, AstroMenace "Laser" | Michael Kurinnoy (Viewizard) | GPL-3.0 |
| `phasers/phaser-energy-beam.ogg` | 2.5 s | "Energy BuildUp to LOOP Short Start" + "LOOP to Energy Power Down Short Finish", crossfaded | JC Sounds | CC BY 4.0 |
| `phasers/phaser-sweep-1.ogg` | 2.0 s | `Laser_05.wav` | Little Robot Sound Factory | CC BY 3.0 |
| `phasers/phaser-sweep-2.ogg` | 1.9 s | `Laser_08.wav` | Little Robot Sound Factory | CC BY 3.0 |
| `phasers/phaser-retro-beam.ogg` | 2.2 s, **trimmed** | `laserbeam.wav` (continuous BeepBox beam, sounds more chiptune) | frosty ham | CC0 |
| `phasers/phaser-short-burst.ogg` | 0.7 s | `laserLarge_000.ogg` (short shot, could suit fighters or the Defiant's pulse phasers) | Kenney | CC0 |

## Photon torpedoes (launch)

| File | Length | Source sound | Author | Licence |
|---|---|---|---|---|
| `torpedoes/torpedo-launch-1.ogg` | 3.0 s, **trimmed** | `weaponfire18.wav`, the "Torpedo" weapon in AstroMenace | Michael Kurinnoy (Viewizard) | GPL-3.0 |
| `torpedoes/torpedo-antimatter.ogg` | 3.0 s | `weaponfire13.wav`, AstroMenace "Antimatter" weapon | Michael Kurinnoy (Viewizard) | GPL-3.0 |
| `torpedoes/torpedo-charged-1.ogg` | 1.3 s | "Energy Shot Charged v1_01" (charge-up then release) | JC Sounds | CC BY 4.0 |
| `torpedoes/torpedo-charged-2.ogg` | 1.3 s | "Energy Shot Charged v2_02" | JC Sounds | CC BY 4.0 |
| `torpedoes/torpedo-heavy-plasma-1.ogg` | 2.5 s, **trimmed** | "Heavy Plasma Shot 01" | JC Sounds | CC BY 4.0 |
| `torpedoes/torpedo-heavy-plasma-2.ogg` | 2.5 s, **trimmed** | "Heavy Plasma Shot 04" | JC Sounds | CC BY 4.0 |
| `torpedoes/torpedo-launch-2.ogg` | 2.7 s | `rlaunch.wav` from "4 projectile launches" | qubodup | CC BY 3.0 |

## Impacts and explosions (for the hit or death sound)

| File | Length | Source sound | Author | Licence |
|---|---|---|---|---|
| `impacts/impact-antimatter.ogg` | 1.9 s | `antimaterhit.wav`, AstroMenace antimatter hit | Michael Kurinnoy (Viewizard) | GPL-3.0 |
| `impacts/impact-plasma.ogg` | 1.3 s | `plasmahit.wav`, AstroMenace plasma hit | Michael Kurinnoy (Viewizard) | GPL-3.0 |
| `impacts/explosion-ship.ogg` | 4.0 s | `explosion3.wav`, AstroMenace big energy explosion | Michael Kurinnoy (Viewizard) | GPL-3.0 |
| `impacts/impact-low-boom.ogg` | 2.0 s | `lowFrequency_explosion_000.ogg` | Kenney | CC0 |

## Source pages

- AstroMenace sounds: <https://opengameart.org/content/space-battle-game-sounds-astromenace> (original game: <https://github.com/viewizard/astromenace>). Weapon names come from the game's `src/assets/audio.cpp`. A copy of the GPL-3.0 is in `licenses/GPL-3.0.txt`; ship it with the add-on.
- JC Sounds, Sci-Fi Pack Vol 1: <https://opengameart.org/content/jc-sounds-sci-fi-pack-vol-1>. Notice requested: "CC BY 4.0 - Credit: JC Sounds".
- Little Robot Sound Factory, Sci-Fi Sound Effects Library: <https://opengameart.org/content/sci-fi-sound-effects-library>. Notice requested: "Attribute Little Robot Sound Factory, and provide this link where possible: www.littlerobotsoundfactory.com".
- qubodup, 4 projectile launches: <https://opengameart.org/content/4-projectile-launches>
- frosty ham, Laser Beam: <https://opengameart.org/content/laser-beam>
- Kenney, Sci-Fi Sounds: <https://opengameart.org/content/sci-fi-sounds> (credit "Kenney.nl" is optional).

Licence texts: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/), [CC BY 3.0](https://creativecommons.org/licenses/by/3.0/), [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/), [GPL-3.0](https://www.gnu.org/licenses/gpl-3.0.html).

## Other packs worth a listen (not downloaded here)

All on OpenGameArt and add-on-server safe: Kenney "63 Digital sound effects" (CC0, retro synth "phaserUp/phaserDown" blips, too small and chirpy for starship phasers), TAD "Doomsday Laser Cannon" (CC0, very long), bart "Space Laser" (CC0, 7 s flanged beam), Zander Noriega "Vintage SciFi SFX Vol 1" (CC BY 3.0, 1950s-style FM laser). Freesound.org also has good material, but I couldn't reach it from here.

## Paste into ART_LICENSE

```
Sound effects in sounds/ (see sounds/CREDITS.md for per-file details):

- phaser-energy-beam.ogg, torpedo-charged-1.ogg, torpedo-charged-2.ogg,
  torpedo-heavy-plasma-1.ogg, torpedo-heavy-plasma-2.ogg
  by JC Sounds, CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)
  https://opengameart.org/content/jc-sounds-sci-fi-pack-vol-1
  Changed: converted to Ogg, trimmed, normalised; phaser-energy-beam is two clips crossfaded.

- phaser-sweep-1.ogg, phaser-sweep-2.ogg
  by Little Robot Sound Factory (www.littlerobotsoundfactory.com), CC BY 3.0
  (https://creativecommons.org/licenses/by/3.0/)
  https://opengameart.org/content/sci-fi-sound-effects-library
  Changed: converted to Ogg, normalised.

- torpedo-launch-2.ogg
  by qubodup, CC BY 3.0 (https://creativecommons.org/licenses/by/3.0/)
  https://opengameart.org/content/4-projectile-launches
  Changed: converted to Ogg, normalised.

- phaser-retro-beam.ogg by frosty ham; phaser-short-burst.ogg and impact-low-boom.ogg
  by Kenney (kenney.nl). CC0 1.0, credit given as a courtesy.

- phaser-maser-1.ogg, phaser-maser-2.ogg, phaser-laser-beam.ogg, torpedo-launch-1.ogg,
  torpedo-antimatter.ogg, impact-antimatter.ogg, impact-plasma.ogg, explosion-ship.ogg
  from AstroMenace, (c) 2006-2007 Michael Kurinnoy, Viewizard, GNU GPL v3
  (see licenses/GPL-3.0.txt). https://github.com/viewizard/astromenace
  Changed: converted to Ogg, trimmed, normalised.
```
