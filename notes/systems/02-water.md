# 02 — Water

## What Vein does (public sources, verify in-game)
| Behaviour | Source | Verified? |
|---|---|---|
| City water runs until a set day, then stops. Setting: `vein.Calendar.WaterShutoffTimeDays`, default **30** (range 1–999) | Wabbanode, Citadel server guides | [ ] |
| Other configs use 20; players report "about a month" and that water and power go off at different times | HostByte, Steam forum | [ ] |
| Players can't restore the utility station's supply yet (on the roadmap) | Steam forum | [ ] |
| Rooftop/outdoor **barrels** are gravity-fed and must be filled by hand with Large Water Jugs | veingame.net guide | [ ] |
| A **well** connected to the house **fuse box** feeds every connected appliance — no need to plumb each sink | veingame.net guide (community tip) | [ ] |
| Water must be **boiled or filtered** before it's safe | HostHavoc overview | [ ] |
| Fully simulated plumbing/gas grid is a *planned* feature, so the current system is simpler | Official site | — |

## Open questions
- [ ] Is well water dirty, or clean? Does a well need power to pump?
- [ ] Barrel capacity, jug capacity, litres per sink/shower/toilet use.
- [ ] Does rain fill barrels? Do barrels or pipes freeze in winter?
- [ ] When several sources hang off one fuse box, which is used first?
- [ ] Does dirty water from a tap show a warning in the UI?

## Our model (`sim/water.py`, `sim/calendar.py`)
- `Calendar` — shared world clock with `water_shutoff_day` (30) and `power_shutoff_day` (46).
- Sources: `CityMains` (clean, until shutoff), `Well` (unlimited, **dirty**), `Barrel` (only what you pour in; one dirty jug taints it until emptied).
- `FuseBox` — every connected source serves every connected `Fixture`; sources drawn in connection order.
- `Container` — fill at a sink, `boil()` to make safe, pour into a barrel. Quality uses `WaterQuality` from the survival model, so drinking dirty water still adds infection.

## Vein's real settings for this system
From published server configs — see [research/vein-server-settings.md](../../research/vein-server-settings.md) for sources and conflicts.

| Setting | Default | Wired into |
|---|---|---|
| `vein.Calendar.WaterShutoffTimeDays` | 30 ⚠️ (one guide 20) | `Calendar.water_shutoff_day` |

## Sources
- https://wabbanode.com/help/vein/how-to-configure-utility-shutoff-times-on-your-vein-server
- https://citadelservers.com/client/knowledgebase/1002/Citadel-Servers---VEIN-Dedicated-Server-Configuration-Guide..html
- https://www.hostbyte.net/billing/knowledgebase/103/Full-VEIN-Server-Configuration-Guide-Game.ini.html
- https://steamcommunity.com/app/1857950/discussions/0/678482693017741517/
- https://steamcommunity.com/app/1857950/discussions/0/663844725992896290/
- https://veingame.net/vein-guides/here-is-the-plain-text-markdown-version-of-the-guide
- https://hosthavoc.com/blog/vein-game-launch
