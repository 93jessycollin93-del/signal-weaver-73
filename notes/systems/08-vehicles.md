# 08 — Vehicles

## What Vein does (public sources, verify in-game)
| Behaviour | Source | Verified? |
|---|---|---|
| A car that won't start has one of: **dead/missing battery**, **empty tank**, or **low engine condition / missing spark plugs** | veingame.net car guide | [ ] |
| **Car Battery Chargers** are found in auto shops | veingame.net car guide | [ ] |
| Fuel is best **siphoned** from abandoned cars — needs a container and a **siphon hose** | veingame.net car guide | [ ] |
| You can **hotwire** cars (guide title: hotwire, charge battery, repair engines) | veingame.net car guide | [ ] |
| Repair = remove damaged parts under the hood and swap in good ones; some parts need a higher **Mechanic** level | Steam forum: Fuel and Vehicles | [ ] |
| Refuel, maintain and upgrade parts — listed as *planned* | Official wiki / site | — |

## Open questions
- [ ] Full list of part slots (tyres, radiator, alternator, doors, windows?).
- [ ] Does hotwiring need a skill level or a tool, and can it fail?
- [ ] Fuel use per km and tank size; does fuel go stale over time?
- [ ] Does the battery recharge while driving?
- [ ] Mechanic level needed per part; how mechanic XP is earned.
- [ ] Do engine noise and headlights attract zombies (link to 06)?

## Our model (`sim/vehicles.py`)
- `Car.why_wont_it_start()` lists every problem: missing/damaged battery, plugs or engine; flat battery; no fuel; no key and not hotwired.
- Every start attempt drains the battery a little, so cranking a broken car can flatten it.
- `hotwire()` needs a mechanic level; `siphon()` needs a siphon hose; `FuelCan` moves fuel between cars.
- `remove_part` / `install_part` check the part's mechanic level.
- Driving burns fuel, wears the engine, and recharges the battery (alternator — our assumption).
- `charge_battery()` only works when the charger has power (link to 03).

## Sources
- https://veingame.net/vein-guides/vein-vehicle-guide-repair-hotwire-maintain
- https://steamcommunity.com/app/1857950/discussions/0/4407417621393729311/
- https://vein.wiki.gg/wiki/VEIN
