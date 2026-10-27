# 07 — Weather, seasons, day/night

## What Vein does (public sources, verify in-game)
| Behaviour | Source | Verified? |
|---|---|---|
| **Dynamic environment where seasons change over time** — listed as a *planned* feature | Official wiki / site | — |
| Weather changes quickly; cold drains energy, heat exhaustion blurs vision | HostHavoc overview | [ ] |
| Solar only works in daytime (day/night cycle exists) | veingame.net guide | [ ] |
| Setting is the Champlain Valley (cold winters, warm summers) | Community wiki hub | [ ] |

Public detail is thin, so **most of this module is our own design** and is marked that way.

## Open questions
- [ ] Are seasons in the current build, and how many days is each?
- [ ] Is there a temperature number anywhere (UI, UE4SS property), or only cold/hot states?
- [ ] Which weather types exist (rain, fog, snow, storms)? Does rain fill barrels (02) or cut solar (03)?
- [ ] Does being indoors or near a fire/heater change body temperature?
- [x] Day length: 65 real minutes at defaults (`vein.Time.*`, see below).

## Our model (`sim/weather.py`)
- `Calendar` (from 02) now also gives `season` — 30 days each, spring → summer → autumn → winter.
- `WeatherSystem.temperature()` = season mean + day/night swing (warmest 15:00) + weather offset; indoors halves the gap to 15 °C; heating holds 20 °C.
- Weather changes hour by hour with seasonal odds; it tends to persist; snow only in winter.
- `solar_factor` — **assumption**, not wired into power yet until confirmed.
- Output temperature plugs straight into `Survivor.tick(temperature=...)` (01).

## Vein's real settings for this system
From published server configs — see [research/vein-server-settings.md](../../research/vein-server-settings.md) for sources and conflicts.

| Setting | Default | Wired into |
|---|---|---|
| `vein.Time.TimeMultiplier` | 16 | `VeinClock.time_multiplier` |
| `vein.Time.NightTimeMultiplier` | 3 | `VeinClock.night_multiplier` |
| `vein.Time.NightTimeMultiplierStart` / `End` | 20 / 6 | `VeinClock.night_start` / `night_end` |

At defaults a full Vein day lasts **65 real minutes**: 06:00–20:00 at 16× (52.5 min) plus night at 48× (12.5 min). `VeinClock.advance_real()` converts wall-clock time to game time exactly across the day/night switch.

## Sources
- https://vein.wiki.gg/wiki/VEIN
- https://hosthavoc.com/blog/vein-game-launch
- https://github.com/wanghuan072/vein-game
