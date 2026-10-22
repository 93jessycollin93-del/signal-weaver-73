# Vein systems — study order

One system at a time, in this order. Each gets a `notes/systems/NN-name.md` (what Vein does, with sources and open questions) and a clean-room module in `sim/` (our own code and numbers, built only from observed behaviour).

| # | System | Notes | Module | Status |
|---|---|---|---|---|
| 01 | Survival stats: hunger, thirst, fatigue, stamina, temperature, infection | [01-survival-stats.md](01-survival-stats.md) | `sim/survival.py` | prototype |
| 02 | Water: wells, barrels, fuse box distribution, boiling/filtering | [02-water.md](02-water.md) | `sim/water.py`, `sim/calendar.py` | prototype |
| 03 | Power: generators, fuel, solar + batteries, power radius, wiring | [03-power.md](03-power.md) | `sim/power.py` | prototype |
| 04 | Building: materials, utility cabinet repair area, decay | [04-building.md](04-building.md) | `sim/building.py` | prototype |
| 05 | Loot & persistence: scarcity, container respawn, items stay put | [05-loot.md](05-loot.md) | `sim/loot.py` | prototype |
| 06 | Zombies: sight, hearing, smell, infection per hit | [06-zombies.md](06-zombies.md) | `sim/zombies.py` | prototype |
| 07 | Weather, seasons, day/night, temperature | [07-weather.md](07-weather.md) | `sim/weather.py` | prototype (mostly our design) |
| 08 | Vehicles | | | todo |
| 09 | Save format (`.vns`) | | | needs a save file |

## Clean-room rule
Notes may describe *behaviour* (what happens in-game). Modules in `sim/` are written from those notes only — never from decompiled code, and never using Vein's assets, names or exact data tables.
