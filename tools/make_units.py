#!/usr/bin/env python3
"""Writes the ship unit types (units/<faction>.cfg) from the tables below.

The numbers come from design/unit-stats.md (proposal 2). Change a ship here and rerun:

    python3 tools/make_units.py

Weapons are described by a weapon kind (KINDS): damage type, range, icon, sound and the
placeholder projectile. A ship's attack list gives the kind, the damage, the strikes and,
optionally, a weapon special and a name.
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---------------------------------------------------------------------------------------------
# Weapon kinds.
#   type:   Wesnoth damage type (phaser=blade, disruptor=pierce, torpedo=impact, plasma=fire,
#           polaron=arcane, kinetic=cold)
#   range:  melee or ranged (only torpedoes are ranged)
#   anim:   bolt (a fast beam bolt flies to the target), torpedo (a glowing torpedo flies to the
#           target), ram (the ship lunges at the target), board (transporter sparkle on the target)
#   fx:     the placeholder projectile image in images/projectiles/dw/ (tools/make_fx.py)
#   sound:  firing sound, hit: impact sound on a hit (both from sounds/free-sci-fi, GPL 3)
# ---------------------------------------------------------------------------------------------
SND = "free-sci-fi/"
KINDS = {
    "phaser":          dict(type="blade", range="melee", icon="attacks/lightbeam.png", anim="bolt", fx="beam-phaser", sound=SND + "phasers/phaser-sweep-1.ogg"),
    "phaser_array":    dict(type="blade", range="melee", icon="attacks/lightbeam.png", anim="bolt", fx="beam-phaser", sound=SND + "phasers/phaser-sweep-2.ogg"),
    "pulse_phaser":    dict(type="blade", range="melee", icon="attacks/lightbeam.png", anim="bolt", fx="bolt-phaser", sound=SND + "phasers/phaser-short-burst.ogg"),
    "spiral_disruptor": dict(type="blade", range="melee", icon="attacks/fire-blast.png", anim="bolt", fx="beam-spiral", sound=SND + "phasers/phaser-energy-beam.ogg"),
    "disruptor":       dict(type="pierce", range="melee", icon="attacks/lightning.png", anim="bolt", fx="bolt-disruptor", sound=SND + "phasers/phaser-maser-1.ogg"),
    "merc_disruptor":  dict(type="pierce", range="melee", icon="attacks/lightning.png", anim="bolt", fx="bolt-disruptor", sound=SND + "phasers/phaser-maser-2.ogg"),
    "breen_disruptor": dict(type="pierce", range="melee", icon="attacks/lightning.png", anim="bolt", fx="bolt-breen", sound=SND + "torpedoes/torpedo-antimatter.ogg"),
    "polaron":         dict(type="arcane", range="melee", icon="attacks/dark-missile.png", anim="bolt", fx="beam-polaron", sound=SND + "phasers/phaser-retro-beam.ogg"),
    "plasma":          dict(type="fire", range="melee", icon="attacks/fireball.png", anim="torpedo", fx="torpedo-plasma", sound=SND + "torpedoes/torpedo-heavy-plasma-1.ogg", hit=SND + "impacts/impact-plasma.ogg"),
    "plasma_cannon":   dict(type="fire", range="melee", icon="attacks/fireball.png", anim="torpedo", fx="torpedo-plasma", sound=SND + "torpedoes/torpedo-heavy-plasma-2.ogg", hit=SND + "impacts/impact-plasma.ogg"),
    "plasma_whip":     dict(type="fire", range="melee", icon="attacks/whip.png", anim="bolt", fx="beam-plasma", sound=SND + "torpedoes/torpedo-heavy-plasma-2.ogg", hit=SND + "impacts/impact-plasma.ogg"),
    "dampener":        dict(type="cold", range="melee", icon="attacks/iceball.png", anim="torpedo", fx="torpedo-dampener", sound=SND + "torpedoes/torpedo-antimatter.ogg"),
    "ram":             dict(type="cold", range="melee", icon="attacks/ram.png", anim="ram", sound=None, hit=SND + "impacts/impact-low-boom.ogg"),
    "boarding":        dict(type="cold", range="melee", icon="attacks/fist-human.png", anim="board", fx="transporter", sound=None, hit=SND + "impacts/impact-low-boom.ogg"),
    "kamikaze":        dict(type="cold", range="melee", icon="attacks/ram.png", anim="ram", sound=None, hit=SND + "impacts/explosion-ship.ogg"),
    "warhead":         dict(type="impact", range="melee", icon="attacks/fireball.png", anim="ram", sound=None, hit=SND + "impacts/explosion-ship.ogg"),
    "photon":          dict(type="impact", range="ranged", icon="attacks/fireball.png", anim="torpedo", fx="torpedo-photon", sound=SND + "torpedoes/torpedo-launch-1.ogg", hit=SND + "impacts/impact-antimatter.ogg"),
    "micro":           dict(type="impact", range="ranged", icon="attacks/fireball.png", anim="torpedo", fx="torpedo-micro", sound=SND + "torpedoes/torpedo-launch-1.ogg", hit=SND + "impacts/impact-antimatter.ogg"),
    "quantum":         dict(type="impact", range="ranged", icon="attacks/iceball.png", anim="torpedo", fx="torpedo-quantum", sound=SND + "torpedoes/torpedo-launch-2.ogg", hit=SND + "impacts/impact-antimatter.ogg"),
    "kl_torpedo":      dict(type="impact", range="ranged", icon="attacks/fireball.png", anim="torpedo", fx="torpedo-klingon", sound=SND + "torpedoes/torpedo-charged-1.ogg", hit=SND + "impacts/impact-antimatter.ogg"),
    "ca_torpedo":      dict(type="impact", range="ranged", icon="attacks/fireball.png", anim="torpedo", fx="torpedo-cardassian", sound=SND + "torpedoes/torpedo-charged-2.ogg", hit=SND + "impacts/impact-antimatter.ogg"),
    "jh_torpedo":      dict(type="impact", range="ranged", icon="attacks/magic-missile.png", anim="torpedo", fx="torpedo-jemhadar", sound=SND + "torpedoes/torpedo-charged-2.ogg", hit=SND + "impacts/impact-antimatter.ogg"),
}

# Default attack names and descriptions per kind (a ship can override the name).
NAMES = {
    "phaser": "phaser", "phaser_array": "phaser array", "pulse_phaser": "pulse phaser",
    "spiral_disruptor": "spiral disruptor", "disruptor": "disruptor", "merc_disruptor": "disruptor",
    "breen_disruptor": "disruptor", "polaron": "polaron beam", "plasma": "plasma charge",
    "plasma_cannon": "plasma cannon", "plasma_whip": "plasma whip", "dampener": "energy dampener",
    "ram": "ram", "boarding": "boarding party", "kamikaze": "kamikaze", "warhead": "warhead",
    "photon": "photon torpedo", "micro": "micro-torpedo", "quantum": "quantum torpedo",
    "kl_torpedo": "photon torpedo", "ca_torpedo": "photon torpedo", "jh_torpedo": "torpedo",
}

SPECIALS = {
    "fleet tactics": "{DW_SPECIAL_FLEET_TACTICS}",
    "targeting lock": "{DW_SPECIAL_TARGETING_LOCK}",
    "energy dampener": "{DW_SPECIAL_ENERGY_DAMPENER}",
    "transporter": "{DW_SPECIAL_TRANSPORTER}",
    "kamikaze": "{DW_SPECIAL_KAMIKAZE}",
    "detonate": "{DW_SPECIAL_DETONATE}",
}

ABILITIES = {
    "Cloak": "{DW_ABILITY_CLOAK}",
    "Nebula cloak": "{DW_ABILITY_NEBULA_CLOAK}",
    "Repairs +4": "{DW_ABILITY_REPAIRS}",
    "Command": "{DW_ABILITY_COMMAND}",
    "Evasive": "{DW_ABILITY_EVASIVE}",
    "Glory": "{DW_ABILITY_GLORY}",
    "Plunder": "{DW_ABILITY_PLUNDER}",
    "Ketracel supply": "{DW_ABILITY_KETRACEL_SUPPLY}",
    "Ketracel-dependent": "{DW_ABILITY_KETRACEL_DEPENDENT}",
    "Machine": "{DW_ABILITY_MACHINE}",
    "Dark matter adept": "{DW_ABILITY_DARK_MATTER_ADEPT}",
    "Badlands pilots": "{DW_ABILITY_BADLANDS_PILOTS}",
}

# Chance to be hit in dark matter for each hull, before and with Dark matter adept.
FUNGUS_ADEPT = {"dw_light": 40, "dw_cruiser": 50, "dw_capital": 60}


def A(kind, dmg, strikes, special=None, name=None):
    return dict(kind=kind, dmg=dmg, strikes=strikes, special=special, name=name)


# ---------------------------------------------------------------------------------------------
# Ships. Columns as in design/unit-stats.md, section 3.
# ---------------------------------------------------------------------------------------------
FACTIONS = {
    "federation": dict(
        title="Federation ships (lawful)", folder="federation", shields="DW_SHIELDS_FEDERATION",
        race="dw_federation", align="lawful",
        ships=[
            dict(id="DW_Danube", name="Danube-class Runabout", image="fed-danube", level=0, cost=10, hp=26, mp=7, xp=20, hull="dw_light",
                 attacks=[A("phaser", 4, 3), A("micro", 6, 1)], desc="Scout, light ship. A runabout from Deep Space Nine, quick enough to grab planets early."),
            dict(id="DW_Miranda", name="Miranda-class", image="fed-miranda", level=1, cost=14, hp=38, mp=5, xp=32, hull="dw_cruiser",
                 attacks=[A("phaser", 4, 3), A("photon", 6, 2)], desc="Cheap line ship. Old, but there are a lot of them."),
            dict(id="DW_Excelsior", name="Excelsior-class", image="fed-excelsior", level=1, cost=20, hp=52, mp=5, xp=40, hull="dw_cruiser",
                 attacks=[A("phaser", 5, 3), A("photon", 8, 2)], desc="Battleship of the line."),
            dict(id="DW_Intrepid", name="Intrepid-class", image="fed-intrepid", level=1, cost=22, hp=44, mp=7, xp=40, hull="dw_cruiser",
                 attacks=[A("phaser", 5, 3), A("photon", 8, 2)], abilities=["Repairs +4"], desc="Fast science cruiser, with engineering teams that repair nearby ships."),
            dict(id="DW_Akira", name="Akira-class", image="fed-akira", level=1, cost=24, hp=52, mp=5, xp=44, hull="dw_cruiser",
                 attacks=[A("phaser", 5, 3), A("photon", 8, 3, "targeting lock")], desc="Torpedo carrier: the strongest Federation torpedo battery."),
            dict(id="DW_Nebula", name="Nebula-class", image="fed-nebula", level=1, cost=26, hp=62, mp=5, xp=48, hull="dw_capital", upkeep=2,
                 attacks=[A("phaser", 7, 3), A("photon", 10, 2)], desc="Heavy cruiser."),
            dict(id="DW_Galaxy", name="Galaxy-class", image="fed-galaxy", level=1, cost=34, hp=68, mp=5, xp=56, hull="dw_capital", upkeep=2,
                 attacks=[A("phaser_array", 7, 4), A("photon", 11, 2)], abilities=["Command", "Repairs +4"], desc="Flagship of the fleet."),
            dict(id="DW_Defiant", name="Defiant-class", image="fed-defiant", level=1, cost=25, hp=44, mp=6, xp=44, hull="dw_light",
                 attacks=[A("pulse_phaser", 9, 3), A("quantum", 12, 1)], abilities=["Evasive", "Cloak"],
                 desc="Glass-cannon escort (leader only). It carries a Romulan cloaking device."),
        ]),
    "klingon": dict(
        title="Klingon ships (chaotic)", folder="klingon", shields="DW_SHIELDS_KLINGON",
        race="dw_klingon", align="chaotic",
        ships=[
            dict(id="DW_Klingon_Freighter", name="Klingon Freighter", image="kl-promellian", level=0, cost=10, hp=32, mp=5, xp=20, hull="dw_cruiser",
                 attacks=[A("disruptor", 5, 3), A("boarding", 6, 2)], abilities=["Glory"], desc="Transport and boarding craft. No torpedoes."),
            dict(id="DW_Raptor", name="Raptor-class Scout", image="kl-raptor", level=1, cost=13, hp=32, mp=8, xp=32, hull="dw_light", shields="DW_SHIELDS_KLINGON_OLD",
                 attacks=[A("disruptor", 5, 3), A("kl_torpedo", 6, 1)], abilities=["Glory"], desc="Scout. The fastest Klingon ship, a 22nd-century design with no cloak and older shields."),
            dict(id="DW_Brel", name="B'rel-class Bird-of-Prey", image="kl-brel", level=1, cost=15, hp=30, mp=7, xp=32, hull="dw_light",
                 attacks=[A("disruptor", 5, 3), A("kl_torpedo", 7, 1)], abilities=["Cloak", "Glory"], desc="Raider and scout that strikes out of cloak."),
            dict(id="DW_D5", name="D5-class Battle Cruiser", image="kl-d5", level=1, cost=16, hp=40, mp=6, xp=36, hull="dw_cruiser", shields="DW_SHIELDS_KLINGON_OLD",
                 attacks=[A("disruptor", 7, 3), A("boarding", 7, 2), A("kl_torpedo", 8, 1)], abilities=["Glory"], desc="Older battlecruiser: cheaper, faster and more fragile than a K't'inga."),
            dict(id="DW_Ktinga", name="K't'inga-class", image="kl-ktinga", level=1, cost=18, hp=42, mp=5, xp=40, hull="dw_cruiser",
                 attacks=[A("disruptor", 6, 3), A("ram", 7, 2), A("kl_torpedo", 8, 2)], abilities=["Glory"], desc="Line battlecruiser."),
            dict(id="DW_Kvort", name="K'Vort-class Bird-of-Prey", image="kl-kvort", level=1, cost=21, hp=44, mp=6, xp=44, hull="dw_cruiser",
                 attacks=[A("disruptor", 7, 3), A("kl_torpedo", 10, 1)], abilities=["Cloak", "Glory"], desc="Heavy raider that strikes out of cloak."),
            dict(id="DW_Vorcha", name="Vor'cha-class", image="kl-vorcha", level=1, cost=25, hp=58, mp=5, xp=48, hull="dw_capital", upkeep=2,
                 attacks=[A("disruptor", 8, 3), A("ram", 10, 2), A("kl_torpedo", 10, 2)], abilities=["Glory"], desc="Attack cruiser."),
            dict(id="DW_Neghvar", name="Negh'Var-class", image="kl-neghvar", level=1, cost=34, hp=72, mp=4, xp=56, hull="dw_capital",
                 attacks=[A("disruptor", 9, 4), A("ram", 12, 2), A("kl_torpedo", 13, 2)], abilities=["Command", "Glory"], desc="Flagship (leader only)."),
        ]),
    "dominion": dict(
        title="Dominion Alliance ships: Cardassians (lawful), Jem'Hadar (chaotic), Breen (neutral)", folder="dominion", shields=None,
        race=None, align=None,
        ships=[
            dict(id="DW_Hideki", name="Hideki-class", image="ca-hideki", level=0, cost=10, hp=30, mp=7, xp=20, hull="dw_light", race="dw_cardassian", align="lawful", shields="DW_SHIELDS_CARDASSIAN",
                 attacks=[A("spiral_disruptor", 5, 3)], desc="Cheap Cardassian patrol ship. No torpedoes."),
            dict(id="DW_Galor", name="Galor-class", image="ca-galor", level=1, cost=15, hp=44, mp=5, xp=36, hull="dw_cruiser", race="dw_cardassian", align="lawful", shields="DW_SHIELDS_CARDASSIAN",
                 attacks=[A("spiral_disruptor", 7, 3, "fleet tactics")], desc="Cardassian line cruiser. No torpedoes, but it fights well in formation."),
            dict(id="DW_Jemhadar_Attack_Ship", name="Jem'Hadar Attack Ship", image="jh-attack", level=1, cost=17, hp=42, mp=6, xp=40, hull="dw_light", race="dw_jemhadar", align="chaotic", shields="DW_SHIELDS_JEMHADAR",
                 attacks=[A("polaron", 8, 3), A("boarding", 6, 3, "transporter"), A("kamikaze", 1, 1, "kamikaze"), A("jh_torpedo", 7, 1)],
                 abilities=["Ketracel-dependent"], desc="Assault ship. Its crew will ram an enemy at full impulse if ordered to."),
            dict(id="DW_Keldon", name="Keldon-class", image="ca-keldon", level=1, cost=21, hp=50, mp=5, xp=44, hull="dw_cruiser", race="dw_cardassian", align="lawful", shields="DW_SHIELDS_CARDASSIAN",
                 attacks=[A("spiral_disruptor", 7, 3, "fleet tactics"), A("ca_torpedo", 8, 2)], desc="Cardassian heavy cruiser, commanded by a Gul."),
            dict(id="DW_Breen_Warship", name="Breen Warship", image="br-warship", level=1, cost=22, hp=58, mp=6, xp=44, hull="dw_cruiser", race="dw_breen", align="neutral", shields="DW_SHIELDS_BREEN",
                 attacks=[A("breen_disruptor", 9, 3), A("dampener", 8, 2, "energy dampener")], abilities=["Dark matter adept"], desc="Disabler. Its energy dampener leaves the target drifting."),
            dict(id="DW_Jemhadar_Battle_Cruiser", name="Jem'Hadar Battle Cruiser", image="jh-cruiser", level=1, cost=28, hp=60, mp=5, xp=52, hull="dw_capital", upkeep=2, race="dw_jemhadar", align="chaotic", shields="DW_SHIELDS_JEMHADAR",
                 attacks=[A("polaron", 7, 4), A("boarding", 7, 3, "transporter"), A("jh_torpedo", 10, 2)],
                 abilities=["Command", "Ketracel supply", "Ketracel-dependent"], desc="Vorta command ship, which keeps the fleet supplied with Ketracel-white."),
            dict(id="DW_Jemhadar_Battleship", name="Jem'Hadar Battleship", image="jh-battleship", level=1, cost=40, hp=88, mp=4, xp=64, hull="dw_capital", race="dw_jemhadar", align="chaotic", shields="DW_SHIELDS_JEMHADAR",
                 attacks=[A("polaron", 10, 4), A("boarding", 8, 3, "transporter"), A("jh_torpedo", 14, 2)],
                 abilities=["Command", "Ketracel supply", "Ketracel-dependent"], desc="Siege flagship (leader only)."),
        ]),
    "maquis": dict(
        title="Maquis ships (neutral)", folder="maquis", shields=None,
        race=None, align="neutral",
        ships=[
            dict(id="DW_Bajoran_Freighter", name="Bajoran Freighter", image="bj-freighter", level=0, cost=14, hp=40, mp=4, xp=20, hull="dw_cruiser", race="dw_bajoran", shields="DW_SHIELDS_BAJORAN",
                 attacks=[A("phaser", 4, 2)], abilities=["Repairs +4", "Dark matter adept"], desc="Supply ship and transport, the Maquis' only field repairs."),
            dict(id="DW_Maquis_Fighter", name="Maquis Fighter", image="mq-fighter", level=1, cost=11, hp=26, mp=8, xp=28, hull="dw_light", race="dw_maquis", shields="DW_SHIELDS_MAQUIS",
                 attacks=[A("phaser", 5, 3), A("plasma", 6, 2), A("micro", 7, 1)], abilities=["Evasive", "Badlands pilots", "Dark matter adept"], desc="Fast fighter (Peregrine-class)."),
            dict(id="DW_Maquis_Raider", name="Maquis Raider", image="mq-raider", level=1, cost=15, hp=30, mp=7, xp=32, hull="dw_light", race="dw_maquis", shields="DW_SHIELDS_MAQUIS",
                 attacks=[A("phaser", 5, 3), A("plasma", 7, 2), A("photon", 8, 1)], abilities=["Evasive", "Nebula cloak", "Badlands pilots", "Dark matter adept"], desc="Ambusher that hides in nebulae and the Badlands."),
            dict(id="DW_Mercenary_Raider", name="Mercenary Raider", image="na-mercenary", level=1, cost=16, hp=38, mp=7, xp=36, hull="dw_light", race="dw_mercenary", shields="DW_SHIELDS_MERCENARY",
                 attacks=[A("merc_disruptor", 7, 3, "fleet tactics")], abilities=["Plunder", "Dark matter adept"], desc="Raider for hire (Baran's ship). No torpedoes."),
            dict(id="DW_Bajoran_Assault_Vessel", name="Bajoran Assault Vessel", image="bj-assault", level=1, cost=17, hp=40, mp=7, xp=36, hull="dw_light", race="dw_bajoran", shields="DW_SHIELDS_BAJORAN",
                 attacks=[A("phaser", 6, 3), A("photon", 8, 2)], abilities=["Evasive", "Dark matter adept"], desc="Heavy fighter."),
            dict(id="DW_Dreadnought", name="Dreadnought", image="mq-dreadnought", level=1, cost=20, hp=48, mp=5, xp=None, hull="dw_cruiser", race="dw_machine", shields="DW_SHIELDS_DREADNOUGHT",
                 attacks=[A("plasma_cannon", 7, 3), A("warhead", 32, 1, "detonate")], abilities=["Machine", "Dark matter adept"], machine=True,
                 desc="Self-guided missile (ATR-4107), a reprogrammed Cardassian weapon. It fights with a plasma cannon until it detonates its warhead."),
            dict(id="DW_Captured_Constellation", name="Captured Constellation", image="cap-constellation", level=1, cost=22, hp=56, mp=5, xp=44, hull="dw_cruiser", race="dw_federation", shields="DW_SHIELDS_FEDERATION",
                 attacks=[A("phaser", 5, 3), A("photon", 8, 2)], abilities=["Repairs +4", "Dark matter adept"], desc="Stolen Federation cruiser (leader only)."),
            dict(id="DW_Stolen_Defiant", name="Stolen Defiant", image="mq-defiant", level=1, cost=25, hp=44, mp=6, xp=44, hull="dw_light", race="dw_federation", shields="DW_SHIELDS_FEDERATION",
                 attacks=[A("pulse_phaser", 9, 3), A("quantum", 12, 1)], abilities=["Evasive", "Cloak", "Dark matter adept"], desc="Glass-cannon escort (leader only), stolen with its cloaking device."),
            dict(id="DW_Ferengi_Marauder", name="Ferengi Marauder", image="mq-marauder", level=1, cost=30, hp=66, mp=5, xp=52, hull="dw_capital", race="dw_ferengi", shields="DW_SHIELDS_FERENGI",
                 attacks=[A("plasma_whip", 10, 3), A("photon", 10, 2)], abilities=["Plunder", "Command", "Dark matter adept"], desc="Mercenary flagship (leader only)."),
        ]),
}

# Terrain keys the crew-level defence bonus touches.
TERRAINS = ["flat", "forest", "hills", "mountains", "village", "castle", "swamp_water", "shallow_water",
            "deep_water", "reef", "sand", "frozen", "cave", "fungus", "unwalkable", "impassable"]


def wml_str(s):
    return s.replace('"', '""')


def attack_id(name):
    return name.replace(" ", "_").replace("-", "_")


def write_attack(out, a):
    k = KINDS[a["kind"]]
    name = a["name"] or NAMES[a["kind"]]
    out.append("    [attack]")
    out.append(f"        name={attack_id(name)}")
    out.append(f"        description= _ \"{name}\"")
    out.append(f"        icon={k['icon']}")
    out.append(f"        type={k['type']}")
    out.append(f"        range={k['range']}")
    out.append(f"        damage={a['dmg']}")
    out.append(f"        number={a['strikes']}")
    if a["special"]:
        out.append("        [specials]")
        out.append(f"            {SPECIALS[a['special']]}")
        out.append("        [/specials]")
    out.append("    [/attack]")


def write_anim(out, a, image):
    k = KINDS[a["kind"]]
    name = attack_id(a["name"] or NAMES[a["kind"]])
    snd = k.get("sound") or ""
    hit = k.get("hit") or ""
    fx = k.get("fx", "")
    anim = k["anim"]
    if anim == "bolt":
        macro = f"{{DW_ANIM_BOLT {name} \"{image}\" \"{fx}\" \"{snd}\"}}" if not hit else \
                f"{{DW_ANIM_BOLT_HIT {name} \"{image}\" \"{fx}\" \"{snd}\" \"{hit}\"}}"
    elif anim == "torpedo":
        macro = f"{{DW_ANIM_TORPEDO {name} \"{image}\" \"{fx}\" \"{snd}\" \"{hit or SND + 'impacts/impact-low-boom.ogg'}\"}}"
    elif anim == "ram":
        macro = f"{{DW_ANIM_RAM {name} \"{image}\" \"{hit}\"}}"
    elif anim == "board":
        macro = f"{{DW_ANIM_BOARD {name} \"{image}\" \"{fx}\" \"{hit}\"}}"
    out.append("    " + macro)


def main_weapon(ship):
    """The attack that gets the Elite crew's extra strike: the first melee beam."""
    for a in ship["attacks"]:
        if KINDS[a["kind"]]["anim"] == "bolt" or a["kind"] in ("plasma", "plasma_cannon"):
            return attack_id(a["name"] or NAMES[a["kind"]])
    return attack_id(ship["attacks"][0]["name"] or NAMES[ship["attacks"][0]["kind"]])


