# 03 — Power

## What Vein does (public sources, verify in-game)
| Behaviour | Source | Verified? |
|---|---|---|
| City power runs until a set day. Setting: `vein.Calendar.ElectricalShutoffTimeDays`, default **46** (range 1–999) | Wabbanode, Citadel server guides | [ ] |
| Players report power sometimes cutting earlier (week 3) and separately from water | Steam forum | [ ] |
| **Generators** (gas or diesel) are the main source | veingame.net guide | [ ] |
| Anything inside a generator's **power radius** works without extra wiring (e.g. street lights) | veingame.net guide | [ ] |
| **Solar** only works in daytime and needs **batteries**; a Makeshift Battery holds **50,000 Wh** | veingame.net guide | [ ] |
| Power hookup range is a server setting; players recommend raising it to 10000 | Steam forum | [ ] |
| A windmill reportedly wouldn't run a mine elevator that worked on a generator | Steam forum | [ ] |
| Fully simulated electrical grid is a *planned* feature | Official site | — |

## Open questions
- [ ] Generator wattage, tank size, burn rate (litres per hour, and does it depend on load?).
- [ ] Exact power radius in metres, and the hookup-range setting's name/unit.
- [ ] Device wattages (fridge, lights, heater, freezer, well pump, electric stove).
- [ ] What happens when demand exceeds supply — everything off, or some devices stay on?
- [ ] Does solar output change with weather or season?
- [ ] Does the city grid charge batteries before shutoff?

## Our model (`sim/power.py`)
- `Generator` — wattage, fuel tank, litres per kWh, radius; stops when dry.
- `SolarPanel` — output only during daytime (06:00–20:00, from `Calendar`).
- `Battery` — 50,000 Wh default; stores spare solar, tops up from the city grid.
- `PowerNetwork` — devices are on the network if wired, or inside a running generator's radius. Supply order: solar → city → batteries → generator fuel. When power is short, devices with higher `priority` are served first.

## Vein's real settings for this system
From published server configs — see [research/vein-server-settings.md](../../research/vein-server-settings.md) for sources and conflicts.

| Setting | Default | Wired into |
|---|---|---|
| `vein.Calendar.ElectricalShutoffTimeDays` | 46 ⚠️ (one guide 30) | `Calendar.power_shutoff_day` |

No public cvar name was found for the power hookup range.

## Sources
- https://wabbanode.com/help/vein/how-to-configure-utility-shutoff-times-on-your-vein-server
- https://citadelservers.com/client/knowledgebase/1002/Citadel-Servers---VEIN-Dedicated-Server-Configuration-Guide..html
- https://veingame.net/vein-guides/here-is-the-plain-text-markdown-version-of-the-guide
- https://veingame.net/vein-guides/vein-game-how-to-power-street-light
- https://steamcommunity.com/app/1857950/discussions/0/689741058327727785/
- https://steamcommunity.com/app/1857950/discussions/0/678482693017741517/
