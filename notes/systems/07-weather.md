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
- [ ] Day length in real minutes, and the related `vein.*` time-scale cvar.

## Our model (`sim/weather.py`)
- `Calendar` (from 02) now also gives `season` — 30 days each, spring → summer → autumn → winter.
- `WeatherSystem.temperature()` = season mean + day/night swing (warmest 15:00) + weather offset; indoors halves the gap to 15 °C; heating holds 20 °C.
- Weather changes hour by hour with seasonal odds; it tends to persist; snow only in winter.
- `solar_factor` — **assumption**, not wired into power yet until confirmed.
- Output temperature plugs straight into `Survivor.tick(temperature=...)` (01).

## Sources
- https://vein.wiki.gg/wiki/VEIN
- https://hosthavoc.com/blog/vein-game-launch
- https://github.com/wanghuan072/vein-game