def write_ship(out, fac, ship):
    race = ship.get("race") or fac["race"]
    align = ship.get("align") or fac["align"]
    shields = ship.get("shields") or fac["shields"]
    folder = fac["folder"]
    image = f"units/{folder}/{ship['image']}.png"
    abilities = ship.get("abilities", [])
    out.append("[unit_type]")
    out.append(f"    id={ship['id']}")
    out.append(f"    name= _ \"{wml_str(ship['name'])}\"")
    out.append(f"    race={race}")
    out.append(f"    image=\"{image}\"")
    out.append(f"    level={ship['level']}")
    out.append(f"    cost={ship['cost']}")
    out.append(f"    hitpoints={ship['hp']}")
    out.append(f"    movement={ship['mp']}")
    out.append(f"    movement_type={ship['hull']}")
    out.append(f"    alignment={align}")
    out.append(f"    experience={ship['xp'] if ship['xp'] else 500}")
    out.append("    advances_to=null")
    if ship.get("upkeep"):
        out.append(f"    upkeep={ship['upkeep']}")
    if ship.get("machine"):
        out.append("    ignore_race_traits=yes")
    out.append(f"    description= _ \"{wml_str(ship['desc'])}\"")
    out.append(f"    {{{shields}}}")
    if "Dark matter adept" in abilities:
        out.append(f"    {{DW_DARK_MATTER_ADEPT_TERRAIN {FUNGUS_ADEPT[ship['hull']]}}}")
    if "Badlands pilots" in abilities:
        out.append("    {DW_BADLANDS_PILOTS_TERRAIN}")
    if abilities:
        out.append("    [abilities]")
        for ab in abilities:
            out.append(f"        {ABILITIES[ab]}")
        out.append("    [/abilities]")
    # Melee first, then ranged, as Wesnoth lists them.
    attacks = sorted(ship["attacks"], key=lambda a: KINDS[a["kind"]]["range"] != "melee")
    for a in attacks:
        write_attack(out, a)
    if not ship.get("machine"):
        vet = ship["xp"]
        elite = 2 * vet
        out.append(f"    {{DW_CREW_LEVELS {elite} {150 - elite} {main_weapon(ship)}}}")
    for a in attacks:
        write_anim(out, a, image)
    out.append(f"    {{DW_ANIM_DEATH \"{image}\"}}")
    out.append("[/unit_type]")
    out.append("")


def main():
    for key, fac in FACTIONS.items():
        out = ["#textdomain wesnoth-Dominion_War_Wesnoth", "",
               f"# {fac['title']}.",
               "# Generated by tools/make_units.py from design/unit-stats.md (proposal 2). Edit the tables",
               "# in that script and rerun it, rather than editing this file by hand.", ""]
        for ship in fac["ships"]:
            write_ship(out, fac, ship)
        with open(os.path.join(ROOT, "units", key + ".cfg"), "w", newline="\n") as f:
            f.write("\n".join(out))
        print("wrote units/%s.cfg (%d ships)" % (key, len(fac["ships"])))


if __name__ == "__main__":
    main()
