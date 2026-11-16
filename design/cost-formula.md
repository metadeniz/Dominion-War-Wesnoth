# Ship cost formula

The prices in `unit-stats.md` (proposal 2) were set by hand, ship by ship. This formula is fitted to those prices, so it describes how they were set and gives a rule for pricing new ships or checking changes.

## The formula

**cost = HP ÷ 4 + melee ÷ 5 + ranged × 0.3 + ability gold − 1**, rounded to the nearest gold.

- **HP:** the ship's hit points.
- **Melee:** the best melee attack's damage × strikes. Fleet tactics counts ×1.25 and the energy dampener ×1.4, as in the balance check.
- **Ranged:** the best torpedo's damage × strikes. Ranged damage is worth more than melee, because a ship with no torpedoes can't shoot back.
- **Ability gold:** the same table the balance check (`unit-stats-balance/duel.py`) uses.

| Ability | Gold |
|---|---|
| Repairs +4, Cloak, Command | 3 |
| Ketracel supply | 2 |
| Nebula cloak | 1.5 |
| Sensors, Evasive, Glory, Plunder | 1 |
| Badlands pilots | 0.5 |
| Ketracel-dependent | −1 |

Movement is left out. With it included, the fit gave it almost no weight, because fast ships already pay through their low HP.

Worked example, the Excelsior: 52 ÷ 4 + 15 ÷ 5 + 16 × 0.3 + 0 − 1 = 13 + 3 + 4.8 − 1 = **19.8**, so 20 gold.

## How well the current prices fit

Across the 31 ships it applies to, the formula is on average 1.0 gold off the hand-set prices. The Dreadnought is left out, because its one-shot warhead needs pricing by hand.

These ships are 2 gold or more away from the formula:

| Ship | Price | Formula | Note |
|---|---|---|---|
| Breen warship | 22 | 18.9 | Above the formula. The energy dampener's slow is probably worth more than the ×1.4 here, so 22 is likely fine. |
| Negh'Var (leader) | 34 | 36.0 | Leader-only, so the price only matters in campaigns. |
| Defiant and Stolen Defiant (leaders) | 25 | 23.0 | Leader-only. |

Everything else is within 2 gold. The Bajoran freighter (was 11) and the Maquis raider (was 13) were moved to the formula, 14 and 15 gold (D, 16 Nov).

## Running the check

`python3 design/unit-stats-balance/costformula.py design/unit-stats-balance/units.py` prints every ship's price next to the formula and flags anything 2 or more gold off. It reads `units.py` as data and runs no code from it.
